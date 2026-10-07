from django.shortcuts import render


def clientes(request):
    return render(request, 'clientes/clientes.html')
