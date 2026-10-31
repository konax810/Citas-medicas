--
-- PostgreSQL database dump
--

\restrict BE0cKMzsjTcOJt30PuZkY3b7jmIGuflSD9IghokqP1R3ycXev8mlqcCAMfwudmi

-- Dumped from database version 17.11
-- Dumped by pg_dump version 17.11

-- Started on 2026-10-31 11:30:20

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 226 (class 1259 OID 49395)
-- Name: citas; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.citas (
    id_cita integer NOT NULL,
    fecha_hora timestamp without time zone NOT NULL,
    id_paciente integer NOT NULL,
    id_servicio integer NOT NULL,
    id_medico integer NOT NULL,
    estado_cita character varying(50) DEFAULT 'Programada'::character varying,
    observaciones text,
    CONSTRAINT citas_estado_cita_check CHECK (((estado_cita)::text = ANY ((ARRAY['Programada'::character varying, 'Atendida'::character varying, 'Cancelada'::character varying])::text[])))
);


ALTER TABLE public.citas OWNER TO postgres;

--
-- TOC entry 225 (class 1259 OID 49394)
-- Name: citas_id_cita_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.citas_id_cita_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.citas_id_cita_seq OWNER TO postgres;

--
-- TOC entry 4949 (class 0 OID 0)
-- Dependencies: 225
-- Name: citas_id_cita_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.citas_id_cita_seq OWNED BY public.citas.id_cita;


--
-- TOC entry 218 (class 1259 OID 49352)
-- Name: especialidades; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.especialidades (
    id_especialidad integer NOT NULL,
    nombre_especialidad character varying(100) NOT NULL,
    descripcion text
);


ALTER TABLE public.especialidades OWNER TO postgres;

--
-- TOC entry 217 (class 1259 OID 49351)
-- Name: especialidades_id_especialidad_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.especialidades_id_especialidad_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.especialidades_id_especialidad_seq OWNER TO postgres;

--
-- TOC entry 4950 (class 0 OID 0)
-- Dependencies: 217
-- Name: especialidades_id_especialidad_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.especialidades_id_especialidad_seq OWNED BY public.especialidades.id_especialidad;


--
-- TOC entry 224 (class 1259 OID 49388)
-- Name: medicos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.medicos (
    id_medico integer NOT NULL,
    nombre_medico character varying(150) NOT NULL,
    consultorio character varying(50) NOT NULL,
    telefono_contacto character varying(20)
);


ALTER TABLE public.medicos OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 49387)
-- Name: medicos_id_medico_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.medicos_id_medico_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.medicos_id_medico_seq OWNER TO postgres;

--
-- TOC entry 4951 (class 0 OID 0)
-- Dependencies: 223
-- Name: medicos_id_medico_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.medicos_id_medico_seq OWNED BY public.medicos.id_medico;


--
-- TOC entry 222 (class 1259 OID 49377)
-- Name: pacientes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pacientes (
    id_paciente integer NOT NULL,
    nombre_paciente character varying(150) NOT NULL,
    telefono character varying(20),
    direccion character varying(200),
    email character varying(150) NOT NULL
);


ALTER TABLE public.pacientes OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 49376)
-- Name: pacientes_id_paciente_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.pacientes_id_paciente_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.pacientes_id_paciente_seq OWNER TO postgres;

--
-- TOC entry 4952 (class 0 OID 0)
-- Dependencies: 221
-- Name: pacientes_id_paciente_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.pacientes_id_paciente_seq OWNED BY public.pacientes.id_paciente;


--
-- TOC entry 220 (class 1259 OID 49363)
-- Name: servicios_medicos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.servicios_medicos (
    id_servicio integer NOT NULL,
    nombre_servicio character varying(150) NOT NULL,
    id_especialidad integer NOT NULL,
    precio_consulta numeric(10,2),
    duracion_minutos integer,
    CONSTRAINT servicios_medicos_duracion_minutos_check CHECK ((duracion_minutos > 0)),
    CONSTRAINT servicios_medicos_precio_consulta_check CHECK ((precio_consulta >= (0)::numeric))
);


ALTER TABLE public.servicios_medicos OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 49362)
-- Name: servicios_medicos_id_servicio_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.servicios_medicos_id_servicio_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.servicios_medicos_id_servicio_seq OWNER TO postgres;

--
-- TOC entry 4953 (class 0 OID 0)
-- Dependencies: 219
-- Name: servicios_medicos_id_servicio_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.servicios_medicos_id_servicio_seq OWNED BY public.servicios_medicos.id_servicio;


--
-- TOC entry 4766 (class 2604 OID 49398)
-- Name: citas id_cita; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.citas ALTER COLUMN id_cita SET DEFAULT nextval('public.citas_id_cita_seq'::regclass);


--
-- TOC entry 4762 (class 2604 OID 49355)
-- Name: especialidades id_especialidad; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.especialidades ALTER COLUMN id_especialidad SET DEFAULT nextval('public.especialidades_id_especialidad_seq'::regclass);


--
-- TOC entry 4765 (class 2604 OID 49391)
-- Name: medicos id_medico; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.medicos ALTER COLUMN id_medico SET DEFAULT nextval('public.medicos_id_medico_seq'::regclass);


--
-- TOC entry 4764 (class 2604 OID 49380)
-- Name: pacientes id_paciente; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pacientes ALTER COLUMN id_paciente SET DEFAULT nextval('public.pacientes_id_paciente_seq'::regclass);


--
-- TOC entry 4763 (class 2604 OID 49366)
-- Name: servicios_medicos id_servicio; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.servicios_medicos ALTER COLUMN id_servicio SET DEFAULT nextval('public.servicios_medicos_id_servicio_seq'::regclass);


--
-- TOC entry 4943 (class 0 OID 49395)
-- Dependencies: 226
-- Data for Name: citas; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.citas (id_cita, fecha_hora, id_paciente, id_servicio, id_medico, estado_cita, observaciones) FROM stdin;
1	2026-11-05 08:00:00	1	1	1	Programada	Paciente con antecedentes de hipertensión arterial.
2	2026-11-05 09:00:00	2	2	2	Programada	Control de crecimiento mensual infantil.
3	2026-11-06 10:30:00	3	3	3	Atendida	Revisión general de manchas y lunares.
4	2026-11-06 11:15:00	4	4	4	Programada	Evaluación por dolores de cabeza recurrentes.
5	2026-11-07 14:00:00	5	5	5	Cancelada	Paciente reprograma cita por motivos laborales.
6	2026-11-07 15:30:00	6	6	6	Programada	Dolor en rodilla derecha tras práctica deportiva.
7	2026-11-08 08:30:00	7	7	7	Atendida	Chequeo general anual de rutina.
8	2026-11-08 09:45:00	8	8	8	Programada	Control periódico de primer trimestre.
9	2026-11-09 10:00:00	9	9	9	Programada	Sesión inicial de manejo de estrés y ansiedad.
10	2026-11-09 11:30:00	10	10	10	Atendida	Remoción de placa bacteriana y profilaxis.
\.


--
-- TOC entry 4935 (class 0 OID 49352)
-- Dependencies: 218
-- Data for Name: especialidades; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.especialidades (id_especialidad, nombre_especialidad, descripcion) FROM stdin;
1	Cardiología	Estudio y tratamiento de las enfermedades del corazón y del aparato circulatorio.
2	Pediatría	Atención médica especializada en niños, niñas y adolescentes.
3	Dermatología	Diagnóstico y tratamiento de afecciones de la piel, mucosas, cabello y uñas.
4	Neurología	Trastornos del sistema nervioso central y periférico.
5	Oftalmología	Estudio de las enfermedades del ojo y su tratamiento.
6	Ortopedia	Tratamiento de lesiones del sistema musculoesquelético.
7	Medicina General	Atención primaria y prevención integral de la salud.
8	Ginecología	Salud del sistema reproductor femenino y embarazo.
9	Psiquiatría	Prevención, diagnóstico y tratamiento de trastornos mentales.
10	Odontología	Cuidado y salud integral de la cavidad oral y dientes.
\.


--
-- TOC entry 4941 (class 0 OID 49388)
-- Dependencies: 224
-- Data for Name: medicos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.medicos (id_medico, nombre_medico, consultorio, telefono_contacto) FROM stdin;
1	Dr. Alberto Mendoza	Consultorio 101	3201112233
2	Dra. Elena Ríos	Consultorio 102	3202223344
3	Dr. Jorge Cárdenas	Consultorio 103	3203334455
4	Dra. Marcela Gómez	Consultorio 104	3204445566
5	Dr. Ricardo Silva	Consultorio 201	3205556677
6	Dra. Claudia Patiño	Consultorio 202	3206667788
7	Dr. Fernando Torres	Consultorio 203	3207778899
8	Dra. Lucía Morales	Consultorio 204	3208889900
9	Dr. Gabriel Rojas	Consultorio 301	3209990011
10	Dra. Andrea Jiménez	Consultorio 302	3200001122
\.


--
-- TOC entry 4939 (class 0 OID 49377)
-- Dependencies: 222
-- Data for Name: pacientes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.pacientes (id_paciente, nombre_paciente, telefono, direccion, email) FROM stdin;
1	Carlos Pérez	3101234567	Calle 10 # 15-20	carlos.perez@email.com
2	María Rodríguez	3112345678	Carrera 5 # 20-30	maria.rodriguez@email.com
3	Juan Gómez	3123456789	Avenida Circunvalar # 8-12	juan.gomez@email.com
4	Ana Torres	3134567890	Calle 25 # 3-45	ana.torres@email.com
5	Luis Martínez	3145678901	Carrera 12 # 45-60	luis.martinez@email.com
6	Diana Sánchez	3156789012	Calle 8 # 11-22	diana.sanchez@email.com
7	Pedro Ramírez	3167890123	Carrera 20 # 30-40	pedro.ramirez@email.com
8	Sofía Herrera	3178901234	Calle 2 # 5-18	sofia.herrera@email.com
9	Andrés Castro	3189012345	Carrera 7 # 14-88	andres.castro@email.com
10	Valentina Vargas	3190123456	Calle 30 # 22-10	valentina.vargas@email.com
\.


--
-- TOC entry 4937 (class 0 OID 49363)
-- Dependencies: 220
-- Data for Name: servicios_medicos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.servicios_medicos (id_servicio, nombre_servicio, id_especialidad, precio_consulta, duracion_minutos) FROM stdin;
1	Electrocardiograma	1	120000.00	30
2	Control Pediátrico Mensual	2	90000.00	20
3	Biopsia de Piel	3	150000.00	40
4	Electroencefalograma	4	200000.00	45
5	Examen de Optometría y Agudeza	5	70000.00	20
6	Inmovilización y Yeso	6	130000.00	30
7	Consulta Médica General	7	60000.00	20
8	Ecografía Obstétrica	8	180000.00	30
9	Terapia Psicológica Individual	9	110000.00	50
10	Limpieza Dental Profunda	10	80000.00	30
\.


--
-- TOC entry 4954 (class 0 OID 0)
-- Dependencies: 225
-- Name: citas_id_cita_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.citas_id_cita_seq', 10, true);


--
-- TOC entry 4955 (class 0 OID 0)
-- Dependencies: 217
-- Name: especialidades_id_especialidad_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.especialidades_id_especialidad_seq', 10, true);


--
-- TOC entry 4956 (class 0 OID 0)
-- Dependencies: 223
-- Name: medicos_id_medico_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.medicos_id_medico_seq', 10, true);


--
-- TOC entry 4957 (class 0 OID 0)
-- Dependencies: 221
-- Name: pacientes_id_paciente_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.pacientes_id_paciente_seq', 10, true);


--
-- TOC entry 4958 (class 0 OID 0)
-- Dependencies: 219
-- Name: servicios_medicos_id_servicio_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.servicios_medicos_id_servicio_seq', 10, true);


--
-- TOC entry 4784 (class 2606 OID 49404)
-- Name: citas citas_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.citas
    ADD CONSTRAINT citas_pkey PRIMARY KEY (id_cita);


--
-- TOC entry 4772 (class 2606 OID 49361)
-- Name: especialidades especialidades_nombre_especialidad_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.especialidades
    ADD CONSTRAINT especialidades_nombre_especialidad_key UNIQUE (nombre_especialidad);


--
-- TOC entry 4774 (class 2606 OID 49359)
-- Name: especialidades especialidades_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.especialidades
    ADD CONSTRAINT especialidades_pkey PRIMARY KEY (id_especialidad);


--
-- TOC entry 4782 (class 2606 OID 49393)
-- Name: medicos medicos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.medicos
    ADD CONSTRAINT medicos_pkey PRIMARY KEY (id_medico);


--
-- TOC entry 4778 (class 2606 OID 49386)
-- Name: pacientes pacientes_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pacientes
    ADD CONSTRAINT pacientes_email_key UNIQUE (email);


--
-- TOC entry 4780 (class 2606 OID 49384)
-- Name: pacientes pacientes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pacientes
    ADD CONSTRAINT pacientes_pkey PRIMARY KEY (id_paciente);


--
-- TOC entry 4776 (class 2606 OID 49370)
-- Name: servicios_medicos servicios_medicos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.servicios_medicos
    ADD CONSTRAINT servicios_medicos_pkey PRIMARY KEY (id_servicio);


--
-- TOC entry 4786 (class 2606 OID 49415)
-- Name: citas fk_cita_medico; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.citas
    ADD CONSTRAINT fk_cita_medico FOREIGN KEY (id_medico) REFERENCES public.medicos(id_medico) ON DELETE RESTRICT;


--
-- TOC entry 4787 (class 2606 OID 49405)
-- Name: citas fk_cita_paciente; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.citas
    ADD CONSTRAINT fk_cita_paciente FOREIGN KEY (id_paciente) REFERENCES public.pacientes(id_paciente) ON DELETE RESTRICT;


--
-- TOC entry 4788 (class 2606 OID 49410)
-- Name: citas fk_cita_servicio; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.citas
    ADD CONSTRAINT fk_cita_servicio FOREIGN KEY (id_servicio) REFERENCES public.servicios_medicos(id_servicio) ON DELETE RESTRICT;


--
-- TOC entry 4785 (class 2606 OID 49371)
-- Name: servicios_medicos fk_especialidad; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.servicios_medicos
    ADD CONSTRAINT fk_especialidad FOREIGN KEY (id_especialidad) REFERENCES public.especialidades(id_especialidad) ON DELETE RESTRICT;


-- Completed on 2026-10-31 11:30:21

--
-- PostgreSQL database dump complete
--

\unrestrict BE0cKMzsjTcOJt30PuZkY3b7jmIGuflSD9IghokqP1R3ycXev8mlqcCAMfwudmi

