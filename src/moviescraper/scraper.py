from .json_requests import get_json_requests


def main():
    onyx_routes = get_json_requests("https://www.theonyxtheatre.com/showtimes/")

    for route in onyx_routes:
        print(route)
