import os
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uuid
from supabase import create_client, Client 
from sentence_transformers import SentenceTransformer
from keybert import KeyBERT
from sklearn.metrics.pairwise import cosine_similarity

#Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ibecmvmtlndaonohzxce.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImliZWNtdm10bG5kYW9ub2h6eGNlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzc4MTA4NzQsImV4cCI6MjA1MzM4Njg3NH0.XBLqtGUJ3bPjrDgM6ZifZoJGOponRjfhd9YzFJ6yrL0")
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Conexión con Supabase establecida.")
except Exception as e:
    print(f"❌ Error fatal al conectar con Supabase: {e}")
    # En un caso real, el programa debería terminar si no hay DB.
    exit()


# Carga modelos IA
MODELO_SBERT = "paraphrase-multilingual-mpnet-base-v2" 
print(f"🧠 Cargando modelo de embeddings: '{MODELO_SBERT}'...")
embedding_model = SentenceTransformer(MODELO_SBERT)
print("🧠 Cargando modelo de keywords (KeyBERT)...")
kw_model = KeyBERT(model=embedding_model)
print("✅ Modelos de IA listos.")


# Pydantic
# Definen la estructura de las peticiones y respuestas de la API

class TicketProcessRequest(BaseModel):
    # El frontend solo necesita enviar el ID del ticket que se acaba de crear, creo
    ticket_id: uuid.UUID = Field(..., description="El ID único del ticket a procesar.")

class TicketProcessResponse(BaseModel):
    status: str
    ticket_id: uuid.UUID
    solucion_sugerida: str
    keywords_extraidas: list[str]


# Lógica Agente Experto 

async def encontrar_solucion_semantica(descripcion_usuario: str) -> str:
    """
    Busca en la tabla `knowledge_base` la solución más relevante usando similitud de embeddings.
    Esta función es el nuevo "cerebro" del agente.
    """
    print("🔎 Buscando solución en la base de conocimientos...")
    # 1. Obtener la base de conocimientos de Supabase
    # Tener una tabla `knowledge_base` con `problema_resumen`, `solucion` y `embedding`
    try:
        response = supabase.table('knowledge_base').select('solucion, embedding').execute()
        knowledge_data = response.data
        if not knowledge_data:
            print("⚠️ Advertencia: La base de conocimientos está vacía.")
            return "Hemos recibido tu ticket. Un agente humano lo revisará pronto."
    except Exception as e:
        print(f"❌ Error al consultar la base de conocimientos: {e}")
        return "No pudimos consultar las soluciones existentes. Tu ticket ha sido registrado para revisión manual."

    # Extraer embeddings y soluciones
    known_embeddings = np.array([item['embedding'] for item in knowledge_data])
    soluciones = [item['solucion'] for item in knowledge_data]

    # Convertir la descripción del usuario en un embedding
    user_embedding = embedding_model.encode([descripcion_usuario])

    # Calcular la similitud del coseno entre el problema del usuario y todos los problemas conocidos
    similarities = cosine_similarity(user_embedding, known_embeddings)

    # Encontrar la mejor coincidencia
    best_match_index = np.argmax(similarities)
    max_similarity = similarities[0][best_match_index]
    print(f"📊 Similitud máxima encontrada: {max_similarity:.2f}")

    #  Decidir si la similitud es suficiente para dar una respuesta
    UMBRAL_CONFIANZA = 0.70  # Se puede ajustar 
    if max_similarity >= UMBRAL_CONFIANZA:
        print(f"✅ Coincidencia encontrada con confianza. Devolviendo solución.")
        return soluciones[best_match_index]
    else:
        print(f"🤔 La similitud está por debajo del umbral. Devolviendo respuesta por defecto.")
        return "Hemos recibido tu ticket. Un agente humano lo revisará pronto."


# Endpoint con FastAPI 

app = FastAPI(
    title="API del Agente Experto para Help Desk",
    description="Procesa un ticket, lo enriquece con IA y busca una solución automática.",
    version="1.0.0"
)

@app.post("/procesar-ticket", response_model=TicketProcessResponse)
async def procesar_ticket_endpoint(request: TicketProcessRequest):
    """
    Endpoint principal para procesar un ticket.
    """
    ticket_id = request.ticket_id
    print(f"\n--- 📩 Procesando nuevo ticket ID: {ticket_id} ---")

    # Obtener la descripción del ticket de la BD
    try:
        response = supabase.table('tickets').select('descripcion').eq('id', str(ticket_id)).single().execute() #toma de la tabla ticmkets la descripcion donde el id sea igual al id que tiene ticket_id y que solo debe regresar uno, ya que se supone no debe haber duplicidad, despues lo ejecutamos
        descripcion = response.data.get('descripcion')
        if not descripcion:
            raise HTTPException(status_code=404, detail=f"Ticket con ID {ticket_id} no encontrado o sin descripción.")
    except Exception as e:
        print(f"❌ Error al obtener el ticket: {e}")
        raise HTTPException(status_code=500, detail=f"Error de base de datos al buscar el ticket: {e}")

    # Extraer palabras clave con KeyBERT
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

    # Encontrar la solución usando el nuevo agente semántico
    solucion_sugerida = await encontrar_solucion_semantica(descripcion)

    # Actualizar el ticket original en la BD con los resultados
    print("💾 Actualizando el ticket en la base de datos...")
    try:
        supabase.table('tickets').update({
            'solucion_sugerida': solucion_sugerida,
            'keywords_detectadas': keywords_extraidas, 
            'estado': 'analizado_por_ia' 
        }).eq('id', str(ticket_id)).execute()
    except Exception as e:
        # Resgistro de la falla, si es que la hay
        print(f"⚠️ Error al actualizar el ticket {ticket_id}: {e}")
        # No lanzamos una excepción HTTP para que el usuario igual reciba la respuesta.

    # Devolver una respuesta completa al frontend
    return TicketProcessResponse(
        status="Procesado exitosamente",
        ticket_id=ticket_id,
        solucion_sugerida=solucion_sugerida,
        keywords_extraidas=keywords_extraidas
    )

@app.get("/")
async def root():
    return {"message": "Servidor del Agente Experto está en línea y listo para recibir tickets."}