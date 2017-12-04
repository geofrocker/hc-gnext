from django.core import mail
from django.core.urlresolvers import reverse

from hc.test import BaseTestCase
from hc.accounts.models import Member
from hc.api.models import Check


class ProfileTestCase(BaseTestCase):

    def test_it_sends_set_password_link(self):
        """
        Test set password link is sent to user email.
        """

        self.client.login(username="alice@example.org", password="password")

        form = {"set_password": "1"}
        r = self.client.post("/accounts/profile/", form)
        assert r.status_code == 302

        # profile.token should be set now
        self.alice.profile.refresh_from_db()
        token = self.alice.profile.token

        # Todo Assert that the token is set
        self.assertIsNotNone(token)
        self.assertGreater(len(token), 0)

        # Todo Assert that the email was sent and check email content
        self.assertIn('set_password_link', r.context)

        link = r.context['set_password_link']
        outbox = mail.outbox

        self.assertGreater(len(outbox), 0)
        self.assertIn(link, outbox[0].body)

    def test_it_sends_report(self):
        """
        Test check report is sent user via email.
        """

        check = Check(name="Test Check", user=self.alice)
        check.save()

        self.alice.profile.send_report()

        # Todo Assert that the email was sent and check email content
        outbox = mail.outbox

        self.assertGreater(len(outbox), 0)
        self.assertIsNot(outbox[0].body, "")  # should not be empty.
        self.assertIn(
            'This is a monthly report sent by healthchecks.io.',
            outbox[0].body)

    def test_it_adds_team_member(self):
        """
        Test user is added to created team via an invite.
        """

        self.client.login(username="alice@example.org", password="password")

        form = {"invite_team_member": "1", "email": "frank@example.org"}
        r = self.client.post("/accounts/profile/", form)
        assert r.status_code == 200

        member_emails = set()
        for member in self.alice.profile.member_set.all():
            member_emails.add(member.user.email)

        # Todo Assert the existence of the member emails
        self.assertGreater(len(member_emails), 0)

        self.assertTrue("frank@example.org" in member_emails)

        # Todo Assert that the email was sent and check email content
        # expected subject message.
        subject = 'You have been invited to join ' \
                  '%(email)s on healthchecks.io' % dict(email=self.alice.email)
        outbox = mail.outbox

        self.assertGreater(len(outbox), 0)
        self.assertTrue(
            outbox[0].subject == subject)
        self.assertIn(self.alice.email, outbox[0].body)

    def test_add_team_member_checks_team_access_allowed_flag(self):
        """
        Test users with team access privileges can invite team members.
        """

        self.client.login(username="charlie@example.org", password="password")

        form = {"invite_team_member": "1", "email": "frank@example.org"}
        r = self.client.post("/accounts/profile/", form)
        assert r.status_code == 403

    def test_it_removes_team_member(self):
        """
        Test team owners can remove team members.
        """

        self.client.login(username="alice@example.org", password="password")

        form = {"remove_team_member": "1", "email": "bob@example.org"}
        r = self.client.post("/accounts/profile/", form)
        assert r.status_code == 200

        self.assertEqual(Member.objects.count(), 0)

        self.bobs_profile.refresh_from_db()
        self.assertEqual(self.bobs_profile.current_team, None)

    def test_it_sets_team_name(self):
        """
        Test team owner can set team name.
        """

        self.client.login(username="alice@example.org", password="password")

        form = {"set_team_name": "1", "team_name": "Alpha Team"}
        r = self.client.post("/accounts/profile/", form)
        assert r.status_code == 200

        self.alice.profile.refresh_from_db()
        self.assertEqual(self.alice.profile.team_name, "Alpha Team")

    def test_set_team_name_checks_team_access_allowed_flag(self):
        """
        Test team name can only be set with users with team access privilege.
        """

        self.client.login(username="charlie@example.org", password="password")

        form = {"set_team_name": "1", "team_name": "Charlies Team"}
        r = self.client.post("/accounts/profile/", form)
        assert r.status_code == 403

    def test_it_switches_to_own_team(self):
        """
        Test user's team is switched to default.
        """

        self.client.login(username="bob@example.org", password="password")

        self.client.get("/accounts/profile/")
        # After visiting the profile page, team should be switched back
        # to user's default team.
        self.bobs_profile.refresh_from_db()
        self.assertEqual(self.bobs_profile.current_team, self.bobs_profile)

    def test_it_shows_badges(self):
        """
        Test users should be able to see badges.
        """

        self.client.login(username="alice@example.org", password="password")
        Check.objects.create(user=self.alice, tags="foo a-B_1  baz@")
        Check.objects.create(user=self.bob, tags="bobs-tag")

        r = self.client.get("/accounts/profile/")
        self.assertContains(r, "foo.svg")
        self.assertContains(r, "a-B_1.svg")

        # Expect badge URLs only for tags that match \w+
        self.assertNotContains(r, "baz@.svg")

        # Expect only Alice's tags
        self.assertNotContains(r, "bobs-tag.svg")

    # Todo Test it creates and revokes API key
    def test_user_can_create_and_revoke_api(self):
        """
        Test user should be able to create and revoke API keys.
        """

        # login charlie.
        self.client.login(username=self.charlie.email, password='password')
        form = {'create_api_key': "1"}

        response = self.client.post(reverse('hc-profile'), form)

        # assert API key is created.
        self.assertIs(response.status_code, 200)
        self.assertContains(response, "The API key has been created!")

        self.charlie.profile.refresh_from_db()

        # # check API key now actually exists in Charlie profile.
        self.assertIsNot(self.charlie.profile.api_key, "")

        # revoke API key.
        form = {'revoke_api_key': "1"}
        response = self.client.post(reverse('hc-profile'), form)

        self.charlie.profile.refresh_from_db()

        self.assertContains(response, 'The API key has been revoked!')
        self.assertTrue(self.charlie.profile.api_key == "")  # name.
