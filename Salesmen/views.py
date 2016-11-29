from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

def tsp(request):
	return render(request,'Salesmen/tsp.html',{})