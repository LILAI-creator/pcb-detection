import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TestHistoryPage:
    def test_history_page_requires_login(self, driver, base_url, wait):
        driver.get(f"{base_url}/login.html")
        time.sleep(0.5)
        driver.execute_script("localStorage.clear();")
        driver.get(f"{base_url}/history.html")
        time.sleep(2)
        current = driver.current_url
        assert "login.html" in current

    def test_history_page_loads(self, logged_in_driver, base_url, wait):
        driver = logged_in_driver
        driver.get(f"{base_url}/history.html")
        title = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".card-title")))
        assert "历史记录" in title.text

    def test_history_filter_elements(self, logged_in_driver, base_url, wait):
        driver = logged_in_driver
        driver.get(f"{base_url}/history.html")
        wait.until(EC.presence_of_element_located((By.ID, "filterClass")))
        assert driver.find_element(By.ID, "filterClass").is_displayed()
        assert driver.find_element(By.ID, "filterStartDate").is_displayed()
        assert driver.find_element(By.ID, "btnFilter").is_displayed()
        assert driver.find_element(By.ID, "btnResetFilter").is_displayed()

    def test_history_table_exists(self, logged_in_driver, base_url, wait):
        driver = logged_in_driver
        driver.get(f"{base_url}/history.html")
        wait.until(EC.presence_of_element_located((By.ID, "historyBody")))
        tbody = driver.find_element(By.ID, "historyBody")
        assert tbody.is_displayed()

    def test_history_filter_by_class(self, logged_in_driver, base_url, wait):
        driver = logged_in_driver
        driver.get(f"{base_url}/history.html")
        wait.until(EC.presence_of_element_located((By.ID, "filterClass")))
        select = driver.find_element(By.ID, "filterClass")
        for option in select.find_elements(By.TAG_NAME, "option"):
            if option.get_attribute("value") == "missing_hole":
                option.click()
                break
        driver.find_element(By.ID, "btnFilter").click()
        wait.until(EC.presence_of_element_located((By.ID, "historyBody")))

    def test_history_reset_filter(self, logged_in_driver, base_url, wait):
        driver = logged_in_driver
        driver.get(f"{base_url}/history.html")
        wait.until(EC.presence_of_element_located((By.ID, "btnResetFilter"))).click()
        wait.until(EC.presence_of_element_located((By.ID, "historyBody")))
        select_val = driver.find_element(By.ID, "filterClass").get_attribute("value")
        assert select_val == ""

    def test_history_pagination_exists(self, logged_in_driver, base_url, wait):
        driver = logged_in_driver
        driver.get(f"{base_url}/history.html")
        wait.until(EC.presence_of_element_located((By.ID, "pagination")))
