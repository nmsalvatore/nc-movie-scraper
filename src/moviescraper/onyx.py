#!/usr/bin/env python3

import json
from datetime import date

import requests

.json_requests import get_json_requests


def get_onyx_showings():
    onyx_endpoints = get_json_requests("https://www.theonyxtheatre.com/showtimes/")

    for endpoint in onyx_endpoints:
        response = requests.get(endpoint)

        if not response.ok:
            raise Exception(f"Unsuccessful response from {endpoint}")

        if '"allMovie"' in response.text:
            print(response.url)


# schedule request
def get_schedule():
    try:
        url = "https://www.theonyxtheatre.com/api/gatsby-source-boxofficeapi/schedule"
        body = {
            "theaters": [{"id": "X065X", "timeZone": "America/Los_Angeles"}],
            "movieIds": [
                "1000008919",
                "10403",
                "12551",
                "15254",
                "1763",
                "265940",
                "269838",
                "27765",
                "280195",
                "295068",
                "299",
                "300207",
                "304508",
                "313532",
                "4423",
                "700",
                "727",
            ],
            "from": "2025-02-17T03:00:00",
            "to": "2026-02-17T03:00:00",
            "websiteId": "V2Vic2l0ZU1hbmFnZXJXZWJzaXRlOjhmNzhiNTE3LTlhZjUtNDEzZi04ZWU0LWVjYzNlNmI3NmI0Zg==",
        }

        response = requests.post(url, json=body)
        return response.json()

    except Exception as e:
        print(e)


schedule = get_schedule()

print(json.dumps(schedule, indent=2))
