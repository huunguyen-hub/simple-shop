from django.template import RequestContext


def setting(request):
    context_instance = RequestContext(request)
    return context_instance
