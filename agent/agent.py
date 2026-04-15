from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm  

from dotenv import load_dotenv, dotenv_values
import os

from agent.core_wrapper import CoreWrapper

load_dotenv()
print(f"DOTENV VALUES: {dotenv_values()}")

if (core_key := os.getenv("CORE_API_KEY")) is None:
    raise ValueError("Falta la clave de la API de CORE en `agents/.env` (CORE_API_KEY=xxx)")


if (openai_key := os.getenv("OPENAI_API_KEY")) is None:
    raise ValueError("Falta la clave de la API de OpenAI en `agents/.env` (OPENAI_API_KEY=xxx)")

core = CoreWrapper(core_key)
# ------------------------
# ROOT AGENT (multi-tool)
# ------------------------

root_agent = LlmAgent(
    name = "investigador",
    #model="gemini-2.0-flash",
    model = LiteLlm(model="openai/gpt-oss-120b", api_base="https://api.poligpt.upv.es/", api_key=openai_key),
    description = "\n".join([
        "Agente que investiga artículos científicos sobre inteligencia artificial y agentes en inglés, y produce informes en español.",
        "Siempre se informa antes de decidir qué va a escribir."
    ]),
    instruction = "\n".join([
        "Eres un investigador en materia de Agentes. Investigas artículos científicos sobre inteligencia artificial y agentes en inglés, y produces informes sobre el tema en exclusivamente en español.",
        "SIEMPRE te informas antes de decidir sobre qué vas a escribir, y TODA la información que escribas debe estar fundamentada en algún artículo que has leído.",
        "Los artículos en los que te fundamentas DEBEN estar plasmados en la sección de Referencias del informe",
        "Las únicas tools a las que tienes acceso son search(keywords) y download(identifier). NO PUEDES usar ninguna más."
        "Pasos:",
        "1. DEBES elegir unas palabras clave para tu búsqueda."
            "SIEMPRE que haya acrónimos tratarás de inferir los términos que lo componen para elegir las palabras clave de tu búsquda (Por ejemplo, 'MAS' se descompone en 'multi-agent systems')."
            "Asume que los acrónimos tienen que ver con tu campo de estudio."
            "SIEMPRE debes coger alguna palabra que no esté en el acrónimo, excepto artículos, preposiciones, conjunciones o otras palabras triviales, que nunca deberán ser consideradas palabra clave",
            "NO ERES creativo con la selección de palabras clave, no inventas palabras clave que no aparezcan o están directamente relacionadas con lo que se te pregunta"
        "2. Llama a `search(keywords)`",
        "3. Mirando el abstract de los artículos, elige 2 que sean relevantes",
        "4. Para los 2 artículos elegidos, llama a `download(identifier)`. Una vez llegado a este punto, NO PUEDES buscar más artículos.",
        "5. Basándote ÚNICAMENTE en el contenido de los artículos descargados, escribe un informe detallado"
    ]),
    tools = [core.search, core.download]
)
