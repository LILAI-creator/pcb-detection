import uuid
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TestRegisterPage:
    def test_register_page_loads(self, driver, base_url, wait):
        driver.get(f"{base_url}/register.html")
        title = wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        assert "PCB缺陷检测" in title.text

    def test_register_form_elements(self, driver, base_url, wait):
        driver.get(f"{base_url}/register.html")
        wait.until(EC.presence_of_element_located((By.ID, "username")))
        assert driver.find_element(By.ID, "username").is_displayed()
        assert driver.find_element(By.ID, "password").is_displayed()
        assert driver.find_element(By.ID, "confirmPassword").is_displayed()
        assert driver.find_element(By.ID, "registerBtn").is_displayed()

    def test_register_with_empty_fields(self, driver, base_url, wait):
        driver.get(f"{base_url}/register.html")
        wait.until(EC.presence_of_element_located((By.ID, "registerBtn"))).click()
        error = wait.until(EC.visibility_of_element_located((By.ID, "errorMsg")))
        assert error.is_displayed()

    def test_register_short_username(self, driver, base_url, wait):
        driver.get(f"{base_url}/register.html")
        wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys("ab")
        driver.find_element(By.ID, "password").send_keys("test123456")
        driver.find_element(By.ID, "confirmPassword").send_keys("test123456")
        driver.find_element(By.ID, "registerBtn").click()
        error = wait.until(EC.visibility_of_element_located((By.ID, "errorMsg")))
        assert error.is_displayed()
        assert "3" in error.text

    def test_register_short_password(self, driver, base_url, wait):
        driver.get(f"{base_url}/register.html")
        wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys("validuser123")
        driver.find_element(By.ID, "password").send_keys("12345")
        driver.find_element(By.ID, "confirmPassword").send_keys("12345")
        driver.find_element(By.ID, "registerBtn").click()
        error = wait.until(EC.visibility_of_element_located((By.ID, "errorMsg")))
        assert error.is_displayed()
        assert "6" in error.text

    def test_register_password_mismatch(self, driver, base_url, wait):
        driver.get(f"{base_url}/register.html")
        wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys("mismatchuser")
        driver.find_element(By.ID, "password").send_keys("test123456")
        driver.find_element(By.ID, "confirmPassword").send_keys("different1")
        driver.find_element(By.ID, "registerBtn").click()
        error = wait.until(EC.visibility_of_element_located((By.ID, "errorMsg")))
        assert error.is_displayed()
        assert "一致" in error.text

    def test_register_success_redirect(self, driver, base_url, wait):
        username = f"sel_reg_{uuid.uuid4().hex[:8]}"
        driver.execute_script("localStorage.clear();")
        driver.get(f"{base_url}/register.html")
        wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys(username)
        driver.find_element(By.ID, "password").send_keys("test123456")
        driver.find_element(By.ID, "confirmPassword").send_keys("test123456")
        driver.find_element(By.ID, "registerBtn").click()
        wait.until(EC.url_contains("index.html"))
        assert "index.html" in driver.current_url

    def test_register_link_to_login(self, driver, base_url, wait):
        driver.execute_script("localStorage.clear();")
        driver.get(f"{base_url}/register.html")
        link = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".auth-footer a")))
        assert "login.html" in link.get_attribute("href")
        link.click()
        wait.until(EC.url_contains("login.html"))
        assert "login.html" in driver.current_url
