import os
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uuid
from supabase import create_client, Client
from sentence_transformers import SentenceTransformer
from keybert import KeyBERT
from sklearn.metrics.pairwise import cosine_similarity
# from register import app as Register
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

MODELO_SBERT = "paraphrase-multilingual-mpnet-base-v2"
print(f"🧠 Cargando modelo de embeddings: '{MODELO_SBERT}'...")
embedding_model = SentenceTransformer(MODELO_SBERT)
print("🧠 Cargando modelo de keywords (KeyBERT)...")
kw_model = KeyBERT(model=embedding_model)
print("✅ Modelos de IA listos.")


# IA 
async def encontrar_solucion_semantica(descripcion_usuario: str) -> str:
    print("🔎 Buscando solución en la base de conocimientos...")
    try:
        response = supabase.table('knowledge_base').select('solucion, embedding').execute()
        knowledge_data = response.data
        if not knowledge_data:
            return "Hemos recibido tu ticket. Un agente humano lo revisará pronto."
    except Exception as e:
        print(f"❌ Error al consultar la base de conocimientos: {e}")
        return "No pudimos consultar las soluciones existentes."

    # Convierte el string del embedding de la DB a una lista de Python si es necesario
    known_embeddings = np.array([ast.literal_eval(item['embedding']) if isinstance(item['embedding'], str) else item['embedding'] for item in knowledge_data])
    soluciones = [item['solucion'] for item in knowledge_data]
    user_embedding = embedding_model.encode([descripcion_usuario])
    similarities = cosine_similarity(user_embedding, known_embeddings)
    best_match_index = np.argmax(similarities)
    max_similarity = similarities[0][best_match_index]
    print(f"📊 Similitud máxima encontrada: {max_similarity:.2f}")

    if max_similarity >= 0.70:
        return soluciones[best_match_index]
    else:
        return "Hemos recibido tu ticket. Un agente humano lo revisará pronto."


# MODELOS PYDANTIC 
class TicketSimpleRequest(BaseModel):
    usuario_id: uuid.UUID
    descripcion: str

# Modelo de respuesta para el ticket procesado (sin cambios)
class TicketCompletoResponse(BaseModel):
    status: str
    ticket_id: str
    solucion_sugerida: str
    keywords_extraidas: list[str]

# Modelo para cuando un agente resuelve un ticket (sin cambios)
class TicketResueltoRequest(BaseModel):
    ticket_id: uuid.UUID
    solucion_final: str = Field(..., description="La solución correcta escrita por el agente humano.")

# Modelos para el endpoint de validación de usuario (sin cambios)
class UserRequest(BaseModel):
    email: str
    nombre: str
    rol: str

class UserResponse(BaseModel):
    id: str
    email: str
    nombre: str
    rol: str


# FASTAPI 
app = FastAPI(
    title="API Unificada de Help Desk con IA",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Para desarrollo. En producción, cámbialo a la URL de tu front-end.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Servidor del Agente Experto está en línea."}


# --- ENDPOINT UNIFICADO ---
@app.post("/registrar-o-validar-usuario", response_model=UserResponse)
async def registrar_o_validar_usuario(request: UserRequest):
    # ...
    try:
        user_response = supabase.table('usuarios').select('*').eq('email', request.email).single().execute()
        print(f"Usuario existente encontrado.")
        return UserResponse(**user_response.data)

    except Exception as e:
        print(f"Usuario nuevo. Creando registro...")
        new_user_data = request.model_dump()
        # --- LÍNEA CORREGIDA ---
        insert_response = supabase.table('usuarios').insert(new_user_data).execute()
        
        if insert_response.data:
            return UserResponse(**insert_response.data)
        else:
            raise HTTPException(status_code=500, detail="No se pudo registrar al nuevo usuario.")

@app.post("/crear-y-procesar-ticket", response_model=TicketCompletoResponse)
async def crear_y_procesar_ticket(request: TicketSimpleRequest): # Usa el nuevo modelo
    """
    Este endpoint ahora solo necesita el ID del usuario y la descripción
    porque el usuario ya fue validado en el paso anterior.
    """
    print(f"\n--- 📩 Creando y procesando ticket para el usuario ID: {request.usuario_id} ---")
    try:
        # PASO 1: YA NO ES NECESARIO BUSCAR AL USUARIO. ¡LO HEMOS SIMPLIFICADO!
        
        # PASO 2: CREAR EL TICKET Y ENLAZARLO
        ticket_data = {
            'descripcion': request.descripcion,
            'usuario_id': str(request.usuario_id) # Usamos el ID directamente
        }
        insert_ticket_response = supabase.table('tickets').insert(ticket_data).execute()
        ticket_id = insert_ticket_response.data[0]['id']
        print(f"🎫 Ticket nuevo creado con ID: {ticket_id}")

        # PASO 3: EJECUTAR EL ANÁLISIS DE IA (sin cambios)
        print(f"🧠 Ejecutando análisis de IA...")
        solucion_sugerida = await encontrar_solucion_semantica(request.descripcion)
        keywords_obj = kw_model.extract_keywords(request.descripcion, keyphrase_ngram_range=(1, 2), stop_words='spanish', use_mmr=True, diversity=0.7, top_n=5)
        keywords_extraidas = [kw[0] for kw in keywords_obj]
        
        # PASO 4: ACTUALIZAR EL TICKET CON LOS RESULTADOS (sin cambios)
        supabase.table('tickets').update({
            'solucion_sugerida': solucion_sugerida,
            'keywords_detectadas': keywords_extraidas,
            'estado': 'analizado_por_ia'
        }).eq('id', str(ticket_id)).execute()
        
        # PASO 5: DEVOLVER LA RESPUESTA FINAL (sin cambios)
        return TicketCompletoResponse(
            status="Ticket procesado exitosamente",
            ticket_id=ticket_id,
            solucion_sugerida=solucion_sugerida,
            keywords_extraidas=keywords_extraidas
        )
    except Exception as e:
        print(f"❌ Error en el flujo: {e}")
        raise HTTPException(status_code=500, detail=f"Ocurrió un error en el servidor: {e}")

# En tu archivo de FastAPI, debajo de tu otro endpoint

@app.post("/resolver-y-entrenar")
async def resolver_y_entrenar(request: TicketResueltoRequest):
    """
    Endpoint para que un agente humano marque un ticket como resuelto
    y, crucialmente, entrene la base de conocimientos con la nueva solución.
    """
    print(f"\n--- 🎓 Entrenando el sistema con el ticket ID: {request.ticket_id} ---")
    try:
        # --- PASO A: OBTENER LA DESCRIPCIÓN ORIGINAL DEL PROBLEMA ---
        ticket_response = supabase.table('tickets').select('descripcion').eq('id', str(request.ticket_id)).single().execute()
        if not ticket_response.data:
            raise HTTPException(status_code=404, detail="El ticket a entrenar no fue encontrado.")
        
        descripcion_original = ticket_response.data['descripcion']

        # --- PASO B: ACTUALIZAR EL TICKET A "RESUELTO" ---
        supabase.table('tickets').update({
            'solucion_final': request.solucion_final,
            'estado': 'resuelto_por_humano'
        }).eq('id', str(request.ticket_id)).execute()
        print("✅ Ticket marcado como resuelto.")

        # --- PASO C: "ALIMENTAR" LA BASE DE CONOCIMIENTOS ---
        # 1. Generar el embedding para la descripción original del problema
        print("🧠 Generando embedding para el nuevo conocimiento...")
        nuevo_embedding = embedding_model.encode([descripcion_original]).tolist()[0]

        # 2. Preparar el nuevo registro de conocimiento
        nuevo_conocimiento = {
            'embedding': str(nuevo_embedding), # Guardarlo como string es más robusto
            'solucion': request.solucion_final # La solución correcta del humano
        }

        # 3. Insertar el nuevo conocimiento en la base
        supabase.table('knowledge_base').insert(nuevo_conocimiento).execute()
        print("✅ ¡Base de conocimientos actualizada con la nueva solución!")

        return {"status": "success", "message": "El ticket fue resuelto y la base de conocimientos ha sido entrenada."}

    except Exception as e:
        print(f"❌ Error durante el entrenamiento: {e}")
        raise HTTPException(status_code=500, detail=f"Ocurrió un error: {e}")
