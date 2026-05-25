import uuid
import time
import sys

from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "http://localhost:8000"
passed = 0
failed = 0
errors = []


def log_pass(name):
    global passed
    passed += 1
    print(f"  [PASS] {name}")


def log_fail(name, detail=""):
    global failed
    failed += 1
    errors.append(f"{name}: {detail}")
    print(f"  [FAIL] {name} - {detail}")


def run_tests():
    global passed, failed, errors
    options = Options()
    options.add_argument("--window-size=1280,800")
    service = Service()
    driver = webdriver.Edge(service=service, options=options)
    driver.implicitly_wait(5)
    wait = WebDriverWait(driver, 10)

    try:
        print("\n===== 登录页面测试 =====\n")

        driver.get(f"{BASE_URL}/login.html")
        time.sleep(0.5)
        driver.execute_script("localStorage.clear();")

        try:
            driver.get(f"{BASE_URL}/login.html")
            title = wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
            assert "PCB缺陷检测" in title.text
            log_pass("登录页加载")
        except Exception as e:
            log_fail("登录页加载", str(e)[:80])

        try:
            driver.get(f"{BASE_URL}/login.html")
            wait.until(EC.presence_of_element_located((By.ID, "username")))
            assert driver.find_element(By.ID, "username").is_displayed()
            assert driver.find_element(By.ID, "password").is_displayed()
            assert driver.find_element(By.ID, "loginBtn").is_displayed()
            log_pass("登录表单元素可见")
        except Exception as e:
            log_fail("登录表单元素可见", str(e)[:80])

        try:
            driver.execute_script("localStorage.clear();")
            driver.get(f"{BASE_URL}/login.html")
            wait.until(EC.presence_of_element_located((By.ID, "loginBtn"))).click()
            error = wait.until(EC.visibility_of_element_located((By.ID, "errorMsg")))
            assert "请输入" in error.text
            log_pass("空字段提交显示错误")
        except Exception as e:
            log_fail("空字段提交显示错误", str(e)[:80])

        try:
            driver.execute_script("localStorage.clear();")
            driver.get(f"{BASE_URL}/login.html")
            wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys("wronguser_xyz")
            driver.find_element(By.ID, "password").send_keys("wrongpass123")
            driver.find_element(By.ID, "loginBtn").click()
            error = wait.until(EC.visibility_of_element_located((By.ID, "errorMsg")))
            assert error.is_displayed()
            log_pass("错误凭据登录失败")
        except Exception as e:
            log_fail("错误凭据登录失败", str(e)[:80])

        try:
            driver.execute_script("localStorage.clear();")
            driver.get(f"{BASE_URL}/login.html")
            link = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".auth-footer a")))
            link.click()
            wait.until(EC.url_contains("register.html"))
            assert "register.html" in driver.current_url
            log_pass("登录页跳转注册页")
        except Exception as e:
            log_fail("登录页跳转注册页", str(e)[:80])

        print("\n===== 注册页面测试 =====\n")

        try:
            driver.execute_script("localStorage.clear();")
            driver.get(f"{BASE_URL}/register.html")
            title = wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
            assert "PCB缺陷检测" in title.text
            log_pass("注册页加载")
        except Exception as e:
            log_fail("注册页加载", str(e)[:80])

        try:
            driver.get(f"{BASE_URL}/register.html")
            wait.until(EC.presence_of_element_located((By.ID, "username")))
            assert driver.find_element(By.ID, "username").is_displayed()
            assert driver.find_element(By.ID, "password").is_displayed()
            assert driver.find_element(By.ID, "confirmPassword").is_displayed()
            assert driver.find_element(By.ID, "registerBtn").is_displayed()
            log_pass("注册表单元素可见")
        except Exception as e:
            log_fail("注册表单元素可见", str(e)[:80])

        try:
            driver.execute_script("localStorage.clear();")
            driver.get(f"{BASE_URL}/register.html")
            wait.until(EC.presence_of_element_located((By.ID, "registerBtn"))).click()
            error = wait.until(EC.visibility_of_element_located((By.ID, "errorMsg")))
            assert error.is_displayed()
            log_pass("空字段注册显示错误")
        except Exception as e:
            log_fail("空字段注册显示错误", str(e)[:80])

        try:
            driver.execute_script("localStorage.clear();")
            driver.get(f"{BASE_URL}/register.html")
            wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys("ab")
            driver.find_element(By.ID, "password").send_keys("test123456")
            driver.find_element(By.ID, "confirmPassword").send_keys("test123456")
            driver.find_element(By.ID, "registerBtn").click()
            error = wait.until(EC.visibility_of_element_located((By.ID, "errorMsg")))
            assert "3" in error.text
            log_pass("短用户名注册显示错误")
        except Exception as e:
            log_fail("短用户名注册显示错误", str(e)[:80])

        try:
            driver.execute_script("localStorage.clear();")
            driver.get(f"{BASE_URL}/register.html")
            wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys("validuser123")
            driver.find_element(By.ID, "password").send_keys("12345")
            driver.find_element(By.ID, "confirmPassword").send_keys("12345")
            driver.find_element(By.ID, "registerBtn").click()
            error = wait.until(EC.visibility_of_element_located((By.ID, "errorMsg")))
            assert "6" in error.text
            log_pass("短密码注册显示错误")
        except Exception as e:
            log_fail("短密码注册显示错误", str(e)[:80])

        try:
            driver.execute_script("localStorage.clear();")
            driver.get(f"{BASE_URL}/register.html")
            wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys("mismatchuser")
            driver.find_element(By.ID, "password").send_keys("test123456")
            driver.find_element(By.ID, "confirmPassword").send_keys("different1")
            driver.find_element(By.ID, "registerBtn").click()
            error = wait.until(EC.visibility_of_element_located((By.ID, "errorMsg")))
            assert "一致" in error.text
            log_pass("密码不一致注册显示错误")
        except Exception as e:
            log_fail("密码不一致注册显示错误", str(e)[:80])

        username = f"vis_test_{uuid.uuid4().hex[:8]}"
        try:
            driver.execute_script("localStorage.clear();")
            driver.get(f"{BASE_URL}/register.html")
            wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys(username)
            driver.find_element(By.ID, "password").send_keys("test123456")
            driver.find_element(By.ID, "confirmPassword").send_keys("test123456")
            driver.find_element(By.ID, "registerBtn").click()
            wait.until(EC.url_contains("index.html"))
            log_pass("注册成功跳转首页")
        except Exception as e:
            log_fail("注册成功跳转首页", str(e)[:80])

        try:
            driver.execute_script("localStorage.clear();")
            driver.get(f"{BASE_URL}/login.html")
            wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys(username)
            driver.find_element(By.ID, "password").send_keys("test123456")
            driver.find_element(By.ID, "loginBtn").click()
            wait.until(EC.url_contains("index.html"))
            log_pass("登录成功跳转首页")
        except Exception as e:
            log_fail("登录成功跳转首页", str(e)[:80])

        try:
            driver.execute_script("localStorage.clear();")
            driver.get(f"{BASE_URL}/register.html")
            link = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".auth-footer a")))
            link.click()
            wait.until(EC.url_contains("login.html"))
            log_pass("注册页跳转登录页")
        except Exception as e:
            log_fail("注册页跳转登录页", str(e)[:80])

    finally:
        driver.quit()

    print(f"\n===== 测试结果 =====\n")
    print(f"  通过: {passed}")
    print(f"  失败: {failed}")
    if errors:
        print(f"\n  失败详情:")
        for e in errors:
            print(f"    - {e}")
    print()
    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
