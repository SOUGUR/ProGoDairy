from django.shortcuts import render

def pump_into_silos(request):
    return render(request, "plants/pump_into_silos.html")

