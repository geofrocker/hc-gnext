from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase
from hc.api.models import Check
from django.urls import reverse
from hc.accounts.forms import EmailPasswordForm


class LoginTestCase(TestCase):
    def setUp(self):
        self.url = reverse('hc-login')
        self.check = Check()
        self.form = {"email": "alice@example.org"}
        alice = User(username="alice", email="alice@example.org")
        alice.set_password("password")
        self.alice = alice

    def test_it_sends_link(self):
        """
        Test login link is sent after login.
        """
        self.check.save()
        session = self.client.session
        session["welcome_code"] = str(self.check.code)
        session.save()

        response = self.client.post(self.url, self.form)
        assert response.status_code == 302

        # Assert that a user was created
        self.assertEqual(User.objects.count(), 1)

        # And email sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Log in to healthchecks.io')

        # Assert contents of the email body
        created_user = User.objects.first()
        self.assertGreater(len(mail.outbox[0].body), 0)
        self.assertIn(created_user.username, mail.outbox[0].body)

        # Assert that check is associated with the new user
        check_user = Check.objects.first().user
        self.assertEqual(check_user.username, created_user.username)

    def test_it_pops_bad_link_from_session(self):
        """
        Test bad_link flag is cleared from the session on GET requests.
        """

        self.client.session["bad_link"] = True
        self.client.get(self.url)
        assert "bad_link" not in self.client.session
        
    # Any other tests?
    def test_login_returns_form_for_get(self):
        """
        Test rendered form is correct.
        """

        response = self.client.get(self.url)
        self.assertTemplateUsed('accounts/login.html')
        self.assertEqual(EmailPasswordForm, response.context['form'].__class__)

    def test_redirect_with_successful_login(self):
        """
        Test user is redirected to checks page on successful login.
        """

        response = self.client.post(self.url, self.form, follow=True)
        self.assertRedirects(response, reverse('hc-login-link-sent'))

    def test_login_with_incorrect_password(self):
        """
        Test error message is shown when user supplies incorrect
        login credentials.
        """
        # create user
        self.alice.save()
        response = self.client.post(self.url, {
            "email": "alice@example.org",
            "password": "wrong-password"
            })
        # bad_credentials should be True in the context
        self.assertTrue(response.context['bad_credentials'])
        self.assertContains(response, 'Incorrect email or password')

    def test_login_link_cannot_be_used_twice(self):
        """
        Test user should use login link only once.
        """

        response = self.client.post(self.url, self.form)
        login_link = response.context['login_link']

        # make first request.
        self.client.post(login_link)

        # logout user.
        self.client.get(reverse('hc-logout'))

        # login again with the same login link.
        response = self.client.post(login_link)
        self.assertRedirects(response, reverse('hc-login'))

    def test_login_with_password(self):
        """
            Test login with email and password supplied in EmailForm
        """
        # create user
        self.alice.save()
        # login with correct password
        response = self.client.post(
            self.url,
            {"email": "alice@example.org", "password": "password"},
            follow=True)
        self.assertRedirects(response, reverse('hc-checks'))
