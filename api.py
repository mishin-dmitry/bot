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
        # NOTE а как лучше анотацию для union делать вместо any?
        # я пробовал Dict[str, Any], я пробовал Dict[str, Union[str, int]]
        # и если в запросе только строки в значениях, то он ошибку выдает
        self,
        endpoint: str,
        querystring: Dict[str, Any],
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
