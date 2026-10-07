from django.shortcuts import render

def personal(request):
    return render(request, 'personal/personal.html')