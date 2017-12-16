from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response

from ionic_api.request import PushNotificationRequest
from ionic_api.response import ErrorResponse, OKResponse
from twz_server_django.settings_private import IONIC_PUSH_GROUP


def test():
    r = PushNotificationRequest()

    # r.list({
    #     PushTokenRequestOptions.List.PageSize: 1
    # })

    obj = {
        "invalidated": None,
        "created": "2017-06-20T16:22:57.823333+00:00",
        "app_id": "c40b81d6",
        "type": "ios",
        "id": "2159d5685f3da8f9b1b3207b7a8043f9",
        "valid": None,
        "token": "9b1f9b700a1f790ba2cbf015bd3081afbf3bb858f4bcb27eade975d566576514"
    }

    obj = [
        {
            "config": {
                "profile": IONIC_PUSH_GROUP,
                "notification": {
                    "android": {
                        "priority": "high",
                        "message": "Get 150% off!",
                        "title": "Test Push"
                    },
                    "payload": {},
                    "ios": {
                        "sound": "default",
                        "priority": 10,
                        "message": "Get 150% off!",
                        "badge": 0,
                        "content_available": 1,
                        "title": "Test Push"
                    },
                    "message": "Get 150% off!",
                    "title": "Test Push"
                },
                "query": {},
                "send_to_all": True
            },
            "created": "2017-06-20T23:15:10.150312+00:00",
            "state": "enqueued",
            "status": "locked",
            "uuid": "9e16052e-1532-4294-bfcc-ac935c14d29e",
            "app_id": "c40b81d6"
        }
    ]

    r.create({
        "tokens": ['9b1f9b700a1f790ba2cbf015bd3081afbf3bb858f4bcb27eade975d566576514'],
        "notification": {
            "message": "First test from django",
            "title": "The first test from django",
            "payload": {}
        },
        "profile": IONIC_PUSH_GROUP
    })

    # r = PushTokenRequest()
    # r.list()

    to_return = Response(None)
    if isinstance(r.response, ErrorResponse):
        to_return = r.response.error
        print(r.response)
    elif isinstance(r.response, OKResponse):
        to_return = r.response.get_raw()
        print(r.response.data)

    return Response(to_return)
