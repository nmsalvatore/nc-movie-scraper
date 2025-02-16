from .xhr import get_api_routes


def main():
    onyx_routes = get_api_routes("https://www.theonyxtheatre.com/showtimes/")

    for route in onyx_routes:
        print(route)
