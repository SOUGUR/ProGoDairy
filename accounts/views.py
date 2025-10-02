from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login as auth_login

def user_access(request):
    return render(request, "accounts/rights_access.html")

def user_flow(request):
    return render(request, "accounts/user_flow.html")



def login(request):
    if request.method == 'POST':
        print("POST data:", request.POST)

        username = request.POST.get('username')
        password = request.POST.get('password')
        print(username, password)
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            auth_login(request, user)
            return redirect('supplier_list') 
        else:
            return render(request, "accounts/error_page.html", {'error': 'Invalid credentials'})
        
    return render(request, "homePage.html")


