#!/usr/bin/env python3

import os
from datetime import datetime

import requests
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
from requests.exceptions import HTTPError, RequestException

from .json_requests import get_json_requests


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

        load_dotenv(env_file)

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
    """A web scraper for movie theater websites.

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
        example_scraper.print_schedule()
    """

    def __init__(self, config: TheaterConfig):
        self.theater_config = config
        self.movie_data = self._fetch_movie_data()
        self.movie_nodes = self._get_movie_nodes()
        self.movie_ids = self._get_movie_ids()
        self.movie_schedule = self._get_theater_schedule()

    def _fetch_movie_data(self) -> tuple[str, dict]:
        """Search the list of JSON requests for the 'allMovie' key

        Returns:
            tuple: Tuple containing (endpoint, movie data)
        """

        for endpoint in get_json_requests(self.theater_config.showtimes_url):
            try:
                response = requests.get(endpoint, timeout=30)
                response.raise_for_status()
                data = response.json().get("data", {})

                if "allMovie" in data and data.get("allMovie") is not None:
                    print(f"Successfully found movie data at: {endpoint}")
                    return (endpoint, data)

            except HTTPError as http_error:
                raise HTTPError(f"Failed to fetch from {endpoint}: {http_error}")

            except RequestException as e:
                raise RequestException(f"Request failed for {endpoint}: {e}")

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
            "theaters": [
                {
                    "id": self.theater_config.theater_id,
                    "timeZone": "America/Los_Angeles",
                }
            ],
            "movieIds": self.movie_ids,
            "from": today.isoformat(),
            "to": today_next_year.isoformat(),
            "websiteId": self.theater_config.website_id,
        }

        response = requests.post(self.theater_config.schedule_endpoint, json=body)
        response.raise_for_status()
        schedule = (
            response.json().get(self.theater_config.theater_id, {}).get("schedule")
        )

        if schedule is None:
            raise ValueError(
                "Response from schedule endpoint was successful, but schedule data could not be found"
            )

        return schedule

    def print_schedule(self) -> None:
        print(self.movie_schedule)


def main():
    onyx_config = TheaterConfig.from_env("env/onyx.env")
    onyx_scraper = TheaterScraper(onyx_config)
    onyx_scraper.print_schedule()
