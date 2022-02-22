from django.conf import settings
from .models import *


def ElectionTitle(request):
    context = {}
    if countDown.objects.exists():
        countdown = countDown.objects.all()[0]
        datetime = countdown.end_time_counter

        year = str(datetime).split("-")[0]
        time = str(datetime).split(" ")[1][:8]
        day = str(datetime).split("-")[2][:2]
        month = str(datetime.strftime("%b"))
        datetime_js = month+' '+day+', '+year+' '+time
        context['countdown'] = countdown
        context['datetime_js'] = datetime_js

    title = "No Title Yet"
    try:
        file = open(settings.ELECTION_TITLE_PATH, 'r')
        title = file.read()
    except:
        pass
    context['TITLE'] = title

    return context
