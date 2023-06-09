import unittest

from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

from test_data.SampleToDoList import SampleToDoList


class FunctionalTests(unittest.TestCase):
    CHROME_DRIVER_PATH = "./ChromeWebDriver"
    MAIN_PAGE_ADDRESS = "http://localhost:8000"
    WEB_WAIT_TIME_IN_SEC = 3

    def set_up_new_session_headless_mode(self):
        options = Options()
        options.headless = True
        service = Service(executable_path=self.CHROME_DRIVER_PATH)
        self.browser = webdriver.Chrome(service=service, options=options)
        self.browser.implicitly_wait(self.WEB_WAIT_TIME_IN_SEC)

    def setUp(self):
        options = Options()
        options.headless = False
        service = Service(executable_path=self.CHROME_DRIVER_PATH)
        self.browser = webdriver.Chrome(service=service, options=options)
        self.browser.implicitly_wait(self.WEB_WAIT_TIME_IN_SEC)

    def tearDown(self):
        self.browser.quit()

    def test_main_webpage_title(self):
        expected_web_title = "To do list"
        self.browser.get(self.MAIN_PAGE_ADDRESS)
        self.assertIn(expected_web_title, self.browser.title)

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

    def test_write_thing_to_do_and_check_if_they_appear_on_webpage(self):
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

    def test_check_url_appearance_after_writing(self):
        self.browser.get(self.MAIN_PAGE_ADDRESS)
        input_box = self.browser.find_element(by='xpath', value='//input[@id="id_new_item"]')
        input_box.send_keys(SampleToDoList.get_items_list()[0])
        input_box.send_keys(Keys.ENTER)
        user_list_url = self.browser.current_url
        self.assertRegex(user_list_url, "/lists/.+")

    def test_new_user_does_not_see_previous_user_list(self):
        # first user logs in and submits thing to do
        self.browser.get(self.MAIN_PAGE_ADDRESS)
        input_box = self.browser.find_element(by='xpath', value='//input[@id="id_new_item"]')
        input_box.send_keys(SampleToDoList.get_items_list()[0])
        input_box.send_keys(Keys.ENTER)
        first_user_list_url = self.browser.current_url

        # new user logs in, check if there is no trace after previous user
        self.browser.quit()
        # self.set_up_new_session_headless_mode()  # does it work? yes
        self.setUp()
        self.browser.get(self.MAIN_PAGE_ADDRESS)
        page_content_text = self.browser.find_element(by='xpath', value='//body').text
        self.assertNotIn(page_content_text, SampleToDoList.get_items_list()[0])
        self.assertNotIn(page_content_text, SampleToDoList.get_items_list()[1])

        # new user types his thing to do:
        input_box = self.browser.find_element(by='xpath', value='//input[@id="id_new_item"]')
        additional_item_to_do = "Buy Milk"
        input_box.send_keys(additional_item_to_do)
        input_box.send_keys(Keys.ENTER)

        # check if there is new user url and no trace from previous user
        second_user_list_url = self.browser.current_url
        page_content_text = self.browser.find_element(by='xpath', value='//body').text
        self.assertRegex(second_user_list_url, "/lists/.+")
        self.assertNotEqual(first_user_list_url, second_user_list_url)
        self.assertIn(additional_item_to_do, page_content_text)
        self.assertNotIn(page_content_text, SampleToDoList.get_items_list()[0])

    def test_layout_and_styling(self):
        self.browser.get(self.MAIN_PAGE_ADDRESS)
        window_width, window_height = 1024, 768
        self.browser.set_window_size(window_width, window_height)

        input_box = self.browser.find_element(By.ID, value="id_new_item")
        # input_box.send_keys("testing\n")

        print(f"MK Location: {input_box.location}")
        # check if input box is centered
        self.assertAlmostEqual(
            input_box.location["x"] + input_box.size["width"] / 2,
            window_width / 2,
            delta=7
        )

    # test_ability_to_write_list
    # check_website_update_after_submitting_items
    # check_web_behavior_after_another_item


if __name__ == '__main__':
    unittest.main()
