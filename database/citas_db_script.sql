-- =====================================================================
-- SCRIPT DE CREACIÓN Y CARGA DE DATOS: citas_medicas_db
-- Proyecto Final - Programación Web
-- =====================================================================

-- Eliminar tablas si ya existen para evitar conflictos en reinicios
DROP TABLE IF EXISTS citas CASCADE;
DROP TABLE IF EXISTS servicios_medicos CASCADE;
DROP TABLE IF EXISTS especialidades CASCADE;
DROP TABLE IF EXISTS pacientes CASCADE;
DROP TABLE IF EXISTS medicos CASCADE;

-- =====================================================================
-- 1. CREACIÓN DE TABLAS
-- =====================================================================

-- Tabla 1: especialidades
CREATE TABLE especialidades (
    id_especialidad SERIAL PRIMARY KEY,
    nombre_especialidad VARCHAR(100) UNIQUE NOT NULL,
    descripcion TEXT
);

-- Tabla 2: servicios_medicos (Depende de especialidades)
CREATE TABLE servicios_medicos (
    id_servicio SERIAL PRIMARY KEY,
    nombre_servicio VARCHAR(150) NOT NULL,
    id_especialidad INT NOT NULL,
    precio_consulta NUMERIC(10, 2) NOT NULL CHECK (precio_consulta >= 0),
    duracion_minutos INT CHECK (duracion_minutos > 0),
    CONSTRAINT fk_especialidad FOREIGN KEY (id_especialidad) 
        REFERENCES especialidades(id_especialidad) ON DELETE RESTRICT
);

-- Tabla 3: pacientes (Flexible para niños, adultos y extranjeros)
CREATE TABLE pacientes (
    id_paciente SERIAL PRIMARY KEY,
	tipo_documento VARCHAR(5) NOT NULL,
	numero_documento VARCHAR(20) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
	apellido VARCHAR(100) NOT NULL,
	sexo VARCHAR(10) NOT NULL,
	rh VARCHAR(5) NOT NULL, --Campo rh agregado
	fecha_nacimiento DATE NOT NULL, -- Clave para calcular la edad exacta siempre
    telefono VARCHAR(20),
    direccion VARCHAR(200),
    email VARCHAR(150) -- Opcional (NULL) y sin UNIQUE para familias o niños

	-- Restricción estricta de documentos válidos (incluyendo Registro Civil y Tarjeta de Identidad)
	CONSTRAINT ck_tipo_documento_paciente 
        CHECK (tipo_documento IN ('CC', 'TI', 'RC', 'CE', 'PA', 'PPT'))

	-- Restricción para asegurar que el RH ingresado sea válido en el sistema médico
    CONSTRAINT ck_rh_paciente 
        CHECK (rh IN ('O+', 'O-', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-'))

	CONSTRAINT ck_sexo_paciente 
        CHECK (sexo IN ('Masculino', 'Femenino'))
);

-- Tabla 4: medicos
CREATE TABLE medicos (
    id_medico SERIAL PRIMARY KEY,
	tipo_documento VARCHAR(5) NOT NULL,
	numero_documento VARCHAR(20) UNIQUE NOT NULL,
	nombre VARCHAR(100) NOT NULL,
	apellido VARCHAR(100) NOT NULL,
	registro_medico VARCHAR(50) UNIQUE NOT NULL,
    consultorio VARCHAR(10) NOT NULL,
    telefono_contacto VARCHAR(20) NOT NULL,
	email VARCHAR(150) UNIQUE NOT NULL,

	CONSTRAINT ck_tipo_doc_medico 
        CHECK (tipo_documento IN ('CC', 'CE', 'PA', 'PPT'))
);

-- Tabla 5: citas (Tabla central con múltiples llaves foráneas)
CREATE TABLE citas (
    id_cita SERIAL PRIMARY KEY,
    fecha_hora TIMESTAMP NOT NULL,
    id_paciente INT NOT NULL,
    id_servicio INT NOT NULL,
    id_medico INT NOT NULL,
    estado_cita VARCHAR(50) DEFAULT 'Programada' CHECK (estado_cita IN ('Programada', 'Atendida', 'Cancelada')),
    observaciones TEXT,
    CONSTRAINT fk_cita_paciente FOREIGN KEY (id_paciente) 
        REFERENCES pacientes(id_paciente) ON DELETE RESTRICT,
    CONSTRAINT fk_cita_servicio FOREIGN KEY (id_servicio) 
        REFERENCES servicios_medicos(id_servicio) ON DELETE RESTRICT,
    CONSTRAINT fk_cita_medico FOREIGN KEY (id_medico) 
        REFERENCES medicos(id_medico) ON DELETE RESTRICT
);


-- =====================================================================
-- 2. INSERCIÓN DE DATOS (Mínimo 10 registros por tabla)
-- =====================================================================

-- Inserciones en especialidades
INSERT INTO especialidades (nombre_especialidad, descripcion) VALUES
('Cardiología', 'Estudio y tratamiento de las enfermedades del corazón y del aparato circulatorio.'),
('Pediatría', 'Atención médica especializada en niños, niñas y adolescentes.'),
('Dermatología', 'Diagnóstico y tratamiento de afecciones de la piel, mucosas, cabello y uñas.'),
('Neurología', 'Trastornos del sistema nervioso central y periférico.'),
('Oftalmología', 'Estudio de las enfermedades del ojo y su tratamiento.'),
('Ortopedia', 'Tratamiento de lesiones del sistema musculoesquelético.'),
('Medicina General', 'Atención primaria y prevención integral de la salud.'),
('Ginecología', 'Salud del sistema reproductor femenino y embarazo.'),
('Psiquiatría', 'Prevención, diagnóstico y tratamiento de trastornos mentales.'),
('Odontología', 'Cuidado y salud integral de la cavidad oral y dientes.');

-- Inserciones en servicios_medicos
INSERT INTO servicios_medicos (nombre_servicio, id_especialidad, precio_consulta, duracion_minutos) VALUES
('Electrocardiograma', 1, 120000.00, 30),
('Control Pediátrico Mensual', 2, 90000.00, 20),
('Biopsia de Piel', 3, 150000.00, 40),
('Electroencefalograma', 4, 200000.00, 45),
('Examen de Optometría y Agudeza', 5, 70000.00, 20),
('Inmovilización y Yeso', 6, 130000.00, 30),
('Consulta Médica General', 7, 60000.00, 20),
('Ecografía Obstétrica', 8, 180000.00, 30),
('Terapia Psicológica Individual', 9, 110000.00, 50),
('Limpieza Dental Profunda', 10, 80000.00, 30);

-- Inserciones en pacientes (Con su respectivo sexo incluido en orden)
INSERT INTO pacientes (tipo_documento, numero_documento, nombre, apellido, sexo, rh, fecha_nacimiento, telefono, direccion, email) VALUES
('CC', '1001234567', 'Carlos', 'Pérez', 'Masculino', 'O+', '1995-03-12', '3101234567', 'Calle 10 # 15-20', 'carlos.perez@email.com'),
('CC', '1002345678', 'María', 'Rodríguez', 'Femenino', 'A+', '1990-07-22', '3112345678', 'Carrera 5 # 20-30', 'maria.rodriguez@email.com'),
('TI', '1003456789', 'Juan', 'Gómez', 'Masculino', 'B+', '2010-05-15', '3123456789', 'Avenida Circunvalar # 8-12', 'juan.gomez@email.com'),
('CC', '1004567890', 'Ana', 'Torres', 'Femenino', 'AB+', '1988-11-04', '3134567890', 'Calle 25 # 3-45', 'ana.torres@email.com'),
('CC', '1005678901', 'Luis', 'Martínez', 'Masculino', 'O-', '1992-01-30', '3145678901', 'Carrera 12 # 45-60', 'luis.martinez@email.com'),
('CC', '1006789012', 'Diana', 'Sánchez', 'Femenino', 'A-', '1998-09-18', '3156789012', 'Calle 8 # 11-22', 'diana.sanchez@email.com'),
('CC', '1007890123', 'Pedro', 'Ramírez', 'Masculino', 'B-', '1985-12-05', '3167890123', 'Carrera 20 # 30-40', 'pedro.ramirez@email.com'),
('RC', '1008901234', 'Sofía', 'Herrera', 'Femenino', 'O+', '2024-02-10', '3178901234', 'Calle 2 # 5-18', NULL),
('CC', '1009012345', 'Andrés', 'Castro', 'Masculino', 'AB-', '1993-06-25', '3189012345', 'Carrera 7 # 14-88', 'andres.castro@email.com'),
('TI', '1010123456', 'Valentina', 'Vargas', 'Femenino', 'O+', '2012-08-30', '3190123456', 'Calle 30 # 22-10', 'valentina.vargas@email.com');

-- Inserciones en medicos (Actualizado con solo el número de consultorio limpio)
INSERT INTO medicos (tipo_documento, numero_documento, nombre, apellido, registro_medico, consultorio, telefono_contacto, email) VALUES
('CC', '80111222', 'Alberto', 'Mendoza', 'RM-90111', '101', '3201112233', 'alberto.mendoza@email.com'),
('CC', '80222333', 'Elena', 'Ríos', 'RM-90222', '102', '3202223344', 'elena.rios@email.com'),
('CC', '80333444', 'Jorge', 'Cárdenas', 'RM-90333', '103', '3203334455', 'jorge.cardenas@email.com'),
('CC', '80444555', 'Marcela', 'Gómez', 'RM-90444', '104', '3204445566', 'marcela.gomez@email.com'),
('CC', '80555666', 'Ricardo', 'Silva', 'RM-90555', '201', '3205556677', 'ricardo.silva@email.com'),
('CC', '80666777', 'Claudia', 'Patiño', 'RM-90666', '202', '3206667788', 'claudia.patino@email.com'),
('CC', '80777888', 'Fernando', 'Torres', 'RM-90777', '203', '3207778899', 'fernando.torres@email.com'),
('CC', '80888999', 'Lucía', 'Morales', 'RM-90888', '204', '3208889900', 'lucia.morales@email.com'),
('CC', '80999000', 'Gabriel', 'Rojas', 'RM-90999', '301', '3209990011', 'gabriel.rojas@email.com'),
('CC', '80000111', 'Andrea', 'Jiménez', 'RM-90000', '302', '3200001122', 'andrea.jimenez@email.com');

-- Inserciones en citas (Tabla central que une pacientes, servicios y médicos)
INSERT INTO citas (fecha_hora, id_paciente, id_servicio, id_medico, estado_cita, observaciones) VALUES
('2026-11-05 08:00:00', 1, 1, 1, 'Programada', 'Paciente con antecedentes de hipertensión arterial.'),
('2026-11-05 09:00:00', 2, 2, 2, 'Programada', 'Control de crecimiento mensual infantil.'),
('2026-11-06 10:30:00', 3, 3, 3, 'Atendida', 'Revisión general de manchas y lunares.'),
('2026-11-06 11:15:00', 4, 4, 4, 'Programada', 'Evaluación por dolores de cabeza recurrentes.'),
('2026-11-07 14:00:00', 5, 5, 5, 'Cancelada', 'Paciente reprograma cita por motivos laborales.'),
('2026-11-07 15:30:00', 6, 6, 6, 'Programada', 'Dolor en rodilla derecha tras práctica deportiva.'),
('2026-11-08 08:30:00', 7, 7, 7, 'Atendida', 'Chequeo general anual de rutina.'),
('2026-11-08 09:45:00', 8, 8, 8, 'Programada', 'Control periódico de primer trimestre.'),
('2026-11-09 10:00:00', 9, 9, 9, 'Programada', 'Sesión inicial de manejo de estrés y ansiedad.'),
('2026-11-09 11:30:00', 10, 10, 10, 'Atendida', 'Remoción de placa bacteriana y profilaxis.');