import requests
import urllib.parse
import io
import time
import re
from pypdf import PdfReader

class CoreWrapper:
    base_url = "https://api.core.ac.uk/v3"
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.auth_header = { "Authorization": f"Bearer {api_key}" }

    def search(self, query: str, limit: int = 10):
        # query = f"(abstract:{query} OR fullText:{query}) AND exists:abstract"
        # query = f"exists:abstract AND {query}"
        query = f"_exists_:abstract AND fullText:{query}"
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


        # INFO: https://api.core.ac.uk/docs/v3#tag/Works
        data = response.json()

        results = [
            {
                "title": result["title"],
                "abstract": result["abstract"],
                "field_of_study": result["fieldOfStudy"],
                "citation_count": result["citationCount"],
                "identifier": result["id"]
            }
            for result in data["results"]
        ]

        return results

    def download(self, identifier: str, max_pages: int = 10):
        headers = self.auth_header | {
            "Content-Type": "application/pdf",
            "accept": "application/pdf"
        }

        response = requests.get(
            f"{self.base_url}/works/{identifier}/download",
            headers = headers,
            stream = True
        )

        if response.status_code != 200:
            raise requests.RequestException

        pdf = PdfReader(io.BytesIO(response.raw.read()))
        text = "\n\n".join([
            page.extract_text()
            for page in pdf.pages[:max_pages]
        ])

        # borra todos los espacios innecesarios
        text = re.sub(r"\s+", " ", text)

        return text



