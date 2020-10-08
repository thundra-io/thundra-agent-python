from django.http import HttpResponse


def index(request):
    return HttpResponse("Test!", status=200)


def view_with_error(request):
    raise Exception("Error")


def repath_view(request):
    return HttpResponse(status=200)
