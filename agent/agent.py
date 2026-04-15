import json
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm  

from dotenv import load_dotenv, dotenv_values
import os

from markdown_pdf import MarkdownPdf, Section
from markdown_parser import MarkdownTree
from typing import Any

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
    file_path = f"{cwd}/output/informe.pdf"
    pdf = MarkdownPdf()
    pdf.add_section(Section(report))
    pdf.save(file_path)

    tree = MarkdownTree()
    tree.parse(report)
    root = tree.root.children[0]
    sections: list[dict[str, Any]] = [
        {
            "name": section.title,
            "word_count": len(section.dump().split())
        }
        for section in root.children
    ]

    root.print_tree()

    json_object = {
        "title": root.title,
        "sections": sections,
        "total_words": len(report.split()),
        "num_sections": len(sections),
        "num_references": core.last_identifiers_count,
        "pdf_path": file_path
    }

    with open(f"{cwd}/output/informe.json", "w") as f:
        f.write(json.dumps(json_object))

    return json_object

# ------------------------
# ROOT AGENT (multi-tool)
# ------------------------

root_agent = LlmAgent(
    name = "Agente Investigador",
    #model="gemini-2.0-flash",
    model = LiteLlm(model="openai/gpt-oss-120b", api_base="https://api.poligpt.upv.es/", api_key=openai_key),
    description = "\n".join([
        "Agente que investiga artículos científicos sobre inteligencia artificial y agentes en inglés, y produce informes en español.",
        "Siempre se informa antes de decidir qué va a escribir."
    ]),
    instruction = open(f"{cwd}/instructions.md").read(),
    tools = [core.search, core.download, export],
)

