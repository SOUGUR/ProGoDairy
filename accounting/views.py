from django.shortcuts import render


def accounting_base(request):
    return render(request, "accounting/accounting_base.html")