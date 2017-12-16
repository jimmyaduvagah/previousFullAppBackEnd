import json


class BaseObject:
    def __init__(self, data={}):
        if data:
            kwargs = data
            for k in kwargs:
                self.__setattr__(k, kwargs[k])

    def __to_dict__(self):
        obj = {}
        keys = dir(self)
        for key in keys:
            if not key.startswith('__'):
                value = self.__getattribute__(key)
                if value is not None:
                    if isinstance(value, str) or isinstance(value, int) or isinstance(value, dict) or isinstance(value, list) or isinstance(value, float) or isinstance(value, bool):
                        obj[key] = value
                    else:
                        obj[key] = value.__to_dict__()

        return obj

    def __to_json__(self):
        return json.dumps(self.__to_dict__())


class IonicPushToken(BaseObject):
    app_id = None
    created = None
    id = None
    invalidated = None
    token = None
    type = None
    valid = None


class IonicPushMessage(BaseObject):
    created = None
    error = None
    notification_id = None
    status = None
    token = IonicPushToken
    user_id = None
    uuid = None

    def __init__(self, data={}):
        if data:
            kwargs = data
            for k in kwargs:
                if k == 'token':
                    self.__setattr__(k, IonicPushToken(kwargs[k]))
                else:
                    self.__setattr__(k, kwargs[k])


class IonicPushNotificationConfigAndroid(BaseObject):
    collapse_key = None
    content_available = None
    data = None
    delay_while_idle = None
    icon = None
    image = None
    message = None
    payload = None
    sound = None
    tag = None
    template_defaults = None
    time_to_live = None
    title = None


class IonicPushNotificationConfigIOS(BaseObject):
    badge = None
    content_available = None
    data = None
    expire = None
    message = None
    payload = None
    priority = None
    sound = None
    template_defaults = None
    title = None


class IonicPushNotificationConfigNotification(BaseObject):
    android = IonicPushNotificationConfigAndroid
    ios = IonicPushNotificationConfigIOS
    message = None
    payload = None
    title = None

    def __init__(self, data={}):
        if data:
            kwargs = data
            for k in kwargs:
                if k == 'ios':
                    self.__setattr__(k, IonicPushNotificationConfigIOS(kwargs[k]))
                elif k == 'android':
                    self.__setattr__(k, IonicPushNotificationConfigAndroid(kwargs[k]))
                else:
                    self.__setattr__(k, kwargs[k])


class IonicPushNotificationConfig(BaseObject):
    notification = IonicPushNotificationConfigNotification
    query = None
    profile = None
    send_to_all = None

    def __init__(self, data={}):
        if data:
            kwargs = data
            for k in kwargs:
                if k == 'notification':
                    self.__setattr__(k, IonicPushNotificationConfigNotification(kwargs[k]))
                else:
                    self.__setattr__(k, kwargs[k])


class IonicPushNotification(BaseObject):
    app_id = None
    config = IonicPushNotificationConfig
    created = None
    overview = None
    state = None
    status = None

    def __init__(self, data={}):
        if data:
            kwargs = data
            for k in kwargs:
                if k == 'config':
                    self.__setattr__(k, IonicPushNotificationConfig(kwargs[k]))
                else:
                    self.__setattr__(k, kwargs[k])
