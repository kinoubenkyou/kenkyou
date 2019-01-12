from django.contrib.auth.decorators import login_required
from django.http import HttpResponse


def index(request):
    return HttpResponse("Index")
