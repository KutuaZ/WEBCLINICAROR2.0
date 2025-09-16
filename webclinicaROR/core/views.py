from django.shortcuts import render

# Create your views here.
def index_estatico(request):
    return render(request, 'paginasinicio/index.html')

def formulario_reserva(request):
    return render(request, 'paginasinicio/reserva.html')
