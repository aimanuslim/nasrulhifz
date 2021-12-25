import random

from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait as wait


# reminder: django only sees functions started with  test or has Test in it to be test functions.

# Create your tests here.
class TestBase(LiveServerTestCase):
    def open(self, url):
        self.wd.get("%s%s" % (self.live_server_url, url))

    def setUp(self):
        self.wd = webdriver.Chrome()
        super(TestBase, self).setUp()

    def tearDown(self):
        self.wd.quit()
        super(TestBase, self).tearDown()

    def clickFirstSurah(self):
        list_of_surah = self.wd.find_elements_by_class_name('list-group-item-action')

        first_surah = list_of_surah[0]
        first_surah.click()


class LoginTest(TestBase):
    def login(self, username, password):
        # Opening the link we want to test
        self.wd.get('http://127.0.0.1:8000/nasrulhifz/')
        username_field = self.wd.find_element_by_id('id_username')
        password_field = self.wd.find_element_by_id('id_password')
        submit_button = self.wd.find_element_by_class_name('btn')

        username_field.send_keys(username)
        password_field.send_keys(password)
        submit_button.click()

    def loginValid(self):
        self.login('aimanuslim@gmail.com', 'chanayya211')

    def loginInvalid(self):
        self.login('aimanuslim@gmail.com', 'datata')

    def testLogin(self):
        self.loginValid()
        self.assertTrue("Surah List" in self.wd.page_source)

    def testLoginInvalid(self):
        self.loginInvalid()
        self.assertTrue("Your username and password didn't match" in self.wd.page_source)


class AyatDisplayTest(LoginTest):
    def testAyatDisplay(self):
        self.loginValid()
        self.clickFirstSurah()

        list_of_ayat_rows = self.wd.find_elements_by_tag_name('td')
        ayat_row = list_of_ayat_rows[0]
        ayat_row.click()

        wait(self.wd, 10)

        canvas = self.wd.find_element_by_id('myCanvas')


class AyatListTest(LoginTest):
    def getFirstCheckboxAndTick(self) -> int:
        checkboxes = self.wd.find_elements_by_name('ayat_number')
        first_checkbox = checkboxes[0]
        first_checkbox.click()
        return int(first_checkbox.get_attribute('value'))

    def clickUpdateButton(self):
        updateButton = self.wd.find_element_by_class_name('btn-success')
        updateButton.click()

    def clickDeleteButton(self):
        deleteButton = self.wd.find_element_by_name('delete')
        deleteButton.click()

    def clickMultipleAyat(self):
        checkboxes = self.wd.find_elements_by_name('ayat_number')
        # checkboxes_count = len(checkboxes)
        deleted_ayat_numbers = []
        if len(checkboxes) > 2:
            to_select_checkboxes = random.sample(checkboxes, 2)
            for checkbox in to_select_checkboxes:
                checkbox.click()
                deleted_ayat_numbers.append(int(checkbox.get_attribute('value')))
        return deleted_ayat_numbers

    def testTickRefreshAndUpdate(self):
        self.loginValid()
        self.clickFirstSurah()
        self.getFirstCheckboxAndTick()
        self.clickUpdateButton()
        trs = self.wd.find_elements_by_tag_name("tr")  # all rows
        first_tr = trs[1]
        tds = first_tr.find_elements_by_css_selector("*")
        has_0_days = False
        for td in tds:
            if "0 days" in td.text: has_0_days = True

        self.assertTrue(has_0_days)
        # TODO: test delete and check removed (single)

    def testDeleteAyat(self):
        self.loginValid()
        self.clickFirstSurah()
        deleted_ayat_number = self.getFirstCheckboxAndTick()
        self.clickDeleteButton()
        trs = self.wd.find_elements_by_tag_name("tr")  # all rows
        for tr in trs[1:]:  # exclude header row
            tds = tr.find_elements_by_css_selector("*")
            ayat_number_data = tds[0]
            assert deleted_ayat_number != int(ayat_number_data.text)

    def testDeleteMultipleAyat(self):
        self.loginValid()
        self.clickFirstSurah()
        deleted_ayat_numbers = self.clickMultipleAyat()
        self.clickDeleteButton()
        trs = self.wd.find_elements_by_tag_name("tr")  # all rows
        for tr in trs[1:]:  # exclude header row
            tds = tr.find_elements_by_css_selector("*")
            ayat_number_data = tds[0]
            assert int(ayat_number_data.text) not in deleted_ayat_numbers

    def testClickBackButtonFromAyatList(self):
        self.loginValid()
        self.clickFirstSurah()
        back_button = self.wd.find_element_by_name("back")
        back_button.click()
        assert self.wd.find_elements_by_xpath("//*[contains(text(), 'Surah List')]")

    def testClickBackButtonFromAyatDetails(self):
        self.loginValid()
        self.clickFirstSurah()
        first_row = self.wd.find_elements_by_tag_name("tr")[1]
        first_cell = first_row.find_elements_by_css_selector("*")[0]
        first_cell.click()
        back_button = self.wd.find_element_by_name("back")
        back_button.click()
        assert "ayats" in self.wd.current_url

# TODO: test sorting
# TODO: test delete with no checked boxes
