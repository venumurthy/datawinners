from time import sleep
import unittest
from nose.plugins.attrib import attr
from framework.base_test import setup_driver, teardown_driver
from pages.allsubjectspage.all_subjects_list_page import AllSubjectsListPage
from framework.utils.common_utils import by_id
from pages.allsubjectspage.subjects_page import SubjectsPage
from pages.loginpage.login_page import LoginPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE, url
from tests.alldatasenderstests.all_data_sender_data import random_string
from tests.allsubjectstests.all_subjects_data import SUBJECT_TYPE, SUBJECT_TYPE_WHITE_SPACES, ERROR_MSG_INVALID_ENTRY, SUBJECT_TYPE_SPL_CHARS, SUBJECT_TYPE_BLANK
from tests.logintests.login_data import VALID_CREDENTIALS


@attr('suit_1')
class TestSubjectsPage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.driver = setup_driver()

    @classmethod
    def tearDownClass(cls):
        teardown_driver(cls.driver)

    def check_pagination_size(self, subjects_page, size):
        self.assertTrue(size >= subjects_page.number_of_rows())
        self.assertEqual(size, subjects_page.selected_page_size())


    def add_subject_type(self, entity_type):
        all_subjects_page = SubjectsPage(self.driver)
        all_subjects_page.click_add_a_subject_type_link()
        all_subjects_page.add_entity_type_with(entity_type)


    @attr('functional_test')
    def test_all_subjects_page(self):
        self.login_with(VALID_CREDENTIALS)
        self.driver.go_to(url("/entity/subjects/clinic/"))
        subjects_page = AllSubjectsListPage(self.driver)
        self.check_pagination_size(subjects_page, 25)

        subjects_page.set_page_size(10)
        self.check_pagination_size(subjects_page, 10)

        subjects_page.search("tes")

        self.check_pagination_size(subjects_page, 10)

        sleep(1)
        for row in subjects_page.rows():
            self.assertIn("tes", row.text.lower())


    @attr('functional_test')
    def test_add_duplicate_subjectType(self):
        self.login_with(VALID_CREDENTIALS)
        self.driver.go_to(url("/entity/subjects/"))
        subject_type_name = SUBJECT_TYPE + random_string(3)
        self.add_subject_type(subject_type_name)
        self.validate_subject_type(subject_type_name)
        self.add_subject_type(subject_type_name)

    def validate_error_messages(self,subject_type_name):
        error_msg = self.driver.find(by_id("type_message")).text
        self.assertEquals(error_msg, subject_type_name)

    @attr('functional_test')
    def test_add_invalid_subjectType(self):
        self.login_with(VALID_CREDENTIALS)
        self.driver.go_to(url("/entity/subjects/"))
        self.add_subject_type(SUBJECT_TYPE_WHITE_SPACES)
        self.validate_error_messages(ERROR_MSG_INVALID_ENTRY)
        self.driver.find(by_id("cancel_add_type")).click()
        self.add_subject_type(SUBJECT_TYPE_SPL_CHARS)
        self.validate_error_messages(ERROR_MSG_INVALID_ENTRY)
        self.driver.find(by_id("cancel_add_type")).click()
        self.add_subject_type(SUBJECT_TYPE_BLANK)
        self.validate_error_messages(ERROR_MSG_INVALID_ENTRY)


    def validate_subject_type(self, subject_type):
        element = self.driver.find_element_by_link_text(subject_type).text
        self.assertEquals(element.lower() , subject_type.lower())

    def login_with(self, credential):
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        LoginPage(self.driver).login_with(credential)

