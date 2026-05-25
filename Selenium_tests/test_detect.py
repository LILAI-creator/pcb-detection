import os
import time
from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


TEST_IMAGE_DIR = Path(__file__).resolve().parent.parent / "test"


class TestDetectPage:
    def test_detect_page_requires_login(self, driver, base_url, wait):
        driver.get(f"{base_url}/login.html")
        time.sleep(0.5)
        driver.execute_script("localStorage.clear();")
        driver.get(f"{base_url}/static/index.html")
        time.sleep(2)
        current = driver.current_url
        assert "login.html" in current

    def test_detect_page_navbar(self, logged_in_driver, static_url, wait):
        driver = logged_in_driver
        driver.get(f"{static_url}/index.html")
        brand = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".navbar-brand")))
        assert "PCB" in brand.text

    def test_detect_page_upload_zone(self, logged_in_driver, static_url, wait):
        driver = logged_in_driver
        driver.get(f"{static_url}/index.html")
        zone = wait.until(EC.presence_of_element_located((By.ID, "uploadZone")))
        assert zone.is_displayed()

    def test_detect_page_defect_legend(self, logged_in_driver, static_url, wait):
        driver = logged_in_driver
        driver.get(f"{static_url}/index.html")
        wait.until(EC.presence_of_element_located((By.ID, "uploadZone")))
        page_text = driver.find_element(By.TAG_NAME, "body").text
        assert "missing_hole" in page_text
        assert "mouse_bite" in page_text

    def test_detect_logout_button(self, logged_in_driver, static_url, wait):
        driver = logged_in_driver
        driver.get(f"{static_url}/index.html")
        logout_btn = wait.until(EC.presence_of_element_located((By.ID, "logoutBtn")))
        assert logout_btn.is_displayed()

    def test_detect_nav_links(self, logged_in_driver, static_url, wait):
        driver = logged_in_driver
        driver.get(f"{static_url}/index.html")
        wait.until(EC.presence_of_element_located((By.ID, "uploadZone")))
        links = driver.find_elements(By.CSS_SELECTOR, ".navbar-links a")
        hrefs = [a.get_attribute("href") for a in links]
        assert any("index.html" in h for h in hrefs)
        assert any("history.html" in h for h in hrefs)
