from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import unittest
from test_data.SampleToDoList import SampleToDoList


class FunctionalTests(unittest.TestCase):
    CHROME_DRIVER_PATH = "../ChromeWebDriver"
    MAIN_PAGE_ADDRESS = "http://localhost:8000"
    WEB_WAIT_TIME_IN_SEC = 3

    def setUp(self):
        options = Options()
        options.headless = True
        service = Service(executable_path=self.CHROME_DRIVER_PATH)
        self.browser = webdriver.Chrome(service=service, options=options)
        self.browser.implicitly_wait(self.WEB_WAIT_TIME_IN_SEC)

    def tearDown(self):
        self.browser.quit()

    def test_main_webpage_title(self):
        expected_web_title = "To do list"
        self.browser.get(self.MAIN_PAGE_ADDRESS)
        self.assertIn(expected_web_title, self.browser.title)
        # self.fail("End of test execution")

    def test_main_webpage_content(self):
        expected_header_title = "Lists"
        self.browser.get(self.MAIN_PAGE_ADDRESS)
        header_text = self.browser.find_element(by='xpath', value='//h1').text
        self.assertIn(expected_header_title, header_text)

    def test_proper_placeholder_on_page(self):
        self.browser.get(self.MAIN_PAGE_ADDRESS)
        input_box = self.browser.find_element(by='xpath', value='//input[@id="id_new_item"]')
        actual_placeholder_text = input_box.get_attribute('placeholder')
        expected_placeholder_text = "Write thing to do"
        self.assertEqual(actual_placeholder_text, expected_placeholder_text)

    def test_write_thing_to_do_and_check_result(self):
        to_do_list = SampleToDoList.get_items_list()
        self.browser.get(self.MAIN_PAGE_ADDRESS)

        for counter, item in enumerate(to_do_list, start=1):
            input_box = self.browser.find_element(by='xpath', value='//input[@id="id_new_item"]')
            input_box.send_keys(item)
            input_box.send_keys(Keys.ENTER)

            table = self.browser.find_element(by='xpath', value='//table[@id="id_list_table"]')
            rows = table.find_elements(by='xpath', value='./tbody/tr')
            expected_text_visible = f"{counter}. {item}"
            self.assertIn(expected_text_visible, [row.text for row in rows],
                          f"no such element: '{expected_text_visible}' in table")

    # test_ability_to_write_list
    # check_website_update_after_submitting_items
    # check_web_behavior_after_another_item


if __name__ == '__main__':
    unittest.main()
