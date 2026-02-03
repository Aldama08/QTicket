import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uuid
from supabase import create_client, Client
from sentence_transformers import SentenceTransformer
from keybert import KeyBERT
# from register import app as Register
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()



SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    # print("Conexión con Supabase establecida.")
except Exception as e:
    # print(f"❌ Error fatal al conectar con Supabase: {e}")
    exit()

MODELO_SBERT = "paraphrase-multilingual-mpnet-base-v2"
# print(f"Cargando modelo: '{MODELO_SBERT}'...")
embedding_model = SentenceTransformer(MODELO_SBERT)
# print("Cargando modelo de keywords (KeyBERT)...")
kw_model = KeyBERT(model=embedding_model)
# print("Modelos de IA listos.")


# IA 
async def encontrar_solucion_semantica(descripcion_usuario: str) -> str:
    # print("Buscando solución inteligente en la DB...")
    try:
        user_embedding = embedding_model.encode(descripcion_usuario).tolist()

        rpc_response = supabase.rpc('buscar_soluciones', {
            'query_embedding': user_embedding,
            'match_threshold': 0.70, # Eespuestas 70% de similitud 
            'match_count': 1         # Solo tráeme la mejor
        }).execute()

        if rpc_response.data:
            mejor_match = rpc_response.data[0]
            # print(f"✅ Solución encontrada con {mejor_match['similarity']:.2f} de similitud.")
            return mejor_match['solucion']
        
        return "Hemos recibido tu ticket. Un agente humano lo revisará pronto. ¡Gracias!"

    except Exception as e:
        return "Error técnico al buscar soluciones."


# MODELOS PYDANTIC 
class TicketSimpleRequest(BaseModel):
    usuario_id: str
    descripcion: str

# Modelo de respuesta para el ticket procesado (sin cambios)
class TicketCompletoResponse(BaseModel):
    status: str
    ticket_id: str
    solucion_sugerida: str
    keywords_extraidas: list[str]

# Modelo para cuando un agente resuelve un ticket (sin cambios)
class TicketResueltoRequest(BaseModel):
    ticket_id: str
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
    title="API Help Desk IA",
    version="2.2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], #En producción, cámbialo a la URL de tu front-end.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "El Agente está en línea."}


def sentEmail(nombre, descripcion):
    remitente = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASSWORD")
    destinatario = os.getenv("EMAIL_DESTINATARIO")
    
    msg = MIMEMultipart()
    msg['From'] = remitente
    msg['To'] = destinatario
    msg['Subject'] = f"Nuevo Ticket: {nombre}"
    
    cuerpo = f"""
    Se ha registrado un nuevo ticket en el sistema:
    Usuario: {nombre}
    Descripción: {descripcion}
    
    Hay que atenderlo pronto.  
    
    """
    msg.attach(MIMEText(cuerpo,'plain'))
    try:
        # Configuración del servidor con Gmail
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(remitente, password)
        server.send_message(msg)
        server.quit()
        print("Correo de notificación enviado con éxito.")
    except Exception as e:
        print(f"Error al enviar el correo: {e}") 
    


@app.post("/registrar-o-validar-usuario", response_model=UserResponse)
async def registrar_o_validar_usuario(request: UserRequest):
    try:
        # Intenta buscar al usuario
        user_response = supabase.table('usuarios').select('*').eq('email', request.email).execute()
        
        # Si existe (la lista no está vacía)
        if user_response.data:
            print(f"Usuario existente encontrado.")
            return UserResponse(**user_response.data[0]) # <--- Agregar [0]

    except Exception as e:
        print(f"Error al buscar usuario: {e}")

    # Si no existe, crear uno nuevo
    print(f"Usuario nuevo o no encontrado. Creando registro...")
    new_user_data = request.model_dump()
    try:
        insert_response = supabase.table('usuarios').insert(new_user_data).execute()
        
        if insert_response.data:
            # Supabase insert devuelve una lista, tomamos el primer elemento
            return UserResponse(**insert_response.data[0]) # <--- Agregar [0]
        else:
            raise HTTPException(status_code=500, detail="No se pudo registrar al nuevo usuario.")
    except Exception as e:
        print(f"Error en inserción: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/crear-y-procesar-ticket", response_model=TicketCompletoResponse)
async def crear_y_procesar_ticket(request: TicketSimpleRequest): 
    """
    Un endpoint para crear y procesar tickets. Daaah
    """
    try:
        
        # PASO 1: CREAR EL TICKET Y ENLAZARLO
        ticket_data = {
            'descripcion': request.descripcion,
            'usuario_id': (request.usuario_id) # Usamos el ID directamente
        }
        insert_ticket_response = supabase.table('tickets').insert(ticket_data).execute()
        ticket_id = insert_ticket_response.data[0]['id']
        print(f"Ticket nuevo creado con ID: {ticket_id}")

        sentEmail(request.usuario_id, request.descripcion)
        
        # PASO 2: EJECUTAR EL ANÁLISIS DE IA
        print( "Ejecutando análisis...")
        solucion_sugerida = await encontrar_solucion_semantica(request.descripcion)
        keywords_obj = kw_model.extract_keywords(request.descripcion, keyphrase_ngram_range=(1, 2), stop_words='spanish', use_mmr=True, diversity=0.7, top_n=5)
        keywords_extraidas = [kw[0] for kw in keywords_obj]
        
        # PASO 4: ACTUALIZAR EL TICKET CON LOS RESULTADOS
        supabase.table('tickets').update({
            'solucion_sugerida': solucion_sugerida,
            'keywords_detectadas': keywords_extraidas,
            'estado': 'analizado_por_ia'
        }).eq('id', str(ticket_id)).execute()
        
        # PASO 5: DEVOLVER LA RESPUESTA
        return TicketCompletoResponse(
            status="Ticket procesado exitosamente",
            ticket_id=ticket_id,
            solucion_sugerida=solucion_sugerida,
            keywords_extraidas=keywords_extraidas
        )
    except Exception as e:
        print(f"Error en el flujo: {e}")
        raise HTTPException(status_code=500, detail=f"Ocurrió un error en el servidor: {e}")


#Generado por AI
@app.post("/resolver-y-entrenar")
async def resolver_y_entrenar(request: TicketResueltoRequest):
    try:
        # A. Obtener lo que el usuario escribió originalmente
        ticket = supabase.table('tickets').select('descripcion').eq('id', request.ticket_id).single().execute()
        descripcion_del_usuario = ticket.data['descripcion']

        # B. Generar el embedding AUTOMÁTICAMENTE
        # Aquí es donde ocurre la automatización: Python lo calcula en el momento
        vector_nuevo = embedding_model.encode(descripcion_del_usuario).tolist()

        # C. Guardar en la base de conocimientos
        supabase.table('knowledge_base').insert({
            'solucion': request.solucion_final, # Lo que escribió el agente
            'embedding': vector_nuevo           # El vector calculado automáticamente
        }).execute()

        return {"message": "Conocimiento guardado y sistema entrenado automáticamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))