from django.shortcuts import render

# Create your views here.



def terms_of_service(request):
    return render(request, "components/terms_of_service.html")

def privacy_policy(request):
    return render(request, "components/privacy_policy.html")


def cookies_policy(request):
    return render(request, "components/cookies_policy.html")
