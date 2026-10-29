
-- TABLA DE EMPRESAS 
CREATE TABLE IF NOT EXISTS empresa (
    id SERIAL PRIMARY KEY,
    cuit VARCHAR(20) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    email_contacto VARCHAR(100) NOT NULL,
    telefono_contacto VARCHAR(50)
);

-- TABLA DE CURSOS / CAPACITACIONES
CREATE TABLE IF NOT EXISTS curso (
    id SERIAL PRIMARY KEY,
    empresa_id INT NOT NULL REFERENCES empresa(id),
    process_instance_id VARCHAR(64) UNIQUE, 
    nombre VARCHAR(150) NOT NULL,
    descripcion TEXT,
    programa TEXT,
    presupuesto DECIMAL(12, 2),
    fecha_inicio DATE,
    fecha_fin DATE,
    estado VARCHAR(50) DEFAULT 'EN_EVALUACION', 
    informe_resultados TEXT,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

