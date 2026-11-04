"""CRUD de la tabla medicos."""
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

import validators as v
from db import DatabaseError, error_message, execute, query

bp = Blueprint("medicos", __name__, url_prefix="/medicos")

TIPOS_DOCUMENTO = ["CC", "CE", "PA", "PPT"]


def _leer_formulario(form):
    errores = []
    datos = {
        "tipo_documento": v.texto(form, "tipo_documento", "Tipo de documento", errores, max_len=5),
        "numero_documento": v.texto(form, "numero_documento", "Número de documento", errores, max_len=20),
        "nombre": v.texto(form, "nombre", "Nombre", errores, max_len=100),
        "apellido": v.texto(form, "apellido", "Apellido", errores, max_len=100),
        "registro_medico": v.texto(form, "registro_medico", "Registro médico", errores, max_len=50),
        "consultorio": v.texto(form, "consultorio", "Consultorio", errores, max_len=50),
        "telefono_contacto": v.texto(form, "telefono_contacto", "Teléfono de contacto", errores, max_len=20),
        "email": v.email(form, "email", "Email", errores),
    }
    if datos["tipo_documento"] and datos["tipo_documento"] not in TIPOS_DOCUMENTO:
        errores.append("Tipo de documento no válido.")
    return datos, errores


def _render_form(item, titulo):
    return render_template("medicos/form.html", item=item, titulo=titulo, tipos_documento=TIPOS_DOCUMENTO)


@bp.route("/")
def listar():
    items = query("""
        SELECT m.*, COUNT(c.id_cita) AS num_citas
          FROM medicos m
          LEFT JOIN citas c ON c.id_medico = m.id_medico
         GROUP BY m.id_medico
         ORDER BY m.id_medico
    """)
    return render_template("medicos/list.html", items=items)


@bp.route("/nuevo", methods=["GET", "POST"])
def crear():
    item = {}
    if request.method == "POST":
        item = request.form.to_dict()
        datos, errores = _leer_formulario(request.form)
        if not errores:
            try:
                execute("""INSERT INTO medicos (tipo_documento, numero_documento, nombre, apellido, registro_medico, consultorio, telefono_contacto, email)
                            VALUES (%(tipo_documento)s, %(numero_documento)s, %(nombre)s, %(apellido)s, %(registro_medico)s, %(consultorio)s, %(telefono_contacto)s, %(email)s)""",
                        datos)
                flash("Médico creado correctamente.", "success")
                return redirect(url_for(".listar"))
            except DatabaseError as exc:
                errores.append(error_message(exc))
        for e in errores:
            flash(e, "danger")
    return _render_form(item, "Nuevo médico")


@bp.route("/<int:id>/editar", methods=["GET", "POST"])
def editar(id):
    item = query("SELECT * FROM medicos WHERE id_medico = %s", (id,), one=True)
    if item is None:
        abort(404)
    if request.method == "POST":
        item = {**item, **request.form.to_dict()}
        datos, errores = _leer_formulario(request.form)
        if not errores:
            try:
                execute("""UPDATE medicos
                              SET tipo_documento    = %(tipo_documento)s,
                                  numero_documento  = %(numero_documento)s,
                                  nombre            = %(nombre)s,
                                  apellido          = %(apellido)s,
                                  registro_medico   = %(registro_medico)s,
                                  consultorio       = %(consultorio)s,
                                  telefono_contacto = %(telefono_contacto)s,
                                  email             = %(email)s
                            WHERE id_medico = %(id)s""",
                        {**datos, "id": id})
                flash("Médico actualizado correctamente.", "success")
                return redirect(url_for(".listar"))
            except DatabaseError as exc:
                errores.append(error_message(exc))
        for e in errores:
            flash(e, "danger")
    return _render_form(item, "Editar médico")


@bp.route("/<int:id>/eliminar", methods=["POST"])
def eliminar(id):
    try:
        if execute("DELETE FROM medicos WHERE id_medico = %s", (id,)):
            flash("Médico eliminado.", "success")
        else:
            flash("El médico no existe.", "warning")
    except DatabaseError as exc:
        flash(error_message(exc), "danger")
    return redirect(url_for(".listar"))