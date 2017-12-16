import json

from ionic_api.objects import IonicPushToken, IonicPushMessage, IonicPushNotification


class BaseResponse:
    status = None
    _raw = None
    object_class = object

    meta = {
        "status": None,
        "version": None,
        "request_id": None
    }

    def get_raw(self):
        return self._raw


class OKResponse(BaseResponse):
    data = None

    def __init__(self, response):
        if len(response) > 0:
            kwargs = json.loads(response)
            for k in kwargs:
                if k == 'data':
                    self.__setattr__('_raw', kwargs['data'])
                else:
                    self.__setattr__(k, kwargs[k])

            if isinstance(self._raw, list):
                self.data = list()
                for item in self._raw:
                    self.data.append(self.get_object_class(item))
            else:
                self.data = self.get_object_class(self._raw)

    def get_object_class(self, item=None):
        return self.object_class(item)

    def get(self, attr, default=None):
        if self.data[attr]:
            return self.data[attr]
        else:
            return default


class ErrorResponse(BaseResponse):
    error = None

    def __init__(self, response):
        kwargs = json.loads(response)
        for k in kwargs:
            self.__setattr__(k, kwargs[k])


class PushTokenResponse(OKResponse):

    object_class = IonicPushToken


class PushTokenListUsersResponse(OKResponse):

    object_class = object


class PushMessageResponse(OKResponse):

    object_class = IonicPushMessage


class PushNotificationResponse(OKResponse):

    object_class = IonicPushNotification



