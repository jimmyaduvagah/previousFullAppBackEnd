from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def test_callback(request):

    raise PermissionError()
