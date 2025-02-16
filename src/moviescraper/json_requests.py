from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from seleniumwire import webdriver


def get_json_requests(url):
    """Retrieve all network requests ending in .json from given URL"""

    # Option configurations
    options = Options()
    options.add_argument("--headless")
    options.binary_location = "/usr/bin/chromium"

    # Explicitly set chromedriver path
    service = Service("/usr/bin/chromedriver")

    # Start headless browser session
    driver = webdriver.Chrome(service=service, options=options)

    # Navigate to URL
    driver.get(url)

    # Wait til iframe loads to look for API routes
    wait = WebDriverWait(driver, timeout=20)
    wait.until(lambda d: d.find_element(By.TAG_NAME, "iframe"))

    # Create a list of API routes that end with .json
    api_routes = list()
    for request in driver.requests:
        if request.url.endswith(".json"):
            api_routes.append(request.url)

    # End browser session
    driver.quit()

    return api_routes
