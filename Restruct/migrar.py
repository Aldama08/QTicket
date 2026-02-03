import os
from supabase import create_client, Client
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# 1. Cargar variables de entorno
load_dotenv()

# 2. Configuración de Clientes
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 3. Cargar el modelo (Debe ser el mismo que usas en el backend)
print("Cargando modelo para migración...")
embedding_model = SentenceTransformer("paraphrase-multilingual-mpnet-base-v2")

def migrar_embeddings():
    print("Buscando registros sin embedding...")
    # Buscamos los que están en NULL
    response = supabase.table('knowledge_base').select('id, solucion').is_('embedding', 'null').execute()
    
    nulos = response.data
    
    if not nulos:
        print("No hay registros pendientes de procesar.")
        return

    print(f"Procesando {len(nulos)} registros...")
    
    for registro in nulos:
        # Generar el vector
        vector = embedding_model.encode(registro['solucion']).tolist()
        
        # Actualizar en Supabase
        supabase.table('knowledge_base').update({'embedding': vector}).eq('id', registro['id']).execute()
        print(f"✅ Vector generado y guardado para ID: {registro['id']}")

if __name__ == "__main__":
    migrar_embeddings()
    print("¡Migración completada!")