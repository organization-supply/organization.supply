import datetime 
import pytz

from django.core.management.base import BaseCommand, CommandError
from django.template.loader import render_to_string
from organization.models.notifications import notify
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
                "template": "notifications/messages/welcome_1.txt"
            },
            {
                "title": "Check out the products you can create.",
                "template": "notifications/messages/welcome_2_products.txt"
            },
            {
                "title": "Check out locations you can create.",
                "template": "notifications/messages/welcome_3_locations.txt"
            },
            {
                "title": "Almost every page has a small information tooltip. Have a look around!",
                "template": "notifications/messages/welcome_4_information.txt"
            },
            {
                "title": "Mutations are a way to keep track of inventory.",
                "template": "notifications/messages/welcome_5_mutations.txt"
            },
            {
                "title": "You an turn the notification by email or other off in your user settings.",
                "template": "notifications/messages/welcome_6_settings.txt"
            },
            {
                "title": "You an turn the notification by email or other off in your user settings.",
                "template": "notifications/messages/welcome_7_reports.txt"
            }
        ]
        super().__init__(*args, **kwargs) # Init base command

    def get_user_joined_since(self, joined_since):
        return User.objects.filter(date_joined__gte=joined_since)

    def get_message(self, day):
        self.stdout.write(self.style.SUCCESS(day))
        return self.MESSAGES[day]

    def handle(self, *args, **options):
        # Get all users we can notify..
        week_ago = datetime.datetime.today().replace(tzinfo=pytz.utc) - datetime.timedelta(days=7)
        users_to_notify = self.get_user_joined_since(week_ago)
        self.stdout.write(self.style.SUCCESS('Found {} user to notify with an introduction'.format(len(users_to_notify))))

        # Generate a notification for each user:
        for user in users_to_notify:
            
    
            # Get the current day since signup
            days_since_signup = (datetime.datetime.today().replace(tzinfo=pytz.utc) - user.date_joined).days

            # Get the corresponding notification
            message = self.get_message(days_since_signup)
            
            description = render_to_string(
                message['template'],
                {} 
            )

            self.stdout.write(self.style.SUCCESS(user.email))

            if message:  # and user.email_settings enabled or something
                notify.send(
                    sender=user, 
                    user=user, 
                    organization=None,
                    title=message['title'], 
                    description=description
                )
