# Sobre este repo

Este repo un proyecto de la asignatura de Agentes Inteligentes.

El proyecto consiste en utilizar `google-adk` para crear un Agente que genere un informe sobre "MAS en Videojuegos".

# Objetivo

Diseñar un Agente de IA que razone, genere y estructure un documento a modo de informe sobre un tema determinado, que habrá de materializarse en un documento final generado automáticamente por el propio sistema.

Los pasos a seguir son:
- Creación de un agente
- Uso de tools, callbacks y control del contexto
- Generar tests para la evuluación del funcionamiento.

## Entregables

- Código fuente del sistema, estructurado y documentado
- Informe técnico de dos páginas describiendo la arquitectura del sistema.
- Documento de ejemplo generado automáticamente por el agente.
- JSON generado del ejemplo ¿?

# Setup

**1\. Crear y activar el entorno virtual**
```bash
python -m venv .venv
source .venv/bin/activate
```

**2\. Instalar dependencias**
```bash
pip install -r requirements.txt
```

**3\. Introducir claves para las APIs de CORE y Google.**

Se deben introducir en el fichero `agents/.env`, que habrá que crear de antemano.
En cada línea se pone una entrada, que tendra la forma `KEY = VALUE`

**4\. Habilitar `direnv` para activar entorno automáticamente (opcional)**
```bash
direnv allow .
```

# Ejecución

Para ejecutar el modelo de IA, se debe ejecutar `adk web` para abrir la interfaz web del modelo.

Dentro de la interfaz, se debe hacer una consulta al modelo en las líneas de *"Genera un informe sobre MAS en videojuegos"*, y el modelo de planificar la generación, basandose en referencias internas y generar un JSON con el contenido y estructura del informe final, a partir del cual se creará un PDF.

# Referencias

Referencias sacadas de **scopus** y **google_scholar**.
