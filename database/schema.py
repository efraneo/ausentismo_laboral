"""Esquema SQL para Supabase - Ejecutar en SQL Editor de Supabase."""

SCHEMA_SQL = """
-- =========================================================
-- TABLA: usuarios
-- =========================================================
CREATE TABLE IF NOT EXISTS usuarios (
    id BIGSERIAL PRIMARY KEY,
    usuario TEXT UNIQUE NOT NULL,
    nombre TEXT NOT NULL,
    clave_hash TEXT NOT NULL,
    correo TEXT UNIQUE,
    identificacion TEXT,
    cargo TEXT,
    fecha_nacimiento TEXT,
    perfil TEXT DEFAULT 'consulta',
    estado TEXT DEFAULT 'pendiente',  -- pendiente | aprobado | rechazado
    caducidad TEXT DEFAULT 'Indefinido',
    ingresos_sistema INT DEFAULT 0,
    ultimo_ingreso TIMESTAMP,
    codigo_2fa TEXT,
    codigo_2fa_expira TIMESTAMP,
    creado_en TIMESTAMP DEFAULT NOW()
);

-- =========================================================
-- TABLA: trabajadores
-- =========================================================
CREATE TABLE IF NOT EXISTS trabajadores (
    id BIGSERIAL PRIMARY KEY,
    identificacion TEXT UNIQUE,
    apellidos_nombres TEXT,
    cargo TEXT,
    area TEXT,
    nivel_escolaridad TEXT,
    salario TEXT,
    fecha_ingreso TEXT,
    eps TEXT,
    afp TEXT,
    sexo TEXT,
    edad TEXT,
    fecha_nacimiento TEXT,
    direccion TEXT,
    contacto TEXT,
    correo_personal TEXT,
    tel_familiar TEXT,
    hipertension_arterial TEXT DEFAULT 'NO',
    obesidad TEXT DEFAULT 'NO',
    diabetes TEXT DEFAULT 'NO',
    cardiopatia TEXT DEFAULT 'NO',
    hipotiroidismo TEXT DEFAULT 'NO',
    dislipidemia TEXT DEFAULT 'NO',
    enfermedad_renal TEXT DEFAULT 'NO',
    fumador TEXT DEFAULT 'NO',
    enfermedad_pulmonar TEXT DEFAULT 'NO',
    estado TEXT DEFAULT 'Vinculado',
    emo_ingreso TEXT DEFAULT 'Pendiente',
    emo_periodico TEXT DEFAULT 'Pendiente',
    emo_retiro TEXT DEFAULT 'Pendiente',
    creado_en TIMESTAMP DEFAULT NOW(),
    actualizado_en TIMESTAMP DEFAULT NOW()
);

-- =========================================================
-- TABLA: ausentismo
-- =========================================================
CREATE TABLE IF NOT EXISTS ausentismo (
    id BIGSERIAL PRIMARY KEY,
    cedula TEXT,
    apellidos_nombres TEXT,
    cargo TEXT,
    proceso TEXT,
    fecha_ingreso TEXT,
    salario TEXT,
    asunto TEXT,
    tipo_incapacidad TEXT,
    fecha_inicial TEXT,
    fecha_final TEXT,
    genera_incapacidad TEXT,
    dias_perdidos INT,
    mes TEXT,
    costo_incapacidad TEXT,
    codigo_cie10 TEXT,
    diagnostico TEXT,
    dia_semana TEXT,
    creado_en TIMESTAMP DEFAULT NOW()
);

-- =========================================================
-- TABLA: permisos_laborales
-- =========================================================
CREATE TABLE IF NOT EXISTS permisos_laborales (
    id BIGSERIAL PRIMARY KEY,
    cedula TEXT,
    apellidos_nombres TEXT,
    cargo TEXT,
    area TEXT,
    fecha_ingreso TEXT,
    asunto TEXT,
    tipo_permiso TEXT,
    fecha_inicial TEXT,
    fecha_final TEXT,
    hora_inicio TEXT,
    hora_final TEXT,
    descanso_almuerzo TEXT,
    horas TEXT,
    mes TEXT,
    creado_en TIMESTAMP DEFAULT NOW()
);

-- =========================================================
-- Índices
-- =========================================================
CREATE INDEX IF NOT EXISTS idx_ausentismo_cedula ON ausentismo(cedula);
CREATE INDEX IF NOT EXISTS idx_ausentismo_mes ON ausentismo(mes);
CREATE INDEX IF NOT EXISTS idx_permisos_cedula ON permisos_laborales(cedula);
CREATE INDEX IF NOT EXISTS idx_trabajadores_estado ON trabajadores(estado);
"""


def print_schema():
    """Imprime el esquema SQL para ejecutar en Supabase."""
    print(SCHEMA_SQL)


if __name__ == "__main__":
    print_schema()
