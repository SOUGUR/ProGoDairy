from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm


from django.shortcuts import render, redirect
from django.contrib.auth.models import Group
from .forms import UserRegistrationForm

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            role = form.cleaned_data['role']
            group, _ = Group.objects.get_or_create(name=role)
            user.groups.add(group)

            login(request, user)

            if role == 'SUPPLIER':
                return redirect('create_supplier_profile')
            elif role == 'DISTRIBUTOR':
                return redirect('create_distributor_profile')  
            else:
                return redirect('employee_dashboard')  
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})


def custom_login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('supplier_dashboard')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid login credentials.")
    else:
        form = AuthenticationForm()

    return render(request, 'registration/login.html', {'form': form})
