from typing import Any
import requests
import urllib.parse
import io
import time
import re
from pypdf import PdfReader

MAX_TOKENS = 10000

class CoreWrapper:
    base_url = "https://api.core.ac.uk/v3"
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.auth_header = { "Authorization": f"Bearer {api_key}" }
        self.cache: dict[str, Any] = {}

    def search(self, query: str, recent_only: bool = False):
        limit = 10
        query = f"_exists_:abstract AND fullText:{query}"
        if recent_only:
            query += " AND yearPublished>2020"

        url = f"{self.base_url}/search/works"
        params = urllib.parse.urlencode(
            { "q": query, "limit": limit }
        )
        headers = self.auth_header | { "Content-Type": "application/json" }

        response = requests.get(
            url,
            params = params,
            headers = headers
        )

        while response.status_code != 200:
            print("fallo en la petición, reintentando en 5s...")
            time.sleep(5)
            response = requests.get(
                url,
                params = params,
                headers = headers
            )

        data = response.json()

        results = []
        for result in data["results"]:
            text = result["fullText"] if "fullText" in result else None
            self.cache[str(result["id"])] = text
            # INFO: https://api.core.ac.uk/docs/v3#tag/Works
            results.append({
                "identifier": str(result["id"]),
                "title": result["title"],
                "abstract": result["abstract"],
                "words": len(result["fullText"]) if text is not None else None,
                "doi": result["doi"],
                "links": result["links"],
                "citation_count": result["citationCount"],
                "published_date": result["publishedDate"] if "publishedDate" in result else None,
                "last_update_date": result["lastUpdate"] if "lastUpdate" in result else None
            })

        return results

    def download(self, identifiers: list[str]):
        documents = {}
        for identifier in identifiers:
            text = (
                str(self.cache[identifier])
                if identifier in self.cache and self.cache[identifier] is not None
                else self._download_pdf(identifier)
            )
            documents[identifier] = " ".join(text.split()[:MAX_TOKENS//len(identifiers)])

        return documents

    def _download_pdf(self, identifier: str):
        max_pages = 10
        max_tries = 10

        headers = self.auth_header | {
            "Content-Type": "application/pdf",
            "accept": "application/pdf"
        }

        response = requests.get(
            f"{self.base_url}/works/{identifier}/download",
            headers = headers,
            stream = True
        )

        while response.status_code != 200 and max_tries >= 0:
            print("fallo en la descarga, reintentando en 5s...")
            time.sleep(5)
            max_tries -= 1

        pdf = PdfReader(io.BytesIO(response.raw.read()))
        text = "\n\n".join([
            page.extract_text()
            for page in pdf.pages[:max_pages]
        ])

        # borra todos los espacios innecesarios
        text = re.sub(r"\s+", " ", text)

        return text
