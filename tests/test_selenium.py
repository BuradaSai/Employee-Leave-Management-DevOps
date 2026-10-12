
import os
import unittest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


BASE_URL = os.getenv("APP_URL", "http://127.0.0.1:5001")


class LeaveManagementUITests(unittest.TestCase):

    def setUp(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)
        self.driver.get(BASE_URL)

    def tearDown(self):
        if hasattr(self, "driver"):
            self.driver.quit()

    def login(self, username, password):
        self.driver.find_element(By.ID, "username").send_keys(username)
        self.driver.find_element(By.ID, "password").send_keys(password)
        self.driver.find_element(
            By.CSS_SELECTOR, "button[type='submit']"
        ).click()

    def test_employee_login(self):
        self.login("employee1", "emp1123")
        self.wait.until(EC.url_contains("/dashboard"))
        self.assertIn("Welcome, employee1", self.driver.page_source)

    def test_manager_login(self):
        self.login("manager", "mgr123")
        self.wait.until(EC.url_contains("/dashboard"))
        self.assertIn("Welcome, manager", self.driver.page_source)


if __name__ == "__main__":
    unittest.main()
