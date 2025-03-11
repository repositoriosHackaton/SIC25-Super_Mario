from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import uvicorn
from google import genai
import numpy as np
import re
from collections import Counter

app = FastAPI()

# Habilitar CORS para permitir peticiones desde cualquier origen
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Funciones para calcular la similitud de cosenos
def text_to_vector(text):
    #saca las palabras del texto y las cuenta
    words = re.findall(r'\w+', text.lower())
    return Counter(words)

def cosine_similarity(vec1, vec2):
    #calcula el producto escalar entre dos vectores en un diccionario
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])
    
    sum1 = sum([v**2 for v in vec1.values()])
    sum2 = sum([v**2 for v in vec2.values()])
    denominator = np.sqrt(sum1) * np.sqrt(sum2)
    
    if not denominator:
        return 0.0
    else:
        return float(numerator) / denominator

def get_cosine_sim(text1, text2):
    vec1 = text_to_vector(text1)
    vec2 = text_to_vector(text2)
    return cosine_similarity(vec1, vec2)

# Cargar el json con las preguntas y respuestas
with open("sacrum.json", "r", encoding="utf-8") as f:
    data = json.load(f)

qa_pairs = []
for bloque in data["informacion"]:
    preguntas = bloque["Preguntas"]
    respuestas = bloque["Respuesta"]
    for pregunta, respuesta in zip(preguntas, respuestas):
        qa_pairs.append((pregunta.lower(), respuesta))

# crea una lista de preguntas para facilitar la busqueda
preguntas_lista = [p for p, _ in qa_pairs]

class MessageRequest(BaseModel):
    prompt: str

# configuracion de la api de gemeni con la api_key
GEMINI_API_KEY = "AIzaSyAPCbQcoHDVlqj_aP1ZngITU0fnUfBEOZQ"
gemini_client = genai.Client(api_key=GEMINI_API_KEY)

@app.post("/generate")
def generate_message(request: MessageRequest):
    prompt = request.prompt.lower()
    
    # usamos similitud de cosenos para conseguir la respuesta mas cercana
    max_similarity = 0.0
    best_index = None
    for idx, question in enumerate(preguntas_lista):
        sim = get_cosine_sim(prompt, question)
        if sim > max_similarity:
            max_similarity = sim
            best_index = idx

    # Si la similitud es mayor a 50% se da la respuesta
    if max_similarity >= 0.5 and best_index is not None:
        return {"generated_text": qa_pairs[best_index][1]}
    
    # si tiene menos del 50% usa el modelo de gemini para generar la respuesta segun esta prompt
    prompt_base = (
        "Eres el chatbot oficial de la Iglesia San Martín de Porres. Toda tu información "
        "y respuestas deben estar alineadas con los datos, servicios y actividades de la iglesia. "
        "Si la pregunta no se relaciona con la iglesia o no tienes información, responde: "
        "'Lo siento, no tengo información sobre ese tema.'\n\nPregunta: "
    )
    full_prompt = prompt_base + request.prompt

    response = gemini_client.models.generate_content(
        model="gemini-2.0-flash",
        contents=full_prompt
    )
    return {"generated_text": response.text}

if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)