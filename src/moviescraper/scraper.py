#!/usr/bin/env python3

import requests
from requests.exceptions import HTTPError

from .json_requests import get_json_requests


class Scraper:
    def __init__(self, url):
        self.url = url
        # self.website_id = website_id
        # self.theater_id = theater_id
        # self.api_endpoint = api_endpoint
        self.movie_data = self._fetch_movie_data()
        self.movie_nodes = self._get_movie_nodes()

    def _fetch_movie_data(self) -> tuple | None:
        """Search the list of JSON requests at a given URL for the
        'allMovie' key"""

        for endpoint in get_json_requests(self.url):
            try:
                response = requests.get(endpoint)
                response.raise_for_status()
                data = response.json().get("data", {})

                if "allMovie" in data:
                    if data.get("allMovie") is not None:
                        return (endpoint, data)

            except HTTPError as http_error:
                print(f"An HTTP error occurred: {http_error}")

            except Exception as error:
                print(f"An error occurred: {error}")

    def _get_movie_nodes(self) -> list:
        """Get movie nodes from movie_data"""

        if self.movie_data is None:
            raise ValueError(
                "Cannot fetch movie nodes if movie_data is None"
            )

        _, data = self.movie_data
        return data["allMovie"]["nodes"]

    def print_movies(self) -> None:
        """Print movie data"""

        if self.movie_nodes is None:
            raise ValueError("Cannot print movie data if movie_nodes is None")

        movie_titles = [movie.get("title") for movie in self.movie_nodes]

        for title in movie_titles:
            print(title)


def main():
    onyx_scraper = Scraper("https://www.theonyxtheatre.com/showtimes/")
    onyx_scraper.print_movies()
