import os
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uuid
from supabase import create_client, Client 
from sentence_transformers import SentenceTransformer
from keybert import KeyBERT
from sklearn.metrics.pairwise import cosine_similarity
from register import app as Register
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import ast

# Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ibecmvmtlndaonohzxce.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImliZWNtdm10bG5kYW9ub2h6eGNlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzc4MTA4NzQsImV4cCI6MjA1MzM4Njg3NH0.XBLqtGUJ3bPjrDgM6ZifZoJGOponRjfhd9YzFJ6yrL0")
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Conexión con Supabase establecida.")
except Exception as e:
    print(f"❌ Error fatal al conectar con Supabase: {e}")
    exit()

# Carga modelos IA
MODELO_SBERT = "paraphrase-multilingual-mpnet-base-v2" 
print(f"🧠 Cargando modelo de embeddings: '{MODELO_SBERT}'...")
embedding_model = SentenceTransformer(MODELO_SBERT)
print("🧠 Cargando modelo de keywords (KeyBERT)...")
kw_model = KeyBERT(model=embedding_model)
print("✅ Modelos de IA listos.")

# Pydantic Models
class TicketProcessRequest(BaseModel):
    ticket_id: uuid.UUID = Field(..., description="El ID único del ticket a procesar.")

class TicketProcessResponse(BaseModel):
    status: str
    ticket_id: uuid.UUID
    solucion_sugerida: str
    keywords_extraidas: list[str]

# Lógica del Agente Experto 
async def encontrar_solucion_semantica(descripcion_usuario: str) -> str:
    print("🔎 Buscando solución en la base de conocimientos...")
    try:
        response = supabase.table('knowledge_base').select('solucion, embedding').execute()
        knowledge_data = response.data
        if not knowledge_data:
            print("⚠️ Advertencia: La base de conocimientos está vacía.")
            return "Hemos recibido tu ticket. Un agente humano lo revisará pronto."
    except Exception as e:
        print(f"❌ Error al consultar la base de conocimientos: {e}")
        return "No pudimos consultar las soluciones existentes. Tu ticket ha sido registrado para revisión manual."

    known_embeddings = np.array([ast.literal_eval(item['embedding']) for item in knowledge_data])
    soluciones = [item['solucion'] for item in knowledge_data]
    user_embedding = embedding_model.encode([descripcion_usuario])
    similarities = cosine_similarity(user_embedding, known_embeddings)
    best_match_index = np.argmax(similarities)
    max_similarity = similarities[0][best_match_index]
    print(f"📊 Similitud máxima encontrada: {max_similarity:.2f}")

    UMBRAL_CONFIANZA = 0.70  # Se puede ajustar 
    if max_similarity >= UMBRAL_CONFIANZA:
        print(f"✅ Coincidencia encontrada con confianza. Devolviendo solución.")
        return soluciones[best_match_index]
    else:
        print(f"🤔 La similitud está por debajo del umbral. Devolviendo respuesta por defecto.")
        return "Hemos recibido tu ticket. Un agente humano lo revisará pronto."

async def transferir_conocimiento_a_db(descripcion: str, solucion: str):
    """
    Función reutilizable para transferir la descripción y solución a la base de conocimiento.
    """
    try:
        print(f"📊 Generando embedding para el conocimiento...")
        problema_embedding = embedding_model.encode([descripcion]).tolist()[0]
        
        new_knowledge = {
            'solucion': solucion,
            'embedding': problema_embedding
        }
        
        supabase.table('knowledge_base').insert(new_knowledge).execute()
        print(f"✅ Conocimiento guardado exitosamente en `knowledge_base`.")
    except Exception as e:
        print(f"❌ Error al guardar el conocimiento: {e}")
        raise HTTPException(status_code=500, detail=f"Error al guardar el conocimiento: {e}")

# Endpoint con FastAPI 
app = FastAPI(
    title="API del Agente Experto para Help Desk",
    description="Procesa un ticket, lo enriquece con IA y busca una solución automática.",
    version="1.0.0"
)

app.mount("/Register", Register)

@app.post("/procesar-ticket", response_model=TicketProcessResponse)
async def procesar_ticket_endpoint(request: TicketProcessRequest):
    """
    Endpoint principal para procesar un ticket.
    """
    ticket_id = request.ticket_id
    print(f"\n--- 📩 Procesando nuevo ticket ID: {ticket_id} ---")

    try:
        response = supabase.table('tickets').select('descripcion').eq('id', str(ticket_id)).single().execute()
        descripcion = response.data.get('descripcion')
        if not descripcion:
            raise HTTPException(status_code=404, detail=f"Ticket con ID {ticket_id} no encontrado o sin descripción.")
    except Exception as e:
        print(f"❌ Error al obtener el ticket: {e}")
        raise HTTPException(status_code=500, detail=f"Error de base de datos al buscar el ticket: {e}")

    print(" Generando embedding del ticket...")
    ticket_embedding = embedding_model.encode([descripcion]).tolist()[0]
    print("Embedding generado.")
    print(f"Embedding del ticket: {ticket_embedding}")

    print("🔑 Extrayendo palabras clave...")
    keywords = kw_model.extract_keywords(
        descripcion,
        keyphrase_ngram_range=(1, 2),
        stop_words='spanish', 
        use_mmr=True,
        diversity=0.7,
        top_n=5
    )
    keywords_extraidas = [kw[0] for kw in keywords]
    print(f"🔍 Palabras clave detectadas: {keywords_extraidas}")

    solucion_sugerida = await encontrar_solucion_semantica(descripcion)

    print("💾 Actualizando el ticket en la base de datos...")
    try:
        supabase.table('tickets').update({
            'solucion_sugerida': solucion_sugerida,
            'keywords_detectadas': keywords_extraidas, 
            'estado': 'analizado_por_ia'
        }).eq('id', str(ticket_id)).execute()
    except Exception as e:
        print(f"⚠️ Error al actualizar el ticket {ticket_id}: {e}")

    # Nuevo paso: Llenar la tabla knowledge_base automáticamente
    # Solo guarda en la base de conocimiento si la solución no es la genérica
    if solucion_sugerida != "Hemos recibido tu ticket. Un agente humano lo revisará pronto.":
      await transferir_conocimiento_a_db(descripcion, solucion_sugerida)
      print("✅ El conocimiento del ticket fue transferido a la base de datos automáticamente.")

    return TicketProcessResponse(
        status="Procesado exitosamente",
        ticket_id=ticket_id,
        solucion_sugerida=solucion_sugerida,
        keywords_extraidas=keywords_extraidas
    )

@app.get("/")
async def root():
    return {"message": "Servidor del Agente Experto está en línea y listo para recibir tickets."}


@app.post("/insertar-conocimiento-inicial")
async def insertar_conocimiento_inicial():
    """
    Endpoint temporal para insertar el primer registro de conocimiento de forma segura.
    """
    descripcion = "Mi computadora no enciende y no hace ningún ruido."
    solucion = "Revisar los cables de alimentación y la fuente de poder."
    
    try:
        embedding = embedding_model.encode([descripcion]).tolist()[0]
        supabase.table('knowledge_base').insert({
            'solucion': solucion,
            'embedding': embedding
        }).execute()
        return {"status": "success", "message": "El conocimiento inicial se insertó correctamente."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al insertar el conocimiento: {e}")



origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://192.168.1.64",
    "http://192.168.1.64:3000",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)