# Plan de pruebas funcionales

## Alcance y resultado de ejecución

Plan de 15 casos, tres por tabla, acorde con la rúbrica. La salida de `pytest --collect-only` confirmó **15 casos recopilados**. La ejecución completa se hizo con `TEST_DB_NAME=consultorio_medico_test_db`, distinta de la base de desarrollo `consultorio_medico_db`: **15 aprobadas, 0 fallidas** (`15 passed in 19.56s`).

Los resultados de esta columna corresponden a aserciones reales de pytest; se indica la prueba automatizada que los demuestra. Las capturas de pantalla solicitadas aún están pendientes: no se registran como evidencia existente ni se presentan como si se hubieran tomado. Cuando se obtengan, deben guardarse en `docs/evidencias/` con los nombres indicados.

## Especialidades

### PF-01 — Ciclo CRUD de especialidad
- **Tabla:** `especialidades`
- **Operación/escenario:** Crear una especialidad, comprobarla en el listado, editarla y eliminarla.
- **Datos de entrada:** Nombre `ZZ_TEST_<token> ESPECIALIDAD`; descripción inicial de prueba; nombre editado con sufijo `EDITADA` y descripción vacía.
- **Resultado esperado:** La creación, actualización y eliminación muestran sus mensajes de éxito; el listado contiene el registro creado; los valores editados quedan persistidos y la fila desaparece al eliminarla.
- **Resultado obtenido real:** `test_PF_01_especialidades_ciclo_crud_listado_y_rutas` verificó creación, listado, formulario de edición, 404 para ID inexistente, actualización persistida y eliminación. También comprobó la carga de inicio, los listados y formularios de alta.
- **Evidencia:** Pendiente de captura visual: `docs/evidencias/PF-01.png`.

### PF-02 — Nombre requerido y duplicado
- **Tabla:** `especialidades`
- **Operación/escenario:** Intentar crear un nombre ya registrado y enviar vacío el nombre requerido.
- **Datos de entrada:** Nombre único generado para pytest; duplicado del mismo nombre; después, espacios en blanco.
- **Resultado esperado:** La aplicación rechaza el duplicado y comunica que el campo es obligatorio cuando está vacío.
- **Resultado obtenido real:** `test_PF_02_especialidades_nombre_requerido_y_unico` verificó ambos mensajes y las páginas principales.
- **Evidencia:** Pendiente de captura visual: `docs/evidencias/PF-02.png`.

### PF-03 — Eliminar especialidad usada
- **Tabla:** `especialidades`
- **Operación/escenario:** Intentar eliminar una especialidad referenciada por un servicio médico.
- **Datos de entrada:** Especialidad de prueba con servicio dependiente y cita asociada.
- **Resultado esperado:** La clave foránea impide la eliminación, la especialidad permanece y se informa que tiene registros relacionados.
- **Resultado obtenido real:** `test_PF_03_especialidad_referenciada_no_se_elimina` comprobó el mensaje y que la especialidad sigue en la base de pruebas.
- **Evidencia:** Pendiente de captura visual: `docs/evidencias/PF-03.png`.

## Servicios médicos

### PF-04 — Ciclo CRUD de servicio
- **Tabla:** `servicios_medicos`
- **Operación/escenario:** Crear un servicio, comprobarlo en el listado, actualizar precio y duración, y eliminarlo.
- **Datos de entrada:** Servicio `ZZ_TEST_<token> SERVICIO`, especialidad válida, precio `12345.50`, duración `30`; edición a `999.50` y `45` minutos.
- **Resultado esperado:** El servicio aparece en el listado, los cambios quedan persistidos y la eliminación lo retira del listado.
- **Resultado obtenido real:** `test_PF_04_servicios_ciclo_crud_listado_y_rutas` verificó creación, listado, formulario de edición, 404 para ID inexistente, valores actualizados persistidos y eliminación.
- **Evidencia:** Pendiente de captura visual: `docs/evidencias/PF-04.png`.

### PF-05 — Precio, duración y especialidad inválidos
- **Tabla:** `servicios_medicos`
- **Operación/escenario:** Envío de valores numéricos inválidos y, en una solicitud separada con los demás datos válidos, referencia a especialidad inexistente.
- **Datos de entrada:** Precio `-5`, duración `0`; precio `abc`; precio no numérico con especialidad vacía; luego precio y duración válidos con un ID de especialidad inexistente.
- **Resultado esperado:** Se muestran validaciones de rango/formato y la referencia inexistente se rechaza por integridad referencial.
- **Resultado obtenido real:** `test_PF_05_servicios_precio_duracion_formato_y_especialidad_invalidos` verificó por separado precio/duración fuera de rango, formato numérico, especialidad obligatoria y especialidad inexistente.
- **Evidencia:** Pendiente de captura visual: `docs/evidencias/PF-05.png`.

### PF-06 — Eliminar servicio usado por una cita
- **Tabla:** `servicios_medicos`
- **Operación/escenario:** Intentar eliminar un servicio asignado a una cita existente.
- **Datos de entrada:** Servicio y cita de prueba con paciente, médico y especialidad válidos.
- **Resultado esperado:** La FK impide eliminar el servicio; permanece en la base y aparece un mensaje comprensible de registro relacionado.
- **Resultado obtenido real:** `test_PF_06_servicio_referenciado_por_cita_no_se_elimina` verificó el mensaje y la permanencia del servicio.
- **Evidencia:** Pendiente de captura visual: `docs/evidencias/PF-06.png`.

## Pacientes

### PF-07 — Ciclo CRUD de paciente
- **Tabla:** `pacientes`
- **Operación/escenario:** Crear un paciente, comprobarlo en el listado, editar apellido y correo y eliminarlo.
- **Datos de entrada:** Documento y correo únicos generados para la ejecución, datos personales válidos; edición del apellido y correo vacío.
- **Resultado esperado:** El paciente aparece en el listado, los cambios quedan persistidos y la fila se elimina correctamente.
- **Resultado obtenido real:** `test_PF_07_pacientes_ciclo_crud_listado_y_rutas` verificó creación, listado, formulario de edición, 404 para ID inexistente, valores actualizados persistidos y eliminación.
- **Evidencia:** Pendiente de captura visual: `docs/evidencias/PF-07.png`.

### PF-08 — Datos personales y correo inválidos
- **Tabla:** `pacientes`
- **Operación/escenario:** Enviar valores que no pertenecen a las opciones permitidas y formatos inválidos.
- **Datos de entrada:** Tipo de documento `XYZ`, sexo `Otro`, RH `ZZ`, fecha `no-es-fecha` y correo `correo-invalido`.
- **Resultado esperado:** El formulario rechaza cada valor y comunica las validaciones correspondientes.
- **Resultado obtenido real:** `test_PF_08_pacientes_formatos_valores_permitidos_y_documento_unico` comprobó el duplicado y los cinco mensajes de validación.
- **Evidencia:** Pendiente de captura visual: `docs/evidencias/PF-08.png`.

### PF-09 — Eliminar paciente con cita
- **Tabla:** `pacientes`
- **Operación/escenario:** Intentar eliminar un paciente referenciado por una cita.
- **Datos de entrada:** Paciente y cita de prueba vinculados.
- **Resultado esperado:** La FK impide la eliminación; el paciente permanece y se informa que está relacionado.
- **Resultado obtenido real:** `test_PF_09_paciente_referenciado_por_cita_no_se_elimina` verificó el mensaje y la permanencia del paciente.
- **Evidencia:** Pendiente de captura visual: `docs/evidencias/PF-09.png`.

## Médicos

### PF-10 — Ciclo CRUD de médico
- **Tabla:** `medicos`
- **Operación/escenario:** Crear un médico, comprobarlo en el listado, cambiar consultorio y eliminarlo.
- **Datos de entrada:** Documento, registro profesional y correo únicos; consultorio inicial `TEST-1`, actualizado a `TEST-2`.
- **Resultado esperado:** El listado muestra el médico, el cambio queda persistido y se elimina correctamente.
- **Resultado obtenido real:** `test_PF_10_medicos_ciclo_crud_listado_y_rutas` verificó creación, listado, formulario de edición, 404 para ID inexistente, actualización persistida y eliminación.
- **Evidencia:** Pendiente de captura visual: `docs/evidencias/PF-10.png`.

### PF-11 — Tipo de documento, correo y datos únicos
- **Tabla:** `medicos`
- **Operación/escenario:** Rechazar tipo de documento y correo inválidos, y valores duplicados en documento, registro profesional o correo.
- **Datos de entrada:** Tipo `XYZ`, correo `correo-malo`; duplicados de cada uno de los tres campos únicos.
- **Resultado esperado:** El formulario muestra errores de formato y evita insertar valores únicos repetidos.
- **Resultado obtenido real:** `test_PF_11_medicos_formatos_y_campos_unicos` verificó formato inválido y los duplicados de documento, registro profesional y correo en un único caso pytest.
- **Evidencia:** Pendiente de captura visual: `docs/evidencias/PF-11.png`.

### PF-12 — Eliminar médico con cita
- **Tabla:** `medicos`
- **Operación/escenario:** Intentar eliminar un médico que atiende una cita existente.
- **Datos de entrada:** Médico y cita de prueba relacionados.
- **Resultado esperado:** La FK impide la eliminación; el médico permanece y se informa que está relacionado.
- **Resultado obtenido real:** `test_PF_12_medico_referenciado_por_cita_no_se_elimina` verificó el mensaje y la permanencia del médico.
- **Evidencia:** Pendiente de captura visual: `docs/evidencias/PF-12.png`.

## Citas

### PF-13 — Ciclo CRUD de cita
- **Tabla:** `citas`
- **Operación/escenario:** Crear una cita, comprobarla en el listado, cambiar estado y eliminarla.
- **Datos de entrada:** Fecha `2099-01-01T10:00`, paciente/servicio/médico existentes, estado `Programada`; edición a `Atendida`.
- **Resultado esperado:** La cita aparece en el listado, se persiste el estado actualizado y se elimina correctamente.
- **Resultado obtenido real:** `test_PF_13_citas_ciclo_crud_listado_y_rutas` verificó creación, listado, formulario de edición, 404 para ID inexistente, estado actualizado persistido y eliminación.
- **Evidencia:** Pendiente de captura visual: `docs/evidencias/PF-13.png`.

### PF-14 — Fecha, relaciones y estado inválidos
- **Tabla:** `citas`
- **Operación/escenario:** Enviar fecha inválida, claves foráneas vacías y estado no permitido.
- **Datos de entrada:** Fecha `fecha-invalida`, paciente/servicio/médico vacíos, estado `No existe`.
- **Resultado esperado:** El formulario conserva los valores enviados y presenta las validaciones de fecha, campos requeridos y estado.
- **Resultado obtenido real:** `test_PF_14_citas_fecha_campos_requeridos_y_estado_invalidos` pasó; comprobó errores, respuesta del formulario y conservación/renderizado del valor de fecha enviado como texto.
- **Evidencia:** Pendiente de captura visual: `docs/evidencias/PF-14.png`.

### PF-15 — Clave foránea inexistente y alcance de eliminación
- **Tabla:** `citas`
- **Operación/escenario:** Intentar crear una cita con paciente inexistente. No aplica el escenario de eliminar una cita referenciada: ninguna tabla del esquema tiene una FK que apunte a `citas`.
- **Datos de entrada:** Fecha, estado, servicio y médico válidos; ID de paciente inexistente.
- **Resultado esperado:** La base rechaza la relación inexistente y la aplicación informa el error. La ausencia de registros hijos de citas se documenta como limitación del esquema, no como una relación que la app deba soportar.
- **Resultado obtenido real:** `test_PF_15_citas_rechaza_clave_foranea_inexistente` comprobó el rechazo y el mensaje de relación inválida, y consultó el esquema para verificar que no hay tablas que referencien a `citas`.
- **Evidencia:** Pendiente de captura visual: `docs/evidencias/PF-15.png`.