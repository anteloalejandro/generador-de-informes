import json
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm  

from dotenv import load_dotenv, dotenv_values
import os

from markdown_pdf import MarkdownPdf, Section
from markdown_parser import MarkdownTree
from typing import Any

from agent.core_wrapper import CoreWrapper

try:
    # Newer docs often show this path.
    from google.adk.agents.llm_agent import Agent  # type: ignore
except Exception:  # pragma: no cover
    from google.adk.agents import Agent  # type: ignore


from google.adk.models.lite_llm import LiteLlm 


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

    with open(f"{cwd}/output/informe.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(json_object))

    return json_object

search = core.search
download = core.download

# ------------------------
# ROOT AGENT (multi-tool)
# ------------------------

root_agent = Agent(
    #model="gemini-3-flash-preview",
    model=LiteLlm(model="openai/gpt-oss-120b", api_base="https://api.poligpt.upv.es/", api_key="sk-LFXs1kjaSxtEDgOMlPUOpA"),

    name="root_agent",
    description = "\n".join([
        "Agente que investiga artículos científicos sobre inteligencia artificial y agentes en inglés, y produce informes en español.",
        "Siempre se informa antes de decidir qué va a escribir."
    ]),
    instruction = open(f"{cwd}/instructions.md", encoding="utf-8").read(),
    tools=[search, download, export],
)

