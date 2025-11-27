from django.shortcuts import render


def accounting_dashboard(request):
    return render(request, "accounting/accounting_dashboard.html")

def billing_and_payment(request):
    return render(request, "accounting/billing_and_payment.html")