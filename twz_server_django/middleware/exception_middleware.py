class ExceptionUserInfoMiddleware(object):
    """
    From https://gist.github.com/sidmitra/646372
    Adds user details to request context on receiving an exception, so that they show up in the error emails.
    
    Add to settings.MIDDLEWARE_CLASSES and keep it outermost(i.e. on top if possible). This allows
    it to catch exceptions in other middlewares as well.
    """
    
    def process_exception(self, request, exception):
        """
        Process the exception.
 
        :Parameters:
           - `request`: request that caused the exception
           - `exception`: actual exception being raised
        """

        try:
            if request.user.is_authenticated():
                request.META['AUTH_USERNAME'] = str(request.user.username)
                request.META['AUTH_USER_EMAIL'] = str(request.user.email)
        except:
            request.META['AUTH_USERNAME'] = "NOT AUTHENTICATED"
            request.META['AUTH_USER_EMAIL'] = "NOT AUTHENTICATED"