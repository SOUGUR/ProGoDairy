from django.shortcuts import render

def user_access(request):
    return render(request, "accounts/rights_access.html")

