# 🩺 Justificación de la Normalización (1FN, 2FN y 3FN)

> El diseño de la base de datos del consultorio médico ha sido estructurado y normalizado hasta la **Tercera Forma Normal (3FN)** para garantizar la consistencia de los datos, evitar redundancias y prevenir anomalías de actualización. A continuación se detalla el cumplimiento para cada una de las 5 tablas:

---

### 1. Tabla `especialidades`
* **Primera Forma Normal (1FN):** Todos los atributos (`nombre_especialidad`, `descripcion`) contienen valores atómicos e indivisibles. No existen grupos repetitivos ni columnas multivaluadas.
* **Segunda Forma Normal (2FN):** Cumple con la 1FN y posee una llave primaria simple (`id_especialidad`), por lo que no existen dependencias parciales.
* **Tercera Forma Normal (3FN):** Todos los atributos no clave dependen única y directamente de la llave primaria, sin dependencias transitivas entre ellos.

---

### 2. Tabla `servicios_medicos`
* **Primera Forma Normal (1FN):** Los campos (`nombre_servicio`, `precio_consulta`, `duracion_minutos`) almacenan valores atómicos y cada registro es una entidad independiente.
* **Segunda Forma Normal (2FN):** La tabla cuenta con una llave primaria simple (`id_servicio`), lo que elimina por completo cualquier dependencia parcial de los atributos respecto a una clave compuesta.
* **Tercera Forma Normal (3FN):** Los atributos descriptivos dependen exclusivamente de la llave primaria. La relación con su especialidad se maneja de forma normalizada mediante la llave foránea `id_especialidad`, sin duplicar información de la especialidad.

---

### 3. Tabla `pacientes`
* **Primera Forma Normal (1FN):** Los datos personales y de contacto (`tipo_documento`, `numero_documento`, `nombre`, `apellido`, `fecha_nacimiento`, `telefono`, `direccion`, `email`) son atómicos.
* **Segunda Forma Normal (2FN):** Al tener una llave primaria unimembre (`id_paciente`), se asegura que ningún atributo dependa de una parte de la clave.
* **Tercera Forma Normal (3FN):** No existen dependencias transitivas; los datos del paciente dependen de manera directa y exclusiva de su identificador único.

---

### 4. Tabla `medicos`
* **Primera Forma Normal (1FN):** Contiene únicamente valores escalares y atómicos para cada columna de identificación y contacto profesional.
* **Segunda Forma Normal (2FN):** Al estar soportada por una llave primaria simple (`id_medico`), cumple de forma natural con la ausencia de dependencias parciales.
* **Tercera Forma Normal (3FN):** Todos los atributos que componen el perfil del médico dependen directamente de la clave primaria, garantizando la atomicidad lógica de la entidad.

---

### 5. Tabla `citas` *(Tabla Intermedia)*
* **Primera Forma Normal (1FN):** Los atributos propios de la interacción (`fecha_hora`, `estado_cita`, `observaciones`) son atómicos y están claramente definidos.
* **Segunda Forma Normal (2FN):** Posee una llave primaria propia e independiente (`id_cita`), evitando dependencias parciales de los campos de la cita respecto a las llaves foráneas.
* **Tercera Forma Normal (3FN):** Actúa como el puente normalizado para resolver la relación de muchos a muchos entre pacientes, servicios médicos y médicos mediante las llaves foráneas (`id_paciente`, `id_servicio`, `id_medico`), asegurando que no existan dependencias transitivas entre los datos de la transacción.

# 🗂️ 2. Diccionario de Datos

## 2.1 Tabla: especialidades

| Campo | Tipo de dato | Restricciones | Descripción |
|---|---|---|---|
| id_especialidad | SERIAL | PK, NOT NULL | Identificador único secuencial de la especialidad médica. |
| nombre_especialidad | VARCHAR(100) | NOT NULL, UNIQUE | Nombre único de la especialidad (ej. Pediatría, Cardiología). |
| descripcion | TEXT | NULL | Descripción opcional sobre el alcance de la especialidad. |

## 2.2 Tabla: servicios_medicos

| Campo | Tipo de dato | Restricciones | Descripción |
|---|---|---|---|
| id_servicio | SERIAL | PK, NOT NULL | Identificador único secuencial del servicio médico. |
| nombre_servicio | VARCHAR(150) | NOT NULL | Nombre descriptivo del servicio brindado. |
| id_especialidad | INT | FK, NOT NULL | Llave foránea hacia la tabla especialidades. Restricción ON DELETE RESTRICT. |
| precio_consulta | NUMERIC(10,2) | NOT NULL, CHECK (precio_consulta >= 0) | Costo del servicio médico (debe ser mayor o igual a 0). |
| duracion_minutos | INT | CHECK (duracion_minutos > 0) | Duración estimada de la consulta en minutos. |

## 2.3 Tabla: pacientes

| Campo | Tipo de dato | Restricciones | Descripción |
|---|---|---|---|
| id_paciente | SERIAL | PK, NOT NULL | Identificador único secuencial del paciente. |
| tipo_documento | VARCHAR(5) | NOT NULL, CHECK (IN ('CC', 'TI', 'RC', 'CE', 'PA', 'PPT')) | Tipo de documento de identidad del paciente. |
| numero_documento | VARCHAR(20) | NOT NULL, UNIQUE | Número único de documento de identidad. |
| nombre | VARCHAR(100) | NOT NULL | Nombre(s) del paciente. |
| apellido | VARCHAR(100) | NOT NULL | Apellido(s) del paciente. |
| fecha_nacimiento | DATE | NOT NULL | Fecha de nacimiento utilizada para el cálculo exacto de edad. |
| telefono | VARCHAR(20) | NULL | Número telefónico de contacto del paciente o acudiente. |
| direccion | VARCHAR(200) | NULL | Dirección de residencia del paciente. |
| email | VARCHAR(150) | NULL | Correo electrónico de contacto del paciente. |

## 2.4 Tabla: medicos

| Campo | Tipo de dato | Restricciones | Descripción |
|---|---|---|---|
| id_medico | SERIAL | PK, NOT NULL | Identificador único secuencial del médico. |
| tipo_documento | VARCHAR(5) | NOT NULL, CHECK (IN ('CC', 'CE', 'PA', 'PPT')) | Tipo de documento de identidad del profesional médico. |
| numero_documento | VARCHAR(20) | NOT NULL, UNIQUE | Número de documento único del profesional médico. |
| nombre | VARCHAR(100) | NOT NULL | Nombre(s) del médico. |
| apellido | VARCHAR(100) | NOT NULL | Apellido(s) del médico. |
| registro_medico | VARCHAR(50) | NOT NULL, UNIQUE | Número de tarjeta o registro profesional médico único. |
| consultorio | VARCHAR(50) | NOT NULL | Identificador o número del consultorio asignado. |
| telefono_contacto | VARCHAR(20) | NOT NULL | Teléfono corporativo o de contacto del médico. |
| email | VARCHAR(150) | NOT NULL, UNIQUE | Correo electrónico institucional único del médico. |

## 2.5 Tabla: citas

| Campo | Tipo de dato | Restricciones | Descripción |
|---|---|---|---|
| id_cita | SERIAL | PK, NOT NULL | Identificador único secuencial de la cita médica. |
| fecha_hora | TIMESTAMP | NOT NULL | Fecha y hora programada para la cita médica. |
| id_paciente | INT | FK, NOT NULL | Llave foránea que referencia al paciente (pacientes.id_paciente). Restricción ON DELETE RESTRICT. |
| id_servicio | INT | FK, NOT NULL | Llave foránea que referencia al servicio médico (servicios_medicos.id_servicio). Restricción ON DELETE RESTRICT. |
| id_medico | INT | FK, NOT NULL | Llave foránea que referencia al médico asignado (medicos.id_medico). Restricción ON DELETE RESTRICT. |
| estado_cita | VARCHAR(50) | DEFAULT 'Programada', CHECK (IN ('Programada', 'Atendida', 'Cancelada')) | Estado actual de la cita médica. |
| observaciones | TEXT | NULL | Notas clínicas u observaciones adicionales sobre la cita. |