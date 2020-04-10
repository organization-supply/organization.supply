import datetime

import pytz
from django.core.management.base import BaseCommand, CommandError
from django.template.loader import render_to_string

from organization.models.notifications import NotificationFactory
from user.models import User


class Command(BaseCommand):
    """
    Cycles through all users to see if there are recent signups (ie: last week)
    If there are , we generate notifications for them...
    """

    def __init__(self, *args, **kwargs):
        # Should we render these to include URLS etc?
        self.MESSAGES = [
            {
                "title": "Welcome to organization.supply!",
                "template": "notifications/messages/welcome_1.html",
            },
            {
                "title": "Check out the products you can create",
                "template": "notifications/messages/welcome_2_products.html",
            },
            {
                "title": "An introduction on locations",
                "template": "notifications/messages/welcome_3_locations.html",
            },
            {
                "title": "Almost every page has a small information tooltip.",
                "template": "notifications/messages/welcome_4_information.html",
            },
            {
                "title": "Mutations are a way to keep track of inventory.",
                "template": "notifications/messages/welcome_5_mutations.html",
            },
            {
                "title": "Manage your preferences in settings.",
                "template": "notifications/messages/welcome_6_settings.html",
            },
            {
                "title": "Have a look at your reports",
                "template": "notifications/messages/welcome_7_reports.html",
            },
            {
                "title": "Shortcut support",
                "template": "notifications/messages/welcome_8_shortcuts.html",
            },
        ]
        super().__init__(*args, **kwargs)  # Init base command

    def get_user_joined_since(self, joined_since):
        return User.objects.filter(date_joined__gte=joined_since)

    def get_template(self, day):
        return self.MESSAGES[day]

    def handle(self, *args, **options):
        # Get all users we can notify..
        since = datetime.datetime.today().replace(tzinfo=pytz.utc) - datetime.timedelta(
            days=len(self.MESSAGES)
        )
        users_to_notify = self.get_user_joined_since(since)
        self.stdout.write(
            self.style.SUCCESS(
                "Found {} user to notify with an introduction".format(
                    len(users_to_notify)
                )
            )
        )

        # Generate a notification for each user:
        for user in users_to_notify:

            # Get the current day since signup
            days_since_signup = (
                datetime.datetime.today().replace(tzinfo=pytz.utc) - user.date_joined
            ).days

            # Get the corresponding notification
            template = self.get_template(days_since_signup)

            self.stdout.write(self.style.SUCCESS(user.email))

            if template:
                NotificationFactory().for_user(user).send_notification(
                    title=template["title"],
                    sender=user,
                    user=user,
                    template=template["template"],
                )
