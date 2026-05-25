import uuid
import time

import pytest
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "http://localhost:8000"
STATIC_URL = f"{BASE_URL}/static"


@pytest.fixture(scope="session")
def driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1280,800")
    options.add_argument("--disable-dev-shm-usage")
    service = Service()
    drv = webdriver.Edge(service=service, options=options)
    drv.implicitly_wait(5)
    yield drv
    drv.quit()


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


@pytest.fixture(scope="session")
def static_url():
    return STATIC_URL


@pytest.fixture
def wait(driver):
    return WebDriverWait(driver, 10)


@pytest.fixture(scope="session")
def test_username():
    return f"sel_user_{uuid.uuid4().hex[:8]}"


@pytest.fixture(scope="session")
def test_password():
    return "selTest123456"


def _clear_storage(driver, base_url):
    driver.get(f"{base_url}/login.html")
    time.sleep(0.5)
    driver.execute_script("localStorage.clear();")


def _login(driver, base_url, username, password):
    driver.get(f"{base_url}/login.html")
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys(username)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.ID, "loginBtn").click()
    wait.until(EC.url_contains("index.html"))


@pytest.fixture(scope="session", autouse=True)
def _register_user(driver, base_url, test_username, test_password):
    _clear_storage(driver, base_url)
    driver.get(f"{base_url}/register.html")
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys(test_username)
    driver.find_element(By.ID, "password").send_keys(test_password)
    driver.find_element(By.ID, "confirmPassword").send_keys(test_password)
    driver.find_element(By.ID, "registerBtn").click()
    wait.until(EC.url_contains("index.html"))
    _clear_storage(driver, base_url)


@pytest.fixture
def logged_in_driver(driver, base_url, test_username, test_password):
    _clear_storage(driver, base_url)
    _login(driver, base_url, test_username, test_password)
    return driver
