"""Conexión a PostgreSQL y funciones de ayuda para ejecutar SQL."""
import psycopg2
import psycopg2.extras
from flask import current_app, g

# Alias para capturar cualquier error de la base de datos en las rutas
DatabaseError = psycopg2.Error


def get_db():
    """Abre una conexión por petición y la reutiliza mientras dure la petición."""
    if "db" not in g:
        cfg = current_app.config
        g.db = psycopg2.connect(
            host=cfg["DB_HOST"],
            port=cfg["DB_PORT"],
            dbname=cfg["DB_NAME"],
            user=cfg["DB_USER"],
            password=cfg["DB_PASSWORD"],
        )
    return g.db


def close_db(exc=None):
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


def init_app(app):
    app.teardown_appcontext(close_db)


def query(sql, params=(), one=False):
    """Ejecuta un SELECT. Devuelve una lista de diccionarios (o uno solo si one=True)."""
    conn = get_db()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(sql, params)
        rows = cur.fetchall()
    conn.commit()
    if one:
        return rows[0] if rows else None
    return rows


def execute(sql, params=()):
    """Ejecuta INSERT / UPDATE / DELETE con commit. Si falla, hace rollback y relanza el error."""
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            affected = cur.rowcount
        conn.commit()
        return affected
    except psycopg2.Error:
        conn.rollback()
        raise


def error_message(exc):
    """Traduce los errores más comunes de PostgreSQL a mensajes claros en español."""
    code = getattr(exc, "pgcode", None)
    if code == "23503":  # foreign_key_violation
        return ("No se puede completar la operación: el registro está relacionado "
                "con otros datos (por ejemplo, tiene citas o servicios asociados).")
    if code == "23505":  # unique_violation
        return "Ya existe un registro con ese valor (campo único duplicado)."
    if code == "23514":  # check_violation
        return "Algún valor está fuera del rango permitido por la base de datos."
    if code == "23502":  # not_null_violation
        return "Falta un campo obligatorio."
    return f"Error de base de datos: {getattr(exc, 'pgerror', None) or exc}"
