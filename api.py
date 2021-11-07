import requests

from typing import Any, Dict
from os import getenv
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

API_HOST = getenv("API_HOST")
API_KEY = getenv("API_KEY")


class Api:
    HEADERS = {
        "x-rapidapi-host": API_HOST,
        "x-rapidapi-key": API_KEY,
    }

    def send_request(
        self,
        endpoint: str,
        querystring: Dict[str, str],
        method="GET",
    ) -> Dict[str, Any]:
        url = f"https://{API_HOST}{endpoint}"

        raw_response = requests.request(
            method, url, headers=self.HEADERS, params=querystring
        )

        response = raw_response.json()

        if response.get("result", "") == "OK":
            return response["data"]["body"]

        return response
