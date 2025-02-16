from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from seleniumwire import webdriver


def get_json_requests(url):
    """Retrieve all network requests ending in .json from a given URL"""

    options = Options()
    options.add_argument("--headless")
    options.binary_location = "/usr/bin/chromium"

    service = Service("/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)

    driver.get(url)

    wait = WebDriverWait(driver, timeout=20)
    wait.until(lambda d: d.find_element(By.TAG_NAME, "iframe"))

    api_routes = list()
    for request in driver.requests:
        if request.url.endswith(".json"):
            api_routes.append(request.url)

    driver.quit()

    return api_routes
