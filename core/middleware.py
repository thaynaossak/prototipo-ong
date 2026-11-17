import time
from django.contrib.auth import logout
class IdleSessionMiddleware:
    def __init__(self,get_response): self.get_response=get_response
    def __call__(self,request):
        now=time.time()
        if request.user.is_authenticated:
            last=request.session.get('last_activity',now)
            if now-last>=1800: logout(request)
            else: request.session['last_activity']=now
        return self.get_response(request)
class HeadersMiddleware:
    def __init__(self,get_response): self.get_response=get_response
    def __call__(self,request):
        response=self.get_response(request)
        response['Content-Security-Policy']="default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; object-src 'none'; base-uri 'self'; frame-ancestors 'none'; form-action 'self'"
        response['Cache-Control']='no-store'
        return response
