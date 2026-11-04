"""CRUD de la tabla especialidades."""
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

import validators as v
from db import DatabaseError, error_message, execute, query

bp = Blueprint("especialidades", __name__, url_prefix="/especialidades")


def _leer_formulario(form):
    errores = []
    datos = {
        "nombre_especialidad": v.texto(form, "nombre_especialidad", "Nombre de Especialidad", errores, max_len=100),
        "descripcion": v.texto(form, "descripcion", "Descripción", errores, obligatorio=False, max_len=200),
    }
    return datos, errores


@bp.route("/")
def listar():
    items = query("""
        SELECT e.*, COUNT(s.id_servicio) AS num_servicios
          FROM especialidades e
          LEFT JOIN servicios_medicos s ON s.id_especialidad = e.id_especialidad
         GROUP BY e.id_especialidad
         ORDER BY e.id_especialidad
    """)
    return render_template("especialidades/list.html", items=items)


@bp.route("/nuevo", methods=["GET", "POST"])
def crear():
    item = {}
    if request.method == "POST":
        item = request.form.to_dict()
        datos, errores = _leer_formulario(request.form)
        if not errores:
            try:
                execute("INSERT INTO especialidades (nombre_especialidad, descripcion) VALUES (%s, %s)",
                        (datos["nombre_especialidad"], datos["descripcion"]))
                flash("Especialidad creada correctamente.", "success")
                return redirect(url_for(".listar"))
            except DatabaseError as exc:
                errores.append(error_message(exc))
        for e in errores:
            flash(e, "danger")
    return render_template("especialidades/form.html", item=item, titulo="Nueva especialidad")


@bp.route("/<int:id>/editar", methods=["GET", "POST"])
def editar(id):
    item = query("SELECT * FROM especialidades WHERE id_especialidad = %s", (id,), one=True)
    if item is None:
        abort(404)
    if request.method == "POST":
        item = {**item, **request.form.to_dict()}
        datos, errores = _leer_formulario(request.form)
        if not errores:
            try:
                execute("""UPDATE especialidades SET nombre_especialidad = %s, descripcion = %s
                            WHERE id_especialidad = %s""",
                        (datos["nombre_especialidad"], datos["descripcion"], id))
                flash("Especialidad actualizada correctamente.", "success")
                return redirect(url_for(".listar"))
            except DatabaseError as exc:
                errores.append(error_message(exc))
        for e in errores:
            flash(e, "danger")
    return render_template("especialidades/form.html", item=item, titulo="Editar especialidad")


@bp.route("/<int:id>/eliminar", methods=["POST"])
def eliminar(id):
    try:
        if execute("DELETE FROM especialidades WHERE id_especialidad = %s", (id,)):
            flash("Especialidad eliminada.", "success")
        else:
            flash("La especialidad no existe.", "warning")
    except DatabaseError as exc:
        flash(error_message(exc), "danger")
    return redirect(url_for(".listar"))