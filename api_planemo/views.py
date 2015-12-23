from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.
def v1(request):
    return JsonResponse({'hi': 'hi'})
