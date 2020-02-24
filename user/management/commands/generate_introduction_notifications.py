import datetime
import os

from django.core.management.base import BaseCommand, CommandError

from user.models import User


class Command(BaseCommand):
    """
    Cycles through all users to see if there are recent signups (ie: last week)
    If there are , we generate notifications for them...
    """

    def __init__(self, *args, **kwargs):
        self.MESSAGES = {
            1: "Welcome to organization.supply!",
            2: "Check out the products and locations you can create.",
            3: "Almost every page has a small information tooltip. Have a look around!",
            4: "Mutations are a way to keep track of inventory.",
            # TODO: add more and test these...
            5: "You an turn the notification by email or other off in your user settings.",
        }

    def get_recent_users(self):
        return []

    def get_message(self, day):
        return self.MESSAGES[day]

    def run(self):
        users_to_notify = self.get_recent_users()
        for user in users_to_notify:
            days_since_signup = user.created - datetime.date.today()
            notication_verb = get_message(days_since_signup)
            if notication_verb:  # and user.email_settings enabled or something
                pass
                # TODO notify (and keep a log somewhere?)
