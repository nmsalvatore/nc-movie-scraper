#!/usr/bin/env python3

import json
from datetime import date

import requests

from .json_requests import get_json_requests


def main():
    onyx_endpoints = get_json_requests("https://www.theonyxtheatre.com/showtimes/")

    movie_endpoint = ""

    for endpoint in onyx_endpoints:
        endpoint_response = requests.get(endpoint)

        if not endpoint_response.ok:
            raise Exception(f"Unsuccessful response from {endpoint}")

        def key_exists(d, key):
            return key in d or any(key_exists(v, key) for v in d.values() if isinstance(v, dict))

        if key_exists(endpoint_response.json(), "allMovie"):
            movie_endpoint = endpoint_response.url
            break

    movie_response = requests.get(movie_endpoint)

    if not movie_response.ok:
        raise Exception(f"Unsuccessful response from {movie_endpoint}")

    print(json.dumps(movie_response.json(), indent=2))
