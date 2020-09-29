from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

# Create your tests here.
class TestTest(LiveServerTestCase):
    
    def setUp(self):
        self.selenium = webdriver.Chrome()
        super(TestTest, self).setUp()

    def tearDown(self):
        self.selenium.quit()
        super(TestTest, self).tearDown()

    def testlogin(self):
        selenium = self.selenium
        #Opening the link we want to test
        selenium.get('http://127.0.0.1:8000/nasrulhifz/')
        username_field = selenium.find_element_by_id('id_username')
        password_field = selenium.find_element_by_id('id_password')
        submit_button = selenium.find_element_by_class_name('btn')

        username_field.send_keys('aimanuslim@gmail.com')
        password_field.send_keys('chanayya211')
        submit_button.click()


        self.assertTrue("Surah List" in selenium.page_source)