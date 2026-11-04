"""CRUD de la tabla servicios_medicos (FK a especialidades)."""
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

import validators as v
from db import DatabaseError, error_message, execute, query

bp = Blueprint("servicios_medicos", __name__, url_prefix="/servicios-medicos")


def _leer_formulario(form):
    errores = []
    datos = {
        "nombre_servicio": v.texto(form, "nombre_servicio", "Nombre del servicio", errores, max_len=150),
        "id_especialidad": v.entero(form, "id_especialidad", "Especialidad", errores, minimo=1),
        "precio_consulta": v.decimal(form, "precio_consulta", "Precio de consulta", errores, minimo=0),
        "duracion_minutos": v.entero(form, "duracion_minutos", "Duración en minutos", errores, minimo=1),
    }
    return datos, errores


def _especialidades():
    return query("SELECT id_especialidad, nombre_especialidad FROM especialidades ORDER BY nombre_especialidad")


def _render_form(item, titulo):
    return render_template("servicios_medicos/form.html", item=item, titulo=titulo,
                           especialidades=_especialidades())


@bp.route("/")
def listar():
    items = query("""
        SELECT s.*, e.nombre_especialidad
          FROM servicios_medicos s
          JOIN especialidades e ON e.id_especialidad = s.id_especialidad
         ORDER BY s.id_servicio
    """)
    return render_template("servicios_medicos/list.html", items=items)


@bp.route("/nuevo", methods=["GET", "POST"])
def crear():
    item = {}
    if request.method == "POST":
        item = request.form.to_dict()
        datos, errores = _leer_formulario(request.form)
        if not errores:
            try:
                execute("""INSERT INTO servicios_medicos (nombre_servicio, id_especialidad, precio_consulta, duracion_minutos)
                            VALUES (%(nombre_servicio)s, %(id_especialidad)s, %(precio_consulta)s, %(duracion_minutos)s)""",
                        datos)
                flash("Servicio médico creado correctamente.", "success")
                return redirect(url_for(".listar"))
            except DatabaseError as exc:
                errores.append(error_message(exc))
        for e in errores:
            flash(e, "danger")
    return _render_form(item, "Nuevo servicio médico")


@bp.route("/<int:id>/editar", methods=["GET", "POST"])
def editar(id):
    item = query("SELECT * FROM servicios_medicos WHERE id_servicio = %s", (id,), one=True)
    if item is None:
        abort(404)
    if request.method == "POST":
        item = {**item, **request.form.to_dict()}
        datos, errores = _leer_formulario(request.form)
        if not errores:
            try:
                execute("""UPDATE servicios_medicos
                              SET nombre_servicio  = %(nombre_servicio)s,
                                  id_especialidad  = %(id_especialidad)s,
                                  precio_consulta  = %(precio_consulta)s,
                                  duracion_minutos = %(duracion_minutos)s
                            WHERE id_servicio = %(id)s""",
                        {**datos, "id": id})
                flash("Servicio médico actualizado correctamente.", "success")
                return redirect(url_for(".listar"))
            except DatabaseError as exc:
                errores.append(error_message(exc))
        for e in errores:
            flash(e, "danger")
    return _render_form(item, "Editar servicio médico")


@bp.route("/<int:id>/eliminar", methods=["POST"])
def eliminar(id):
    try:
        if execute("DELETE FROM servicios_medicos WHERE id_servicio = %s", (id,)):
            flash("Servicio médico eliminado.", "success")
        else:
            flash("El servicio médico no existe.", "warning")
    except DatabaseError as exc:
        flash(error_message(exc), "danger")
    return redirect(url_for(".listar"))