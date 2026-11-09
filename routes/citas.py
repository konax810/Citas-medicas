"""CRUD de la tabla citas (FK a pacientes, servicios_medicos y medicos)."""
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

import validators as v
from db import DatabaseError, error_message, execute, query

bp = Blueprint("citas", __name__, url_prefix="/citas")

ESTADOS_CITA = ["Programada", "Atendida", "Cancelada"]


def _leer_formulario(form):
    errores = []
    datos = {
        "fecha_hora": v.fecha_hora(form, "fecha_hora", "Fecha y hora", errores),
        "id_paciente": v.entero(form, "id_paciente", "Paciente", errores, minimo=1),
        "id_servicio": v.entero(form, "id_servicio", "Servicio médico", errores, minimo=1),
        "id_medico": v.entero(form, "id_medico", "Médico", errores, minimo=1),
        "estado_cita": v.texto(form, "estado_cita", "Estado de la cita", errores, max_len=50),
        "observaciones": v.texto(form, "observaciones", "Observaciones", errores, obligatorio=False),
    }
    if datos["estado_cita"] and datos["estado_cita"] not in ESTADOS_CITA:
        errores.append("Estado de cita no válido.")
    return datos, errores


def _render_form(item, titulo):
    return render_template(
        "citas/form.html", item=item, titulo=titulo, estados=ESTADOS_CITA,
        # 🛠️ AGREGADO: numero_documento para que aparezca en el paréntesis del paciente
        pacientes=query("SELECT id_paciente, nombre, apellido, numero_documento FROM pacientes ORDER BY apellido"),
        servicios=query("SELECT id_servicio, nombre_servicio, precio_consulta FROM servicios_medicos ORDER BY nombre_servicio"),
        # 🛠️ Asegúrate de incluir el campo que va dentro del paréntesis del médico (ej: consultorio)
        medicos=query("SELECT id_medico, nombre, apellido, consultorio FROM medicos ORDER BY apellido"),
    )


@bp.route("/")
def listar():
    items = query("""
        SELECT ci.*, p.nombre AS nombre_paciente, p.apellido AS apellido_paciente,
               s.nombre_servicio, m.nombre AS nombre_medico, m.apellido AS apellido_medico
          FROM citas ci
          JOIN pacientes       p ON p.id_paciente = ci.id_paciente
          JOIN servicios_medicos s ON s.id_servicio = ci.id_servicio
          JOIN medicos         m ON m.id_medico   = ci.id_medico
         ORDER BY ci.fecha_hora DESC, ci.id_cita DESC
    """)
    return render_template("citas/list.html", items=items)


@bp.route("/nuevo", methods=["GET", "POST"])
def crear():
    item = {"estado_cita": "Programada"}
    if request.method == "POST":
        item = request.form.to_dict()
        datos, errores = _leer_formulario(request.form)
        if not errores:
            try:
                execute("""INSERT INTO citas (fecha_hora, id_paciente, id_servicio, id_medico, estado_cita, observaciones)
                            VALUES (%(fecha_hora)s, %(id_paciente)s, %(id_servicio)s, %(id_medico)s, %(estado_cita)s, %(observaciones)s)""",
                        datos)
                flash("Cita médica programada correctamente.", "success")
                return redirect(url_for(".listar"))
            except DatabaseError as exc:
                errores.append(error_message(exc))
        for e in errores:
            flash(e, "danger")
    return _render_form(item, "Nueva cita médica")


@bp.route("/<int:id>/editar", methods=["GET", "POST"])
def editar(id):
    item = query("SELECT * FROM citas WHERE id_cita = %s", (id,), one=True)
    if item is None:
        abort(404)
    if request.method == "POST":
        item = {**item, **request.form.to_dict()}
        datos, errores = _leer_formulario(request.form)
        if not errores:
            try:
                execute("""UPDATE citas
                              SET fecha_hora    = %(fecha_hora)s,
                                  id_paciente   = %(id_paciente)s,
                                  id_servicio   = %(id_servicio)s,
                                  id_medico     = %(id_medico)s,
                                  estado_cita   = %(estado_cita)s,
                                  observaciones = %(observaciones)s
                            WHERE id_cita = %(id)s""",
                        {**datos, "id": id})
                flash("Cita médica actualizada correctamente.", "success")
                return redirect(url_for(".listar"))
            except DatabaseError as exc:
                errores.append(error_message(exc))
        for e in errores:
            flash(e, "danger")
    return _render_form(item, "Editar cita médica")


@bp.route("/<int:id>/eliminar", methods=["POST"])
def eliminar(id):
    try:
        if execute("DELETE FROM citas WHERE id_cita = %s", (id,)):
            flash("Cita eliminada.", "success")
        else:
            flash("La cita no existe.", "warning")
    except DatabaseError as exc:
        flash(error_message(exc), "danger")
    return redirect(url_for(".listar"))