from .json_requests import get_json_requests


def main():
    onyx_endpoints = get_json_requests("https://www.theonyxtheatre.com/showtimes/")
    prime_endpoints = get_json_requests("https://www.prime-cinemas.com/showtimes/")

    for route in onyx_endpoints + prime_endpoints:
        print(route)
