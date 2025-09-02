from django.shortcuts import render

def pump_into_silos(request):
    return render(request, "plants/pump_into_silos.html")


def tanker_logs(request):
    return render(request, "plants/tanker_logs.html")

