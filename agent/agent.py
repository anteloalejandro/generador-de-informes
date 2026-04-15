from google.genai import types
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

cwd = os.path.dirname(os.path.abspath(__file__))

core = CoreWrapper(core_key)

def export(report: str):
    with open(f"{cwd}/.output/informe.md", "w") as f:
        f.write(report)

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
    instruction = open(f"{cwd}/instructions.md").read(),
    tools = [core.search, core.download, export],
    generate_content_config=types.GenerateContentConfig(
        max_output_tokens=10000
    )
)

