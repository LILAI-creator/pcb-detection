import uuid
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TestLoginPage:
    def test_login_page_loads(self, driver, base_url, wait):
        driver.execute_script("localStorage.clear();")
        driver.get(f"{base_url}/login.html")
        title = wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        assert "PCB缺陷检测" in title.text

    def test_login_form_elements(self, driver, base_url, wait):
        driver.execute_script("localStorage.clear();")
        driver.get(f"{base_url}/login.html")
        wait.until(EC.presence_of_element_located((By.ID, "username")))
        assert driver.find_element(By.ID, "username").is_displayed()
        assert driver.find_element(By.ID, "password").is_displayed()
        assert driver.find_element(By.ID, "loginBtn").is_displayed()

    def test_login_with_empty_fields(self, driver, base_url, wait):
        driver.execute_script("localStorage.clear();")
        driver.get(f"{base_url}/login.html")
        wait.until(EC.presence_of_element_located((By.ID, "loginBtn"))).click()
        error = wait.until(EC.visibility_of_element_located((By.ID, "errorMsg")))
        assert "请输入" in error.text

    def test_login_with_wrong_credentials(self, driver, base_url, wait):
        driver.execute_script("localStorage.clear();")
        driver.get(f"{base_url}/login.html")
        wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys("wronguser_xyz")
        driver.find_element(By.ID, "password").send_keys("wrongpass123")
        driver.find_element(By.ID, "loginBtn").click()
        error = wait.until(EC.visibility_of_element_located((By.ID, "errorMsg")))
        assert error.is_displayed()

    def test_login_success_redirect(self, driver, base_url, wait):
        username = f"sel_login_{uuid.uuid4().hex[:8]}"
        password = "selTest123456"
        driver.execute_script("localStorage.clear();")
        driver.get(f"{base_url}/register.html")
        wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys(username)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.ID, "confirmPassword").send_keys(password)
        driver.find_element(By.ID, "registerBtn").click()
        wait.until(EC.url_contains("index.html"))
        driver.execute_script("localStorage.clear();")
        driver.get(f"{base_url}/login.html")
        wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys(username)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.ID, "loginBtn").click()
        wait.until(EC.url_contains("index.html"))
        assert "index.html" in driver.current_url

    def test_login_link_to_register(self, driver, base_url, wait):
        driver.execute_script("localStorage.clear();")
        driver.get(f"{base_url}/login.html")
        link = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".auth-footer a")))
        assert "register.html" in link.get_attribute("href")
        link.click()
        wait.until(EC.url_contains("register.html"))
        assert "register.html" in driver.current_url
