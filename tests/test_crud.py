"""Pruebas de integración CRUD para el sistema del consultorio médico.

La suite escribe y elimina datos. Antes de ejecutarla, configura TEST_DB_NAME
con el nombre de una base PostgreSQL de pruebas ya preparada con el esquema
del proyecto. No uses la base de desarrollo ni ejecutes aquí el SQL que elimina
y recrea las tablas.

Ejecutar explícitamente este archivo con: python -m pytest -v tests/test_crud.py
"""
from contextlib import closing
from decimal import Decimal
from html import unescape
import os
import re
from uuid import uuid4

import psycopg2
import pytest

from app import create_app
from config import Config


TABLAS_IDS = {
    "especialidades": ("especialidades", "id_especialidad"),
    "servicios-medicos": ("servicios_medicos", "id_servicio"),
    "pacientes": ("pacientes", "id_paciente"),
    "medicos": ("medicos", "id_medico"),
    "citas": ("citas", "id_cita"),
}


def conectar(config):
    return psycopg2.connect(
        host=config.DB_HOST,
        port=config.DB_PORT,
        dbname=config.DB_NAME,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
    )


@pytest.fixture(scope="session")
def test_config():
    """Bloquea la suite si no se indicó una base aislada de pruebas."""
    nombre_pruebas = (os.getenv("TEST_DB_NAME") or "").strip()
    nombre_app = str(Config.DB_NAME).strip()

    if not nombre_pruebas:
        pytest.fail(
            "Falta TEST_DB_NAME. Configura una base PostgreSQL exclusiva para pruebas.",
            pytrace=False,
        )
    if nombre_pruebas.casefold() == nombre_app.casefold():
        pytest.fail(
            "TEST_DB_NAME coincide con DB_NAME de la aplicación. "
            "Las pruebas no se ejecutarán contra esa base.",
            pytrace=False,
        )

    config_pruebas = type(
        "TestConfig",
        (Config,),
        {"DB_NAME": nombre_pruebas, "TESTING": True},
    )

    # Esta comprobación solo lee. No crea bases, tablas ni registros.
    try:
        with closing(conectar(config_pruebas)) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT current_database()")
                nombre_conectado = cur.fetchone()[0]
                if nombre_conectado.casefold() != nombre_pruebas.casefold():
                    pytest.fail(
                        "PostgreSQL conectó a una base distinta de TEST_DB_NAME.",
                        pytrace=False,
                    )
                for tabla in (
                    "especialidades",
                    "servicios_medicos",
                    "pacientes",
                    "medicos",
                    "citas",
                ):
                    cur.execute("SELECT to_regclass(%s)", (f"public.{tabla}",))
                    if cur.fetchone()[0] is None:
                        pytest.fail(
                            f"La base de pruebas no contiene public.{tabla}. "
                            "Prepara el esquema manualmente en la base de pruebas.",
                            pytrace=False,
                        )
    except psycopg2.Error as exc:
        pytest.fail(
            f"No se pudo comprobar la base TEST_DB_NAME={nombre_pruebas!r}: {exc}",
            pytrace=False,
        )

    return config_pruebas


@pytest.fixture
def client(test_config):
    app = create_app(test_config)
    app.config["TESTING"] = True
    with app.test_client() as cliente:
        yield cliente


def sql(config, consulta, params=()):
    """Ejecuta una consulta parametrizada en la misma base de pruebas."""
    with closing(conectar(config)) as conn:
        with conn:
            with conn.cursor() as cur:
                cur.execute(consulta, params)
                return cur.fetchone() if cur.description else None


def textos_alertas(respuesta):
    """Devuelve solo el texto de las alertas para que un fallo sea legible."""
    html = respuesta.get_data(as_text=True)
    bloques = re.findall(r'<div class="alert\b[^\"]*"[^>]*>(.*?)</div>', html, re.S)
    textos = [re.sub(r"<[^>]+>", " ", bloque) for bloque in bloques]
    return " ".join(unescape(" ".join(textos)).split())


def siguiente_id(config, recurso):
    tabla, columna = TABLAS_IDS[recurso]
    # tabla y columna salen del diccionario constante TABLAS_IDS, no del usuario.
    resultado = sql(config, f"SELECT COALESCE(MAX({columna}), 0) + 1 FROM {tabla}")
    return resultado[0]


@pytest.fixture
def registros_prueba(test_config):
    """Crea identificadores únicos y limpia dependencias incluso si falla una aserción."""
    token = uuid4().hex[:12].upper()
    etiqueta = f"ZZ_TEST_{token}"
    registros = {
        "token": token,
        "etiqueta": etiqueta,
        "nombre_especialidad": f"{etiqueta} ESPECIALIDAD",
        "nombre_servicio": f"{etiqueta} SERVICIO",
        "documento_paciente": f"PT{token}",
        "documento_medico": f"MD{token}",
        "registro_medico": f"RM-{token}",
        "email_paciente": f"paciente-{token.lower()}@example.test",
        "email_medico": f"medico-{token.lower()}@example.test",
    }
    yield registros

    # El orden respeta las FK: citas -> pacientes/médicos/servicios -> especialidades.
    with closing(conectar(test_config)) as conn:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """DELETE FROM citas
                        WHERE observaciones = %s
                           OR id_paciente IN (
                               SELECT id_paciente FROM pacientes WHERE numero_documento = %s
                           )
                           OR id_servicio IN (
                               SELECT id_servicio FROM servicios_medicos WHERE nombre_servicio = %s
                           )
                           OR id_medico IN (
                               SELECT id_medico FROM medicos WHERE registro_medico = %s
                           )""",
                    (
                        registros["etiqueta"],
                        registros["documento_paciente"],
                        registros["nombre_servicio"],
                        registros["registro_medico"],
                    ),
                )
                cur.execute(
                    "DELETE FROM pacientes WHERE numero_documento = %s",
                    (registros["documento_paciente"],),
                )
                cur.execute(
                    "DELETE FROM medicos WHERE registro_medico = %s",
                    (registros["registro_medico"],),
                )
                cur.execute(
                    "DELETE FROM servicios_medicos WHERE nombre_servicio = %s",
                    (registros["nombre_servicio"],),
                )
                cur.execute(
                    """DELETE FROM especialidades
                        WHERE nombre_especialidad IN (%s, %s)""",
                    (
                        registros["nombre_especialidad"],
                        f"{registros['nombre_especialidad']} EDITADA",
                    ),
                )


def datos_especialidad(registros, **cambios):
    return {
        "nombre_especialidad": registros["nombre_especialidad"],
        "descripcion": "Especialidad creada por las pruebas.",
        **cambios,
    }


def datos_servicio(registros, id_especialidad, **cambios):
    return {
        "nombre_servicio": registros["nombre_servicio"],
        "id_especialidad": str(id_especialidad),
        "precio_consulta": "12345.50",
        "duracion_minutos": "30",
        **cambios,
    }


def datos_paciente(registros, **cambios):
    return {
        "tipo_documento": "CC",
        "numero_documento": registros["documento_paciente"],
        "nombre": registros["etiqueta"],
        "apellido": "Paciente Prueba",
        "sexo": "Femenino",
        "rh": "O+",
        "fecha_nacimiento": "1990-05-12",
        "telefono": "3000000000",
        "direccion": "Dirección de prueba",
        "email": registros["email_paciente"],
        **cambios,
    }


def datos_medico(registros, **cambios):
    return {
        "tipo_documento": "CC",
        "numero_documento": registros["documento_medico"],
        "nombre": registros["etiqueta"],
        "apellido": "Médico Prueba",
        "registro_medico": registros["registro_medico"],
        "consultorio": "TEST-1",
        "telefono_contacto": "3100000000",
        "email": registros["email_medico"],
        **cambios,
    }


def datos_cita(registros, padres, **cambios):
    return {
        "fecha_hora": "2099-01-01T10:00",
        "id_paciente": str(padres["paciente"]),
        "id_servicio": str(padres["servicio"]),
        "id_medico": str(padres["medico"]),
        "estado_cita": "Programada",
        "observaciones": registros["etiqueta"],
        **cambios,
    }


def crear_especialidad(cliente, config, registros):
    respuesta = cliente.post(
        "/especialidades/nuevo",
        data=datos_especialidad(registros),
        follow_redirects=True,
    )
    assert "Especialidad creada correctamente" in respuesta.get_data(as_text=True)
    return sql(
        config,
        "SELECT id_especialidad FROM especialidades WHERE nombre_especialidad = %s",
        (registros["nombre_especialidad"],),
    )[0]


def crear_paciente(cliente, config, registros):
    respuesta = cliente.post(
        "/pacientes/nuevo", data=datos_paciente(registros), follow_redirects=True
    )
    assert "Paciente creado correctamente" in respuesta.get_data(as_text=True)
    return sql(
        config,
        "SELECT id_paciente FROM pacientes WHERE numero_documento = %s",
        (registros["documento_paciente"],),
    )[0]


def crear_medico(cliente, config, registros):
    respuesta = cliente.post(
        "/medicos/nuevo", data=datos_medico(registros), follow_redirects=True
    )
    assert "Médico creado correctamente" in respuesta.get_data(as_text=True)
    return sql(
        config,
        "SELECT id_medico FROM medicos WHERE registro_medico = %s",
        (registros["registro_medico"],),
    )[0]


@pytest.fixture
def padres_prueba(client, test_config, registros_prueba):
    """Prepara relaciones mediante los formularios reales de la aplicación."""
    id_especialidad = crear_especialidad(client, test_config, registros_prueba)
    id_paciente = crear_paciente(client, test_config, registros_prueba)
    id_medico = crear_medico(client, test_config, registros_prueba)

    respuesta = client.post(
        "/servicios-medicos/nuevo",
        data=datos_servicio(registros_prueba, id_especialidad),
        follow_redirects=True,
    )
    assert "Servicio médico creado correctamente" in respuesta.get_data(as_text=True)
    id_servicio = sql(
        test_config,
        "SELECT id_servicio FROM servicios_medicos WHERE nombre_servicio = %s",
        (registros_prueba["nombre_servicio"],),
    )[0]
    return {
        "especialidad": id_especialidad,
        "paciente": id_paciente,
        "medico": id_medico,
        "servicio": id_servicio,
    }



# ---------------------------------------------------------------- casos PF (15 en total, sin parametrizaciones)


def crear_cita(cliente, config, registros, padres, **cambios):
    respuesta = cliente.post(
        "/citas/nuevo",
        data=datos_cita(registros, padres, **cambios),
        follow_redirects=True,
    )
    assert "Cita médica programada correctamente" in respuesta.get_data(as_text=True)
    fila = sql(
        config,
        "SELECT id_cita FROM citas WHERE observaciones = %s",
        (registros["etiqueta"],),
    )
    assert fila is not None
    return fila[0]


def comprobar_paginas_principales(cliente):
    """Comprueba inicio, los cinco listados y los cinco formularios de alta."""
    rutas = (
        "/",
        "/especialidades/",
        "/servicios-medicos/",
        "/pacientes/",
        "/medicos/",
        "/citas/",
        "/especialidades/nuevo",
        "/servicios-medicos/nuevo",
        "/pacientes/nuevo",
        "/medicos/nuevo",
        "/citas/nuevo",
    )
    for ruta in rutas:
        assert cliente.get(ruta).status_code == 200, f"No cargó {ruta}"


def comprobar_edicion_y_404(cliente, recurso, id_existente, id_inexistente):
    assert cliente.get(f"/{recurso}/{id_existente}/editar").status_code == 200
    assert cliente.get(f"/{recurso}/{id_inexistente}/editar").status_code == 404


# Cada prueba corresponde a un ID del plan y contiene todas sus comprobaciones
# para mantener exactamente 15 casos recopilados por pytest.


def test_PF_01_especialidades_ciclo_crud_listado_y_rutas(
    client, test_config, registros_prueba
):
    comprobar_paginas_principales(client)
    id_registro = crear_especialidad(client, test_config, registros_prueba)
    assert registros_prueba["nombre_especialidad"] in client.get(
        "/especialidades/"
    ).get_data(as_text=True)
    id_inexistente = siguiente_id(test_config, "especialidades")
    comprobar_edicion_y_404(client, "especialidades", id_registro, id_inexistente)

    respuesta = client.post(
        f"/especialidades/{id_registro}/editar",
        data=datos_especialidad(
            registros_prueba,
            nombre_especialidad=f"{registros_prueba['nombre_especialidad']} EDITADA",
            descripcion="Descripción modificada.",
        ),
        follow_redirects=True,
    )
    assert "Especialidad actualizada correctamente" in respuesta.get_data(as_text=True)
    assert sql(
        test_config,
        "SELECT nombre_especialidad, descripcion FROM especialidades WHERE id_especialidad = %s",
        (id_registro,),
    ) == (f"{registros_prueba['nombre_especialidad']} EDITADA", "Descripción modificada.")

    respuesta = client.post(
        f"/especialidades/{id_registro}/eliminar", follow_redirects=True
    )
    assert "Especialidad eliminada" in respuesta.get_data(as_text=True)
    assert sql(
        test_config,
        "SELECT COUNT(*) FROM especialidades WHERE id_especialidad = %s",
        (id_registro,),
    )[0] == 0


def test_PF_02_especialidades_nombre_requerido_y_unico(
    client, test_config, registros_prueba
):
    comprobar_paginas_principales(client)
    crear_especialidad(client, test_config, registros_prueba)

    duplicado = client.post(
        "/especialidades/nuevo",
        data=datos_especialidad(registros_prueba),
    )
    assert "Ya existe un registro" in duplicado.get_data(as_text=True)

    vacio = client.post(
        "/especialidades/nuevo", data={"nombre_especialidad": "  "}
    )
    assert "es obligatorio" in vacio.get_data(as_text=True)


def test_PF_03_especialidad_referenciada_no_se_elimina(
    client, test_config, padres_prueba, registros_prueba
):
    crear_cita(client, test_config, registros_prueba, padres_prueba)
    respuesta = client.post(
        f"/especialidades/{padres_prueba['especialidad']}/eliminar",
        follow_redirects=True,
    )
    mensaje = textos_alertas(respuesta)
    assert "relacionado" in mensaje.casefold(), mensaje
    assert sql(
        test_config,
        "SELECT COUNT(*) FROM especialidades WHERE id_especialidad = %s",
        (padres_prueba["especialidad"],),
    )[0] == 1


def test_PF_04_servicios_ciclo_crud_listado_y_rutas(
    client, test_config, registros_prueba
):
    comprobar_paginas_principales(client)
    id_especialidad = crear_especialidad(client, test_config, registros_prueba)
    respuesta = client.post(
        "/servicios-medicos/nuevo",
        data=datos_servicio(registros_prueba, id_especialidad),
        follow_redirects=True,
    )
    assert "Servicio médico creado correctamente" in respuesta.get_data(as_text=True)
    id_registro = sql(
        test_config,
        "SELECT id_servicio FROM servicios_medicos WHERE nombre_servicio = %s",
        (registros_prueba["nombre_servicio"],),
    )[0]
    assert registros_prueba["nombre_servicio"] in client.get(
        "/servicios-medicos/"
    ).get_data(as_text=True)
    comprobar_edicion_y_404(
        client,
        "servicios-medicos",
        id_registro,
        siguiente_id(test_config, "servicios-medicos"),
    )

    respuesta = client.post(
        f"/servicios-medicos/{id_registro}/editar",
        data=datos_servicio(
            registros_prueba,
            id_especialidad,
            precio_consulta="999.50",
            duracion_minutos="45",
        ),
        follow_redirects=True,
    )
    assert "Servicio médico actualizado correctamente" in respuesta.get_data(as_text=True)
    assert sql(
        test_config,
        "SELECT precio_consulta, duracion_minutos FROM servicios_medicos WHERE id_servicio = %s",
        (id_registro,),
    ) == (Decimal("999.50"), 45)

    respuesta = client.post(
        f"/servicios-medicos/{id_registro}/eliminar", follow_redirects=True
    )
    assert "Servicio médico eliminado" in respuesta.get_data(as_text=True)
    assert sql(
        test_config,
        "SELECT COUNT(*) FROM servicios_medicos WHERE id_servicio = %s",
        (id_registro,),
    )[0] == 0


def test_PF_05_servicios_precio_duracion_formato_y_especialidad_invalidos(
    client, test_config, registros_prueba
):
    comprobar_paginas_principales(client)
    id_especialidad = crear_especialidad(client, test_config, registros_prueba)

    respuesta = client.post(
        "/servicios-medicos/nuevo",
        data=datos_servicio(
            registros_prueba,
            id_especialidad,
            precio_consulta="-5",
            duracion_minutos="0",
        ),
    )
    html = respuesta.get_data(as_text=True)
    assert "mayor o igual a 0" in html
    assert "mayor o igual a 1" in html

    respuesta = client.post(
        "/servicios-medicos/nuevo",
        data=datos_servicio(
            registros_prueba,
            id_especialidad,
            precio_consulta="abc",
        ),
    )
    assert "debe ser un número" in respuesta.get_data(as_text=True)

    respuesta = client.post(
        "/servicios-medicos/nuevo",
        data=datos_servicio(
            registros_prueba,
            "",
            precio_consulta="abc",
        ),
    )
    html = respuesta.get_data(as_text=True)
    assert "debe ser un número" in html
    assert "Especialidad" in html and "obligatorio" in html

    id_inexistente = siguiente_id(test_config, "especialidades")
    respuesta = client.post(
        "/servicios-medicos/nuevo",
        data=datos_servicio(registros_prueba, id_inexistente),
    )
    assert "relacionado" in respuesta.get_data(as_text=True)


def test_PF_06_servicio_referenciado_por_cita_no_se_elimina(
    client, test_config, padres_prueba, registros_prueba
):
    crear_cita(client, test_config, registros_prueba, padres_prueba)
    respuesta = client.post(
        f"/servicios-medicos/{padres_prueba['servicio']}/eliminar",
        follow_redirects=True,
    )
    mensaje = textos_alertas(respuesta)
    assert "relacionado" in mensaje.casefold(), mensaje
    assert sql(
        test_config,
        "SELECT COUNT(*) FROM servicios_medicos WHERE id_servicio = %s",
        (padres_prueba["servicio"],),
    )[0] == 1


def test_PF_07_pacientes_ciclo_crud_listado_y_rutas(
    client, test_config, registros_prueba
):
    comprobar_paginas_principales(client)
    id_registro = crear_paciente(client, test_config, registros_prueba)
    assert registros_prueba["etiqueta"] in client.get(
        "/pacientes/"
    ).get_data(as_text=True)
    comprobar_edicion_y_404(
        client, "pacientes", id_registro, siguiente_id(test_config, "pacientes")
    )

    respuesta = client.post(
        f"/pacientes/{id_registro}/editar",
        data=datos_paciente(
            registros_prueba,
            apellido="Paciente Actualizado",
            email="actualizado@example.test",
        ),
        follow_redirects=True,
    )
    assert "Paciente actualizado correctamente" in respuesta.get_data(as_text=True)
    assert sql(
        test_config,
        "SELECT apellido, email FROM pacientes WHERE id_paciente = %s",
        (id_registro,),
    ) == ("Paciente Actualizado", "actualizado@example.test")

    respuesta = client.post(
        f"/pacientes/{id_registro}/eliminar", follow_redirects=True
    )
    assert "Paciente eliminado" in respuesta.get_data(as_text=True)
    assert sql(
        test_config,
        "SELECT COUNT(*) FROM pacientes WHERE id_paciente = %s",
        (id_registro,),
    )[0] == 0


def test_PF_08_pacientes_formatos_valores_permitidos_y_documento_unico(
    client, test_config, registros_prueba
):
    comprobar_paginas_principales(client)
    crear_paciente(client, test_config, registros_prueba)

    duplicado = client.post(
        "/pacientes/nuevo",
        data=datos_paciente(registros_prueba, nombre="Otro nombre"),
    )
    assert "Ya existe un registro" in duplicado.get_data(as_text=True)

    invalido = client.post(
        "/pacientes/nuevo",
        data=datos_paciente(
            registros_prueba,
            numero_documento=f"ALT{registros_prueba['token']}",
            tipo_documento="XYZ",
            sexo="Otro",
            rh="ZZ",
            fecha_nacimiento="no-es-fecha",
            email="correo-invalido",
        ),
    )
    html = invalido.get_data(as_text=True)
    assert "Tipo de documento no válido" in html
    assert "Sexo no válido" in html
    assert "RH no válido" in html
    assert "fecha válida" in html
    assert "formato válido" in html


def test_PF_09_paciente_referenciado_por_cita_no_se_elimina(
    client, test_config, padres_prueba, registros_prueba
):
    crear_cita(client, test_config, registros_prueba, padres_prueba)
    respuesta = client.post(
        f"/pacientes/{padres_prueba['paciente']}/eliminar",
        follow_redirects=True,
    )
    mensaje = textos_alertas(respuesta)
    assert "relacionado" in mensaje.casefold(), mensaje
    assert sql(
        test_config,
        "SELECT COUNT(*) FROM pacientes WHERE id_paciente = %s",
        (padres_prueba["paciente"],),
    )[0] == 1


def test_PF_10_medicos_ciclo_crud_listado_y_rutas(
    client, test_config, registros_prueba
):
    comprobar_paginas_principales(client)
    id_registro = crear_medico(client, test_config, registros_prueba)
    assert registros_prueba["etiqueta"] in client.get(
        "/medicos/"
    ).get_data(as_text=True)
    comprobar_edicion_y_404(
        client, "medicos", id_registro, siguiente_id(test_config, "medicos")
    )

    respuesta = client.post(
        f"/medicos/{id_registro}/editar",
        data=datos_medico(registros_prueba, consultorio="TEST-2"),
        follow_redirects=True,
    )
    assert "Médico actualizado correctamente" in respuesta.get_data(as_text=True)
    assert sql(
        test_config,
        "SELECT consultorio FROM medicos WHERE id_medico = %s",
        (id_registro,),
    )[0] == "TEST-2"

    respuesta = client.post(
        f"/medicos/{id_registro}/eliminar", follow_redirects=True
    )
    assert "Médico eliminado" in respuesta.get_data(as_text=True)
    assert sql(
        test_config,
        "SELECT COUNT(*) FROM medicos WHERE id_medico = %s",
        (id_registro,),
    )[0] == 0


def test_PF_11_medicos_formatos_y_campos_unicos(
    client, test_config, registros_prueba
):
    comprobar_paginas_principales(client)
    id_existente = crear_medico(client, test_config, registros_prueba)

    invalido = client.post(
        "/medicos/nuevo",
        data=datos_medico(
            registros_prueba,
            numero_documento=f"ALT{registros_prueba['token']}",
            registro_medico=f"ALT-RM-{registros_prueba['token']}",
            email="correo-malo",
            tipo_documento="XYZ",
        ),
    )
    html = invalido.get_data(as_text=True)
    assert "Tipo de documento no válido" in html
    assert "formato válido" in html

    valores_unicos = {
        "numero_documento": registros_prueba["documento_medico"],
        "registro_medico": registros_prueba["registro_medico"],
        "email": registros_prueba["email_medico"],
    }
    for campo, valor in valores_unicos.items():
        datos = datos_medico(
            registros_prueba,
            numero_documento=f"ALT{registros_prueba['token']}",
            registro_medico=f"ALT-RM-{registros_prueba['token']}",
            email=f"alt-{registros_prueba['token'].lower()}@example.test",
        )
        datos[campo] = valor
        respuesta = client.post("/medicos/nuevo", data=datos)
        assert "Ya existe un registro" in respuesta.get_data(as_text=True), campo

    assert sql(
        test_config,
        "SELECT COUNT(*) FROM medicos WHERE id_medico = %s",
        (id_existente,),
    )[0] == 1


def test_PF_12_medico_referenciado_por_cita_no_se_elimina(
    client, test_config, padres_prueba, registros_prueba
):
    crear_cita(client, test_config, registros_prueba, padres_prueba)
    respuesta = client.post(
        f"/medicos/{padres_prueba['medico']}/eliminar",
        follow_redirects=True,
    )
    mensaje = textos_alertas(respuesta)
    assert "relacionado" in mensaje.casefold(), mensaje
    assert sql(
        test_config,
        "SELECT COUNT(*) FROM medicos WHERE id_medico = %s",
        (padres_prueba["medico"],),
    )[0] == 1


def test_PF_13_citas_ciclo_crud_listado_y_rutas(
    client, test_config, padres_prueba, registros_prueba
):
    comprobar_paginas_principales(client)
    id_registro = crear_cita(client, test_config, registros_prueba, padres_prueba)
    assert registros_prueba["etiqueta"] in client.get(
        "/citas/"
    ).get_data(as_text=True)
    comprobar_edicion_y_404(
        client, "citas", id_registro, siguiente_id(test_config, "citas")
    )

    respuesta = client.post(
        f"/citas/{id_registro}/editar",
        data=datos_cita(
            registros_prueba, padres_prueba, estado_cita="Atendida"
        ),
        follow_redirects=True,
    )
    assert "Cita médica actualizada correctamente" in respuesta.get_data(as_text=True)
    assert sql(
        test_config,
        "SELECT estado_cita FROM citas WHERE id_cita = %s",
        (id_registro,),
    )[0] == "Atendida"

    respuesta = client.post(
        f"/citas/{id_registro}/eliminar", follow_redirects=True
    )
    assert "Cita eliminada" in respuesta.get_data(as_text=True)
    assert sql(
        test_config,
        "SELECT COUNT(*) FROM citas WHERE id_cita = %s",
        (id_registro,),
    )[0] == 0


def test_PF_14_citas_fecha_campos_requeridos_y_estado_invalidos(
    client, test_config, padres_prueba, registros_prueba
):
    comprobar_paginas_principales(client)
    respuesta = client.post(
        "/citas/nuevo",
        data=datos_cita(
            registros_prueba,
            padres_prueba,
            fecha_hora="fecha-invalida",
            id_paciente="",
            id_servicio="",
            id_medico="",
            estado_cita="No existe",
        ),
    )
    html = respuesta.get_data(as_text=True)
    assert respuesta.status_code == 200
    assert "fecha y hora válidas" in html
    assert "obligatorio" in html
    assert "Estado de cita no válido" in html
    assert 'value="fecha-invalida"' in html


def test_PF_15_citas_rechaza_clave_foranea_inexistente(
    client, test_config, padres_prueba, registros_prueba
):
    comprobar_paginas_principales(client)
    id_inexistente = siguiente_id(test_config, "pacientes")
    respuesta = client.post(
        "/citas/nuevo",
        data=datos_cita(
            registros_prueba, padres_prueba, id_paciente=str(id_inexistente)
        ),
    )
    assert "relacionado" in respuesta.get_data(as_text=True)

    # El esquema no tiene tablas dependientes de citas, por lo que no existe
    # un caso de eliminación de cita referenciada que la aplicación deba cubrir.
    referencias_a_citas = sql(
        test_config,
        """SELECT COUNT(*)
           FROM information_schema.table_constraints tc
           JOIN information_schema.constraint_column_usage ccu
             ON ccu.constraint_catalog = tc.constraint_catalog
            AND ccu.constraint_schema = tc.constraint_schema
            AND ccu.constraint_name = tc.constraint_name
           WHERE tc.constraint_type = 'FOREIGN KEY'
             AND ccu.table_schema = 'public'
             AND ccu.table_name = 'citas'""",
    )[0]
    assert referencias_a_citas == 0
