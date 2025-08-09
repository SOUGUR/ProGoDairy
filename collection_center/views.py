from django.shortcuts import render

def assign_cooler_tank(request):
    return render(request, 'collection_center/assign_cooler_tank.html')
