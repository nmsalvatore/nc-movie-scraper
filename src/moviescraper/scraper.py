#!/usr/bin/env python3

import os
from datetime import datetime

import dotenv
import requests
from dateutil import relativedelta as date_delta
from requests import exceptions as req_exceptions

from . import browser


class TheaterConfig:
    """The configuration class required by the TheaterScraper class.

    A configuration class storing venue-specific information to be used
    by the TheaterScraper class and the Boxoffice CMS API.

    Attributes:
        showtimes_url: The base URL where showtimes are listed on
            the movie theater website
        website_id: Website ID used by Boxoffice CMS
        theater_id: Theater ID used by Boxoffice CMS
        schedule_endpoint: API endpoint holding movie schedule data

    Example usage:
        example_config = TheaterConfig(
            "https://www.example.com/showtimes",
            "S0meAlPh@numER1C+hing",
            "ABC123",
            "https://www.example.com/api/schedule"
        )
        example_scraper = TheaterScraper(example_config)
    """

    def __init__(
        self,
        showtimes_url: str,
        website_id: str,
        theater_id: str,
        schedule_endpoint: str,
    ):
        """Initialize class attributes using arguments.

        Args:
            showtimes_url: The base URL where showtimes are listed on
                the movie theater website
            website_id: Website ID used by Boxoffice CMS
            theater_id: Theater ID used by Boxoffice CMS
            schedule_endpoint: API endpoint holding movie schedule data
        """
        self.showtimes_url = showtimes_url
        self.website_id = website_id
        self.theater_id = theater_id
        self.schedule_endpoint = schedule_endpoint

    @classmethod
    def from_env(cls, env_file: str) -> "TheaterConfig":
        """Instantiate TheaterConfig using environment variables.

        As an alternative method for instantiation, this method will
        instantiate the TheaterConfig class and initialize the class
        attributes using environment variables stored in a .env file.

        Args:
            env_file: The path to an .env file from the project's
                root directory

        Example usage:
            example_config = TheaterConfig.from_env("env/example.env")
            example_scraper = TheaterScraper(example_config)
        """

        dotenv.load_dotenv(env_file)

        required_vars = [
            "SHOWTIMES_URL",
            "WEBSITE_ID",
            "THEATER_ID",
            "SCHEDULE_ENDPOINT",
        ]
        missing_vars = [var for var in required_vars if not os.getenv(var)]

        if missing_vars:
            raise ValueError(
                f"Missing required environment variables from {env_file}: {', '.join(missing_vars)}"
            )

        return cls(
            showtimes_url=os.getenv("SHOWTIMES_URL", ""),
            website_id=os.getenv("WEBSITE_ID", ""),
            theater_id=os.getenv("THEATER_ID", ""),
            schedule_endpoint=os.getenv("SCHEDULE_ENDPOINT", ""),
        )


class TheaterScraper:
    """A web scraper for Boxoffice CMS movie theater websites.

    The web scraper handles fetching and parsing of movie data
    from movie theater websites powered by Boxoffice CMS through their
    API endpoints.

    Args:
        config: Configuration class for specific movie theater

    Attributes:
        theater_config: Configuration class for specific movie theater
        movie_data: Tuple containing endpoint used to fetch data and
            the movie data itself
        movie_nodes: List of movie nodes contained in movie data
        movie_ids: List of movie IDs as identified by Boxoffice CMS
        movie_schedule: List of movie showings

    Example usage:
        example_config = TheaterConfig.from_env("env/example.env")
        example_scraper = TheaterScraper(example_config)
    """

    def __init__(self, config: TheaterConfig):
        self.theater_config = config
        self.movie_data = self._fetch_movie_data()
        self.movie_nodes = self._get_movie_nodes()
        self.movie_ids = self._get_movie_ids()

    def _fetch_movie_data(self) -> tuple[str, dict]:
        """Find movie data from list of JSON requests.

        Searches list of JSON requests for 'allMovie' key in response
        data for each endpoint. If the key is found and key value is
        not None, returns a tuple containing the endpoint and the
        response data.

        Returns:
            (endpoint, movie_data): Tuple containing API endpoint containing
                the 'allMovie' key and the data provided by the value
                of the 'allMovie' key
        """

        showtimes_url = self.theater_config.showtimes_url

        for endpoint in browser.get_json_requests(showtimes_url):
            try:
                response = requests.get(endpoint, timeout=30)
                response.raise_for_status()
                data = response.json().get("data", {})

                if "allMovie" in data and data.get("allMovie") is not None:
                    print(f"Successfully found movie data at: {endpoint}")

                    movie_data = data["allMovie"]
                    return (endpoint, movie_data)

            except req_exceptions.RequestException as e:
                raise req_exceptions.RequestException(
                    f"Failed to get movie data from {endpoint}: {e}"
                )

        raise ValueError("Could not find API endpointing containing the 'allMovie' key")

    def _get_movie_nodes(self) -> list[dict]:
        """Get list of movies nodes.

        Returns:
            nodes: A list containing nodes for each movie
                currently listed on the theater website
        """

        _, data = self.movie_data
        nodes = data["nodes"]
        return nodes

    def _get_movie_ids(self) -> list[str]:
        """Get list of movie IDs from movie nodes.

        Returns:
            ids: A list of IDs representing all movies currently
                listed on the theater website
        """

        ids = [node.get("id") for node in self.movie_nodes]
        return ids

    def print_movie_titles(self) -> None:
        """Print movie titles, each separated by a newline"""

        if self.movie_nodes is None:
            raise ValueError("Cannot print movie data if movie_nodes is None")

        movie_titles = [movie.get("title") for movie in self.movie_nodes]

        for title in movie_titles:
            print(title)

    def get_schedule(self) -> list[dict]:
        """Get current schedule for theater.

        Make a POST request to the schedule_endpoint using today's
        date and the movie IDs found in the current endpoint containing
        movie data.

        Returns:
            schedule: A list of unparsed showings, as provided by the
                Boxoffice CMS API
        """

        config = self.theater_config

        today = datetime.today()
        today_next_year = today + date_delta.relativedelta(years=1)

        body = {
            "theaters": [
                {
                    "id": config.theater_id,
                    "timeZone": "America/Los_Angeles",
                }
            ],
            "movieIds": self.movie_ids,
            "from": today.isoformat(),
            "to": today_next_year.isoformat(),
            "websiteId": config.website_id,
        }

        try:
            response = requests.post(config.schedule_endpoint, json=body, timeout=30)
            response.raise_for_status()
            schedule = (
                response.json().get(config.theater_id, {}).get("schedule")
            )

            if schedule is None:
                raise ValueError(
                    "Response from schedule endpoint was successful, but schedule data could not be found"
                )

            return schedule

        except req_exceptions.RequestException as e:
            raise req_exceptions.RequestException(
                f"Failed to get schedule from {config.schedule_endpoint}: {e}"
            )


def main():
    onyx_config = TheaterConfig.from_env("env/onyx.env")
    onyx_scraper = TheaterScraper(onyx_config)

    schedule = onyx_scraper.get_schedule()
    print(schedule)
