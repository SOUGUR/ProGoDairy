from django.shortcuts import render

def take_composite_sample(request):
    return render(request, "milk/take_composite_sample.html")

def list_composite_samples(request):
    return render(request, "milk/list_composite_samples.html")