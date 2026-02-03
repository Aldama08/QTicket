# QTicket

# Agente Experto para Help Desk

Este proyecto es un backend construido con FastAPI que funciona como un agente inteligente para un sistema de Help Desk. Su función principal es analizar la descripción de un ticket de soporte, entender su significado y sugerir una solución basada en una base de conocimientos.

---
## ✨ Características Principales

* **Análisis Semántico:** Utiliza `sentence-transformers` para convertir las descripciones de los tickets en vectores numéricos (embeddings) y entender el problema del usuario más allá de las palabras clave.
* **Sugerencia de Soluciones:** Compara el problema del usuario con una base de conocimientos para encontrar la solución más relevante mediante similitud de coseno.
* **Extracción de Palabras Clave:** Usa `KeyBERT` para identificar los términos más importantes del ticket, que pueden ser usados para etiquetado o análisis.
* **API RESTful:** Expone un endpoint para que un frontend pueda interactuar con el agente de manera sencilla.

---
## 🛠️ Tecnologías Utilizadas

* **Backend:** FastAPI, Uvicorn
* **Procesamiento de Lenguaje (NLP):** Sentence-Transformers, KeyBERT, Transformers
* **Base de Datos:** Supabase (PostgreSQL con pg_vector)
* **Computación Científica:** NumPy, Scikit-learn, PyTorch

---
## Para utilizarlo

Sigue estos pasos para configurar y ejecutar el proyecto en tu entorno local.

1.  **Clonar el repositorio**
    ```bash
    git clone https://github.com/Aldama08/QTicket.git
    cd QTicket
    cd Restruct
    ```

2.  **Crear y activar un entorno virtual**
    ```bash
    # En macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # En Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Instalar las dependencias**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Ejecutar el servidor**
    ```bash
    uvicorn backend:app --reload
    ```
    La API estará disponible en `http://127.0.0.1:8000`.

---
## 🔌 Endpoints de la API

La documentación completa e interactiva de la API está disponible en `/docs` una vez que el servidor está en ejecución.

### Procesar un Ticket

* **Endpoint:** `POST /procesar-ticket`
* **Descripción:** Recibe el ID de un ticket existente, analiza su descripción, busca una solución en la base de conocimientos y actualiza el ticket con los resultados.
* **Cuerpo de la Petición (Request Body):**
    ```json
    {
      "ticket_id": "tu-uuid-del-ticket-aqui"
    }
    ```
* **Respuesta Exitosa (Success Response):**
    ```json
    {
      "status": "Procesado exitosamente",
      "ticket_id": "tu-uuid-del-ticket-aqui",
      "solucion_sugerida": "La solución encontrada o un mensaje por defecto.",
      "keywords_extraidas": ["palabra1", "palabra2"]
    }
    ```
---