from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from hc.api.models import Check

class CheckModelTestCase(TestCase):
    def test_it_strips_tags(self):
        '''
        tests for tags
        '''
        check = Check()
        check.tags = " foo  bar "
        self.assertEquals(check.tags_list(), ["foo", "bar"])

    # Test for empty string
    def test_it_returns_an_empty_list(self):
        '''
        tests for empty string
        '''
        check = Check()
        check.tags = ""
        self.assertEquals(check.tags_list(), [])

    def test_status_works_with_grace_period(self):
        '''
        Checks if the status works within the grace period.
        '''
        check = Check()
        check.status = "up"
        check.last_ping = timezone.now() - timedelta(days=1, minutes=30)
        self.assertTrue(check.in_grace_period())
        self.assertEqual(check.get_status(), "up")

    def test_paused_check_is_not_in_grace_period(self):
        '''
        Checks if status paused its not in grace period.
        '''
        check = Check()
        check.status = "up"
        check.last_ping = timezone.now() - timedelta(days=1, minutes=30)
        self.assertTrue(check.in_grace_period())
        check.status = "paused"
        self.assertFalse(check.in_grace_period())

    #Test that when a new check is created, it is not in the grace periodd
    def test_new_check_is_not_in_grace_period(self):
        '''
        Checks new check is not in grace period.
        '''
        check = Check()
        check.status = "new"
        check.last_ping = timezone.now()
        self.assertFalse(check.in_grace_period())
