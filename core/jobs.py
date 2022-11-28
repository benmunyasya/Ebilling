import datetime

from io import BytesIO
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from accounts.models import UserNotifications


from django.core.exceptions import ObjectDoesNotExist

from django.template.loader import get_template, render_to_string


from django.shortcuts import HttpResponse



utc = pytz.UTC
get_today = datetime.datetime.now().replace(tzinfo=utc)
def print_hello():
   
    user_notification=UserNotifications.objects.create(message='1 minutes has elapsed')
def start():
    scheduler = BackgroundScheduler()
   
    scheduler.add_job(print_hello, 'interval', minutes=1)
   
    scheduler.start()