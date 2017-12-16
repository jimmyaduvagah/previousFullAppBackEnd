import hashlib
import json

import requests
from debug_toolbar import settings

from ionic_api.response import OKResponse, ErrorResponse, PushTokenResponse, PushTokenListUsersResponse, \
    PushMessageResponse, PushNotificationResponse
from twz_server_django.settings_private import IONIC_API_TOKEN


class BaseAuthenticatedRequest:
    url = None
    payload = None
    headers = {
        'Content-Type': "application/json"
    }
    response = None
    status = None
    query_parameters = None
    method = 'get'
    pk = None
    response_class = OKResponse

    def __init__(self, **kwargs):
        for k in kwargs:
            self.__setattr__(k, kwargs[k])

    def get_headers(self):
        headers = self.headers
        headers['Authorization'] = "Bearer %s" % self.get_token()
        return headers

    def get_token(self):
        return IONIC_API_TOKEN

    def get_url(self):
        if self.pk:
            return "%s%s/%s" % ('https://api.ionic.io/', self.url, self.get_pk())
        else:
            return "%s%s" % ('https://api.ionic.io/', self.url)

    def get_response_class(self, *args):
        return self.response_class(*args)

    def get_payload(self):
        payload = json.dumps(self.payload)
        # try:
        # except Jsone:
        #     payload = self.payload
        #     print(e)

        return payload

    def get_pk(self):
        return self.pk

    def get_method(self):
        return self.method

    def get_query_parameters(self):
        return self.query_parameters

    def set_query_parameters(self, query_parameters):
        self.query_parameters = query_parameters
        return self.query_parameters

    def fire(self):
        response = getattr(requests, self.get_method())(
            self.get_url(),
            data=self.get_payload(),
            params=self.get_query_parameters(),
            headers=self.get_headers()
        )
        self.status = response.status_code
        print(response.text)
        if str(self.status).startswith('2'):
            self.response = self.get_response_class(response.text)
        else:
            self.response = ErrorResponse(response.text)

        self.response.status = self.status

        return self.response


class ListRequest():
    def list(self, query_parameters=None):
        if query_parameters:
            self.set_query_parameters(query_parameters)
        self.method = 'get'
        return self.fire()


class RetrieveRequest():
    def retrieve(self, pk=None, query_parameters=None):
        if pk:
            self.pk = pk
        else:
            raise Exception('No primary key was provided.')
        if query_parameters:
            self.set_query_parameters(query_parameters)
        self.method = 'get'
        return self.fire()


class PatchRequest():
    def patch(self, pk=None, data=None, query_parameters=None):
        if pk:
            self.pk = pk
        else:
            raise Exception('No primary key was provided.')
        if data:
            self.payload = data
        else:
            raise Exception('No data was provided for the patch.')

        if query_parameters:
            self.set_query_parameters(query_parameters)
        self.method = 'patch'
        return self.fire()


class CreateRequest():
    def create(self, data=None, query_parameters=None):
        if data:
            self.payload = data
        else:
            raise Exception('No data was provided for the create.')

        if query_parameters:
            self.set_query_parameters(query_parameters)
        self.method = 'post'
        return self.fire()


class DeleteRequest():
    def delete(self, pk=None, query_parameters=None):
        if pk:
            self.pk = pk
        else:
            raise Exception('No primary key was provided.')

        if query_parameters:
            self.set_query_parameters(query_parameters)
        self.method = 'delete'
        return self.fire()


class PushTokenRequest(BaseAuthenticatedRequest,
                       ListRequest,
                       PatchRequest,
                       DeleteRequest,
                       RetrieveRequest,
                       CreateRequest):

    url = 'push/tokens'

    response_class = PushTokenResponse

    def get_formatted_pk(self, pk):
        if not pk:
            raise Exception('No primary key was provided.')

        if len(pk) != 32:
            m = hashlib.md5()
            m.update(pk.encode('UTF-8'))
            pk = m.hexdigest()
        return pk

    def retrieve(self, pk=None, query_parameters=None):
        pk = self.get_formatted_pk(pk)
        super(PushTokenRequest, self).retrieve(pk, query_parameters)

    def patch(self, pk=None, data=None, query_parameters=None):
        pk = self.get_formatted_pk(pk)
        super(PushTokenRequest, self).patch(pk, data, query_parameters)

    def delete(self, pk=None, query_parameters=None):
        pk = self.get_formatted_pk(pk)
        super(PushTokenRequest, self).delete(pk, query_parameters)

    def list_associated_users(self, pk=None, query_parameters=None):
        pk = self.get_formatted_pk(pk)
        self.url = "%s/%s/users" % (self.url, pk)
        self.response_class = PushTokenListUsersResponse
        super(PushTokenRequest, self).list(query_parameters)

    def associate_user(self, pk=None, user_id=None, query_parameters=None):
        if not user_id:
            raise Exception('No user id was provided.')

        pk = self.get_formatted_pk(pk)
        self.url = "%s/%s/users/%s" % (self.url, pk, user_id)
        self.response_class = PushTokenListUsersResponse

        if query_parameters:
            self.set_query_parameters(query_parameters)
        self.method = 'post'
        return self.fire()

    def disassociate_user(self, pk=None, user_id=None, query_parameters=None):
        if not user_id:
            raise Exception('No user id was provided.')

        pk = self.get_formatted_pk(pk)
        self.url = "%s/%s/users/%s" % (self.url, pk, user_id)
        self.response_class = PushTokenListUsersResponse

        if query_parameters:
            self.set_query_parameters(query_parameters)
        self.method = 'delete'
        return self.fire()


class BaseRequestOptions:
    class List:
        PageSize = 'page_size'
        Page = 'page'

    class Retrieve:
        pass

    class Patch:
        pass

    class Delete:
        pass


class PushTokenRequestOptions(BaseRequestOptions):

    class List(BaseRequestOptions.List):
        ShowInvalid = 'show_invalid'
        UserId = 'user_id'

    class ListAssociatedUsers(BaseRequestOptions.List):
        pass


class PushMessageRequest(BaseAuthenticatedRequest,
                         DeleteRequest,
                         RetrieveRequest):

    url = 'push/messages'

    response_class = PushMessageResponse


class PushMessageRequestOptions(BaseRequestOptions):
    pass


class PushNotificationRequest(BaseAuthenticatedRequest,
                              CreateRequest,
                              ListRequest,
                              DeleteRequest,
                              RetrieveRequest):

    url = 'push/notifications'

    response_class = PushNotificationResponse


class PushNotificationRequestOptions(BaseRequestOptions):

    class List(BaseRequestOptions.List):
        Fields = 'fields'
