import os
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid
from supabase import create_client, Client 

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ibecmvmtlndaonohzxce.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImliZWNtdm10bG5kYW9ub2h6eGNlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzc4MTA4NzQsImV4cCI6MjA1MzM4Njg3NH0.XBLqtGUJ3bPjrDgM6ZifZoJGOponRjfhd9YzFJ6yrL0")

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Conexión establecida.")
except Exception as e:
    print(f"❌ Error al conectar: {e}")
    exit()

class createPerson(BaseModel):
    email: str
    nombre: str
    rol: str


class personResponse(BaseModel):
    id: uuid.UUID
    email: str
    nombre: str
    rol: str

#Intacia 
app = FastAPI(
    title = "API para la toma de datos del usuario",
    description = "Procesa los datos de los usuarios que requieren un Ticket",
    version="0.0.1"
)

    
@app.post("/procesar-datos", response_model=personResponse) #Como la funcion la devuelve
async def procesar_datos_endpoint(request: createPerson): #Como el cliente debe poner
    """
    Endpoint principal para procesar datos de los usuarios
    """
    new_data = request.model_dump()

    try:
        response = supabase.table('usuarios').insert(new_data).execute()

        if response.data:
            return personResponse(**response.data[0])

        raise HTTPException(status_code=500, detail="Error interno del servidor, no se pudo registrar al usuario.")

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error en la solicitud: {e}")
