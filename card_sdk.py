import json
from urllib.parse import urljoin

import requests


class CardSDK:
    base_url: str
    api_key: str

    def __init__(self, base_url: str, api_key: str) -> None:
        self.base_url = base_url
        self.api_key = api_key

    def verify(self, idm: str) -> bool:
        url = urljoin(self.base_url, "/api/card/verify")
        payload = json.dumps({"idm": idm})
        headers = {"X-Api-Key": self.api_key, "Content-Type": "application/json"}
        response = requests.request("GET", url, headers=headers, data=payload)

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(e)
            return False

        try:
            status = response.json()
        except requests.exceptions.JSONDecodeError as e:
            print(e)
            return False

        return status["verified"] is not None and status["verified"]
