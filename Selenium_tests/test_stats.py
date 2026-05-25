import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TestStatsPage:
    def test_stats_page_requires_login(self, driver, base_url, wait):
        driver.get(f"{base_url}/login.html")
        time.sleep(0.5)
        driver.execute_script("localStorage.clear();")
        driver.get(f"{base_url}/stats.html")
        time.sleep(2)
        current = driver.current_url
        assert "login.html" in current

    def test_stats_page_loads(self, logged_in_driver, base_url, wait):
        driver = logged_in_driver
        driver.get(f"{base_url}/stats.html")
        title = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".card-title")))
        assert "缺陷类别分布" in title.text

    def test_stats_stat_cards(self, logged_in_driver, base_url, wait):
        driver = logged_in_driver
        driver.get(f"{base_url}/stats.html")
        wait.until(EC.presence_of_element_located((By.ID, "statTotal")))
        assert driver.find_element(By.ID, "statTotal").is_displayed()
        assert driver.find_element(By.ID, "statDefectRate").is_displayed()
        assert driver.find_element(By.ID, "statDefectTotal").is_displayed()
        assert driver.find_element(By.ID, "statTopDefect").is_displayed()

    def test_stats_pie_chart(self, logged_in_driver, base_url, wait):
        driver = logged_in_driver
        driver.get(f"{base_url}/stats.html")
        canvas = wait.until(EC.presence_of_element_located((By.ID, "pieChart")))
        assert canvas.is_displayed()

    def test_stats_line_chart(self, logged_in_driver, base_url, wait):
        driver = logged_in_driver
        driver.get(f"{base_url}/stats.html")
        canvas = wait.until(EC.presence_of_element_located((By.ID, "lineChart")))
        assert canvas.is_displayed()

    def test_stats_bar_chart(self, logged_in_driver, base_url, wait):
        driver = logged_in_driver
        driver.get(f"{base_url}/stats.html")
        canvas = wait.until(EC.presence_of_element_located((By.ID, "barChart")))
        assert canvas.is_displayed()

    def test_stats_values_not_dash(self, logged_in_driver, base_url, wait):
        driver = logged_in_driver
        driver.get(f"{base_url}/stats.html")
        total_el = wait.until(EC.presence_of_element_located((By.ID, "statTotal")))
        assert total_el.text != "-"
