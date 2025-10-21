from django.shortcuts import render

def add_get_vehicle_driver(request):
    return render(request, 'distribution/vehicle_driver.html')

def vehicle_list(request):
    return render(request, 'distribution/vehicle_list.html')

def vehicle_CIP_log(request):
    return render(request, 'distribution/vehicle_CIP_log.html')

def create_milk_transfer(request):
    return render(request, 'distribution/milk_transfer.html')

def milk_transfer_list(request):
    return render(request, 'distribution/milk_transfer_list.html')

def gate_pass_tickets(request):
    return render(request, 'distribution/gate_pass_tickets.html')

def gate_pass(request):
    return render(request, 'distribution/gate_pass.html')
