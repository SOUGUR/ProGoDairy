from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from accounts.models import UserProfile
from .forms import SupplierProfileForm
from .models import Supplier


@login_required
def create_supplier_profile(request):
    if hasattr(request.user, "supplier_profile"):
        return redirect("supplier_dashboard")

    if request.method == "POST":
        form = SupplierProfileForm(request.POST)
        if form.is_valid():
            supplier = form.save(commit=False)
            supplier.user = request.user
            supplier.save()
            return redirect(
                "supplier_dashboard"
            )  # Redirect to dashboard or success page
    else:
        form = SupplierProfileForm()

    return render(request, "suppliers/create_supplier_profile.html", {"form": form})


@login_required
def supplier_dashboard(request):
    if not user_profile.roles.filter(name="supplier").exists():
        return redirect("unauthorized")
    try:
        supplier = Supplier.objects.get(user=request.user)
    except Supplier.DoesNotExist:
        return redirect("create_supplier_profile")

    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        return redirect("create_supplier_profile")

    if not user_profile.roles.filter(name="supplier").exists():
        return redirect("unauthorized")

    return render(request, "suppliers/supplier_dashboard.html", {"supplier": supplier})
