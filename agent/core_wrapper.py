from time import sleep
import requests
from pypdf import PdfReader

class CoreWrapper:
    base_url = "https://api.core.ac.uk/v3"
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.auth_header = { "Authorization": f"Bearer {api_key}" }

    def search(self, query: str, limit: int = 10):
        url = f"{self.base_url}/search/works"
        params = { "q": query, "limit": limit }
        headers = self.auth_header | { "Content-Type": "application/json" }

        response = requests.get(
            url,
            params = params,
            headers = headers
        )

        max_tries = 5
        while response.status_code != 200 and max_tries >= 0:
            sleep(5)
            max_tries -= 1
            response = requests.get(
                url,
                params = params,
                headers = headers
            )
        if response.status_code != 200:
            raise requests.RequestException


        # INFO: https://api.core.ac.uk/docs/v3#tag/Works
        data = response.json()

        return {
            "title": data.title,
            "abstract": data.abstract,
            "field_of_study": data.fieldOfStudy,
            "citation_count": data.citationCount,
            "identifier": data.id
        }

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

        pdf = PdfReader(response)
        text = "\n\n".join([
            page.extract_text()
            for page in pdf.pages[:max_pages]
        ])

        return text



