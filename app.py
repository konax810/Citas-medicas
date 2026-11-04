"""Punto de entrada de la aplicación CRUD consultorio_medico_db."""
import psycopg2
from flask import Flask, render_template

import db
from config import Config
from routes.especialidades import bp as especialidades_bp
from routes.servicios_medicos import bp as servicios_medicos_bp
from routes.pacientes import bp as pacientes_bp
from routes.medicos import bp as medicos_bp
from routes.citas import bp as citas_bp


def formato_pesos(valor):
    """Filtro Jinja: 150000 -> $ 150.000 (Ideal para costos de servicios médicos)"""
    if valor is None:
        return ""
    return "$ " + f"{float(valor):,.0f}".replace(",", ".")


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    app.add_template_filter(formato_pesos, "pesos")

    # Registro de Blueprints adaptados al consultorio médico
    for bp in (especialidades_bp, servicios_medicos_bp, pacientes_bp, medicos_bp, citas_bp):
        app.register_blueprint(bp)

    @app.route("/")
    def inicio():
        # Conteos y estadísticas adaptados a las tablas del consultorio médico
        conteos = db.query("""
            SELECT (SELECT COUNT(*) FROM especialidades)    AS especialidades,
                   (SELECT COUNT(*) FROM servicios_medicos) AS servicios_medicos,
                   (SELECT COUNT(*) FROM pacientes)         AS pacientes,
                   (SELECT COUNT(*) FROM medicos)           AS medicos,
                   (SELECT COUNT(*) FROM citas)             AS citas
        """, one=True)
        return render_template("index.html", c=conteos)

    @app.errorhandler(psycopg2.OperationalError)
    def error_conexion(exc):
        return render_template("error_db.html", error=str(exc)), 500

    @app.errorhandler(404)
    def no_encontrado(exc):
        return render_template("404.html"), 404

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5001)