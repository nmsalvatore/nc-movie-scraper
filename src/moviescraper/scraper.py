#!/usr/bin/env python3

from datetime import datetime
from dateutil.relativedelta import relativedelta

import requests
from requests.exceptions import HTTPError

from .json_requests import get_json_requests


class Scraper:
    def __init__(self, url, config):
        self.url = url
        self.website_id = config.get("website_id")
        self.theater_id = config.get("theater_id")
        self.schedule_endpoint = config.get("schedule_endpoint")
        self.movie_data = self._fetch_movie_data()
        self.movie_nodes = self._get_movie_nodes()
        self.movie_ids = self._get_movie_ids()
        self.movie_schedule = self._get_theater_schedule()

    def _fetch_movie_data(self) -> tuple:
        """
        Search the list of JSON requests for the 'allMovie' key
        """

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

        raise ValueError("Could not find API endpointing containing the 'allMovie' key")

    def _get_movie_nodes(self) -> list:
        """
        Get list of nodes from movie_data
        """

        _, data = self.movie_data
        return data["allMovie"]["nodes"]

    def _get_movie_ids(self) -> list:
        """
        Get movie ID from each node and return them all in a list
        """

        return [node.get("id") for node in self.movie_nodes]

    def print_movies(self) -> None:
        """
        Print movie data
        """

        if self.movie_nodes is None:
            raise ValueError("Cannot print movie data if movie_nodes is None")

        movie_titles = [movie.get("title") for movie in self.movie_nodes]

        for title in movie_titles:
            print(title)

    def _get_theater_schedule(self) -> list:
        """
        Create post request for theater schedule and return the value
        of the schedule key.
        """

        today = datetime.today()
        today_next_year = today + relativedelta(years=1)

        body = {
            "theaters": [{"id": self.theater_id, "timeZone": "America/Los_Angeles"}],
            "movieIds": self.movie_ids,
            "from": today.isoformat(),
            "to": today_next_year.isoformat(),
            "websiteId": self.website_id,
        }

        response = requests.post(self.schedule_endpoint, json=body)
        response.raise_for_status()

        data = response.json()
        schedule = data.get(self.theater_id, {}).get("schedule")

        if schedule is None:
            raise ValueError(
                "Response from schedule endpoint was successful, but schedule data could not be found"
            )

        return schedule

    def print_movie_schedule(self) -> None:
        print(self.movie_schedule)


def main():
    onyx_scraper = Scraper(
        "https://www.theonyxtheatre.com/showtimes/",
        {
            "theater_id": "X065X",
            "website_id": "V2Vic2l0ZU1hbmFnZXJXZWJzaXRlOjhmNzhiNTE3LTlhZjUtNDEzZi04ZWU0LWVjYzNlNmI3NmI0Zg==",
            "schedule_endpoint": "https://www.theonyxtheatre.com/api/gatsby-source-boxofficeapi/schedule"
        }
    )

    onyx_scraper.print_movie_schedule()
