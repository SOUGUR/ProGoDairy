from django.shortcuts import render

def take_composite_sample(request):
    return render(request, "milk/take_composite_sample.html")

def list_composite_samples(request):
    return render(request, "milk/list_composite_samples.html")

def take_gate_sample(request):
    return render(request, "milk/take_gate_sample.html")

def manage_milk_route_pricings(request):
    return render(request, "milk/milk_route_prices.html")