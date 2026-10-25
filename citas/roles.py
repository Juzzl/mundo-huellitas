from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

ADMIN = "administrador"
GROOMER = "groomer"
CUIDADOR = "cuidador"
CLIENTE = "cliente"
PERSONAL = (ADMIN, GROOMER, CUIDADOR) 
ROLES = PERSONAL + (CLIENTE,)
ALIAS = {"clientes": CLIENTE}

def rol_de(user):
    if not user.is_authenticated:
        return None
    if user.is_superuser:
        return ADMIN
    for nombre in user.groups.values_list("name", flat=True):
        normalizado = ALIAS.get(nombre.strip().lower(), nombre.strip().lower())
        if normalizado in ROLES:
            return normalizado
    return None

def rol_requerido(*roles):
    def decorador(vista):
        @wraps(vista)
        def envoltura(request, *args, **kwargs):
            if rol_de(request.user) not in roles:
                raise PermissionDenied
            return vista(request, *args, **kwargs)
        return login_required(envoltura)
    return decorador

def contexto_rol(request):
    return {"rol": rol_de(request.user)}

