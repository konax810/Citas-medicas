"""CRUD de la tabla pacientes."""
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

import validators as v
from db import DatabaseError, error_message, execute, query

bp = Blueprint("pacientes", __name__, url_prefix="/pacientes")

TIPOS_DOCUMENTO = ["CC", "TI", "RC", "CE", "PA", "PPT"]


def _leer_formulario(form):
    errores = []
    datos = {
        "tipo_documento": v.texto(form, "tipo_documento", "Tipo de documento", errores, max_len=5),
        "numero_documento": v.texto(form, "numero_documento", "Número de documento", errores, max_len=20),
        "nombre": v.texto(form, "nombre", "Nombre", errores, max_len=100),
        "apellido": v.texto(form, "apellido", "Apellido", errores, max_len=100),
        "fecha_nacimiento": v.fecha(form, "fecha_nacimiento", "Fecha de nacimiento", errores),
        "telefono": v.texto(form, "telefono", "Teléfono", errores, obligatorio=False, max_len=20),
        "direccion": v.texto(form, "direccion", "Dirección", errores, obligatorio=False, max_len=200),
        "email": v.email(form, "email", "Email", errores),
    }
    if datos["tipo_documento"] and datos["tipo_documento"] not in TIPOS_DOCUMENTO:
        errores.append("Tipo de documento no válido.")
    return datos, errores


def _render_form(item, titulo):
    return render_template("pacientes/form.html", item=item, titulo=titulo, tipos_documento=TIPOS_DOCUMENTO)


@bp.route("/")
def listar():
    items = query("""
        SELECT p.*, COUNT(c.id_cita) AS num_citas
          FROM pacientes p
          LEFT JOIN citas c ON c.id_paciente = p.id_paciente
         GROUP BY p.id_paciente
         ORDER BY p.id_paciente
    """)
    return render_template("pacientes/list.html", items=items)


@bp.route("/nuevo", methods=["GET", "POST"])
def crear():
    item = {}
    if request.method == "POST":
        item = request.form.to_dict()
        datos, errores = _leer_formulario(request.form)
        if not errores:
            try:
                execute("""INSERT INTO pacientes (tipo_documento, numero_documento, nombre, apellido, fecha_nacimiento, telefono, direccion, email)
                            VALUES (%(tipo_documento)s, %(numero_documento)s, %(nombre)s, %(apellido)s, %(fecha_nacimiento)s, %(telefono)s, %(direccion)s, %(email)s)""",
                        datos)
                flash("Paciente creado correctamente.", "success")
                return redirect(url_for(".listar"))
            except DatabaseError as exc:
                errores.append(error_message(exc))
        for e in errores:
            flash(e, "danger")
    return _render_form(item, "Nuevo paciente")


@bp.route("/<int:id>/editar", methods=["GET", "POST"])
def editar(id):
    item = query("SELECT * FROM pacientes WHERE id_paciente = %s", (id,), one=True)
    if item is None:
        abort(404)
    if request.method == "POST":
        item = {**item, **request.form.to_dict()}
        datos, errores = _leer_formulario(request.form)
        if not errores:
            try:
                execute("""UPDATE pacientes
                              SET tipo_documento   = %(tipo_documento)s,
                                  numero_documento = %(numero_documento)s,
                                  nombre           = %(nombre)s,
                                  apellido         = %(apellido)s,
                                  fecha_nacimiento = %(fecha_nacimiento)s,
                                  telefono         = %(telefono)s,
                                  direccion        = %(direccion)s,
                                  email            = %(email)s
                            WHERE id_paciente = %(id)s""",
                        {**datos, "id": id})
                flash("Paciente actualizado correctamente.", "success")
                return redirect(url_for(".listar"))
            except DatabaseError as exc:
                errores.append(error_message(exc))
        for e in errores:
            flash(e, "danger")
    return _render_form(item, "Editar paciente")


@bp.route("/<int:id>/eliminar", methods=["POST"])
def eliminar(id):
    try:
        if execute("DELETE FROM pacientes WHERE id_paciente = %s", (id,)):
            flash("Paciente eliminado.", "success")
        else:
            flash("El paciente no existe.", "warning")
    except DatabaseError as exc:
        flash(error_message(exc), "danger")
    return redirect(url_for(".listar"))