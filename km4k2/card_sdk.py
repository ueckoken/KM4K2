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
        """
        Raises:
            requests.exceptions.HTTPError: if API returns unexpected HTTP status
            requests.exceptions.JSONDecodeError: if API returns invalid JSON
        """
        url = urljoin(self.base_url, "/api/card/verify")
        payload = json.dumps({"idm": idm})
        headers = {"X-Api-Key": self.api_key, "Content-Type": "application/json"}
        response = requests.request("GET", url, headers=headers, data=payload)

        if response.status_code == requests.codes.not_found:  # unregistered
            return False
        if response.status_code == requests.codes.forbidden:  # expired
            return False

        response.raise_for_status()

        # ok
        status = response.json()
        return status["verified"]
