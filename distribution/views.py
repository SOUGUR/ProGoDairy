from django.shortcuts import render

def vehicle_list(request):
    return render(request, 'distribution/vehicle_list.html')