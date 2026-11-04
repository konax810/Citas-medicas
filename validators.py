"""Validaciones sencillas de formularios."""
from datetime import date, datetime
from decimal import Decimal, InvalidOperation


def texto(form, campo, etiqueta, errores, obligatorio=True, max_len=None):
    valor = (form.get(campo) or "").strip()
    if obligatorio and not valor:
        errores.append(f"El campo «{etiqueta}» es obligatorio.")
    if max_len and len(valor) > max_len:
        errores.append(f"«{etiqueta}» admite máximo {max_len} caracteres.")
    return valor or None


def entero(form, campo, etiqueta, errores, minimo=None):
    valor = (form.get(campo) or "").strip()
    if not valor:
        errores.append(f"El campo «{etiqueta}» es obligatorio.")
        return None
    try:
        numero = int(valor)
    except ValueError:
        errores.append(f"«{etiqueta}» debe ser un número entero.")
        return None
    if minimo is not None and numero < minimo:
        errores.append(f"«{etiqueta}» debe ser mayor o igual a {minimo}.")
    return numero


def decimal(form, campo, etiqueta, errores, minimo=None, maximo=None, mayor_que=None):
    valor = (form.get(campo) or "").strip().replace(",", ".")
    if not valor:
        errores.append(f"El campo «{etiqueta}» es obligatorio.")
        return None
    try:
        numero = Decimal(valor)
    except InvalidOperation:
        errores.append(f"«{etiqueta}» debe ser un número.")
        return None
    if mayor_que is not None and numero <= mayor_que:
        errores.append(f"«{etiqueta}» debe ser mayor que {mayor_que}.")
    if minimo is not None and numero < minimo:
        errores.append(f"«{etiqueta}» debe ser mayor o igual a {minimo}.")
    if maximo is not None and numero > maximo:
        errores.append(f"«{etiqueta}» debe ser menor o igual a {maximo}.")
    return numero


def fecha(form, campo, etiqueta, errores):
    valor = (form.get(campo) or "").strip()
    if not valor:
        errores.append(f"El campo «{etiqueta}» es obligatorio.")
        return None
    try:
        return date.fromisoformat(valor)
    except ValueError:
        errores.append(f"«{etiqueta}» debe ser una fecha válida.")
        return None


def fecha_hora(form, campo, etiqueta, errores):
    valor = (form.get(campo) or "").strip()
    if not valor:
        errores.append(f"El campo «{etiqueta}» es obligatorio.")
        return None
    try:
        return datetime.fromisoformat(valor)
    except ValueError:
        errores.append(f"«{etiqueta}» debe ser una fecha y hora válidas.")
        return None


def email(form, campo, etiqueta, errores):
    valor = (form.get(campo) or "").strip()
    if valor and ("@" not in valor or "." not in valor.split("@")[-1]):
        errores.append(f"«{etiqueta}» no tiene un formato válido.")
    return valor or None