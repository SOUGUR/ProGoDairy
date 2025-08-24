from django.shortcuts import render

def vehicle_list(request):
    return render(request, 'distribution/vehicle_list.html')

def create_milk_transfer(request):
    return render(request, 'distribution/milk_transfer.html')

def milk_transfer_list(request):
    return render(request, 'distribution/milk_transfer_list.html')
