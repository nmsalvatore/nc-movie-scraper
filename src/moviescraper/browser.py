#!/usr/bin/env python3

from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from seleniumwire import webdriver


def get_json_requests(url: str) -> list[str]:
    """Retrieve all network requests ending in .json from a given URL"""

    print(f"Compiling list of JSON requests at: {url}")

    driver = None

    try:
        options = Options()
        options.add_argument("--headless")
        options.binary_location = "/usr/bin/chromium"
        service = Service("/usr/bin/chromedriver")

        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)

        wait = WebDriverWait(driver, timeout=20)
        wait.until(lambda d: d.find_element(By.TAG_NAME, "iframe"))

        endpoints: list[str] = []

        for request in driver.requests:
            if request.url.endswith(".json"):
                endpoints.append(request.url)

        return endpoints

    except Exception as e:
        print(f"Failed to retrieve JSON requests from {url}:", e)
        return []

    finally:
        if driver:
            driver.quit()
