#import "@preview/ilm:2.0.0": *
#import "@preview/calloutly:1.0.0" : callout-style, callout, note, tip, important, warning, caution

#set text(lang: "es")
#set figure(supplement: "Figura")

#show: ilm.with(
  title: "Arquitectura del Agente Generador de Informes",
  authors: ("Alejandro Antelo Fashoro", "Pau Riera Ribes"),
  date: datetime.today(),
  date-format: "[day] / [month] / [year repr:full]",
  raw-text: "use-typst-default",
  table-of-contents: none,
  external-link-circle: false,
  chapter-pagebreak: false,
  footer: "page-number-center",
  paper-size: "a4",
)

#show: callout-style.with(style: "quarto")

= Introducción

Este Agente generador de informes genera está pensado para generar informes sobre "MAS en videojuegos".

Con este fin, se ha creado un agente con *acceso a internet* que puede buscar artículos científicos relevantes para su propósito.

= _Tools_

El agente cuenta con 3 _tools_:

- ```python search(keywords: str, recent_only: bool)```
- ```python download(intentifer: str)```
- ```python export(markdown: str)```

`search` y `download` son métodos de la clase `CoreWrapper`, que abstrae la complejidad de interactuar con la API REST de #link("https://core.ac.uk/")[CORE].

`search` busca un número limitado de artículos científicos que coincidan con las `keywords` pasadas, y devuelve una lista de coincidencias en forma de `dict`, con las siguientes entradas:

```python
{
  "identifier": str,
  "title": str,
  "abstract": str,
  "words": int | None,
  "doi": str,
  "links": list[str],
  "citation_count": int,
  "published_date": str | None,
  "last_update_date": str | None
}
```

Además, al hacer la búsqueda se guarda en una caché interna el contenido de los artículos. Así se ahorra tiempo, recursos y tókens de la API CORE cuando el modelo de IA decida descargar el artículo usando la _tool_ `download`.

En caso de que no se haya podido guardar el artículo en la caché, `download` tratará de buscar de forma programática el PDF del artículo y, haciendo uso de la librería `pypdf`, lo convierte a texto plano.

#callout(title: [Uso de `dict` en los valores de retorno])[
  Hemos detectado que usar `dict`s en vez de listas o tipos más básicos ayuda a que el Agente entienda mejor los datos que ha recibido y qué debe hacer con ellos, ya que podemos darle un sentido semántico a las claves de los valores que devolvamos.

  Por esto mismo, la _tool_ `download`, que podría devolver una lista de artículos, devuelve un `dict` en su lugar.
]

Finalmente, la _tool_ `export` hace una serie de cosas:
- *Genera y guarda* un PDF a partir del `markdown`, usando la librería `markdown-pdf`.
- *Analiza* la estructura del `markdown` para extraer las secciones y el conteo de palabras por cada sección, usando la librería `markdown-parser-py`.
- *Devuelve* un `dict` (que también exporta a `.json`) con la información que pide la práctica para que el Agente pueda mostrársela al usuario.


= Instrucciones

Como todas las referencias que va a usar el modelo están en inglés, le hemos indicado que es un investigador cuyo trabajo es generar reportes en español sobre inteligencia artificial basándose en artículos científicos en inglés. También le hemos indicado que en sus informes siempre cita sus fuentes en un apartado "Referencias".

En líneas generales, queremos que el Agente siga los siguientes pasos:

+ Analizar el _prompt_ del usuario para *averiguar las palabras clave* que usar en la búsqueda.
+ *Buscar* con la _tool_ `search` y *decidir* cuáles de los resultados son relevantes.
  + Si el Agente decide que no tiene suficientes artículos o no son suficientemente relevantes, *puede hacer una búsqueda nueva* (un número limitado de veces) con nuevas palabras clave.
+ Coger los `identifier` de los artículos relevantes y pasarlos a la _tool_ `download` para *descargar su contenido*.
+ Utiliza artículos descargados para *generar un informe* en formato Markdown.
+ *Exportar el informe* con la _tool_ `export` y *mostrar las estadísticas* del informe (no el informe en sí mismo) y la ruta del PDF generado.

#callout(title: "¿Por qué Markdown?")[
  Markdown se ha elegido como formato para el informe y para las instrucciones del Agente porque los LLM son inheremente buenos generando y leyendo Markdown.
]

Al Agente se le pasa en su parámetro `instruction` el contenido del archivo `agent/instructions.md`. En él, además de delinear los pasos mencionados antes, ha hecho falta *coaccionar al Agente y reforzar ciertos conceptos* para que usase las _tools_ como se le pedía o que evitase hacer cosas que se le había prohibido explícitamente.

Aún así pueden aparecer, esporádicamente, problemas puntuales como que el modelo alucine una _tool_ `search.commentary` o `search<|channel|>.commentary`, o que muestre el informe sin exportarlo, a pesar de que se ha intentado mitigar proveyendo al Agente en sus instrucciones de la lista _tools_ a las que tiene acceso, junto a los parámetros que recibe y una breve descripción.

= Tests

Hemos usado un Agente Juez para evaluar la calidad de las peticiones finales. El Juez evalúa los siguientes criterios de calidad de la respuesta:

- El texto está en español, salvo términos técnicos.
- Se muestran los datos del informe generado.
- Se muestra la ruta al PDF del informe generado.
- Se asegura de que no muestra el informe completo, pero sí sus datos.

#callout(title: "Sobre los tests deterministas sin juez")[
  Este Agente tiene dos particularidades que hace que los tests sin juez no sean particularmente útiles.

  + Las respuestas finales pueden variar mucho y seguir siendo correctas, ya que el informe generado puede ser diferente cada vez si la petición no es muy específica, y por tanto los titulos de sus secciones y el conteo de palabras será diferente cada vez.

  + El uso de herramientas no será particularmente similar, porque puede llamar a `search` de forma interativa.

  Por esto mismo, no hemos usado tests sin juez y hemos puesto la `tool_trajectory_avg_score` a 0.
]

También se ha usado a otro Agente Juez que evalúa el uso de las llamadas a las _tools_, con los siguientes criterios:

- La última llamada que se hace es a `export`
- La llamada anterior a `export` es `download`
- La llamada a `download` se hace entre 2 y 5 _identifiers_
- La primera llamada es `search`
- No se llama a `search` más de 3 veces

= Referencias

Todas referencias bibliográficas del modelo se obtienen en tiempo de ejecución de la #link("https://core.ac.uk/")[*API de CORE*]: _#link("https://core.ac.uk/")_
