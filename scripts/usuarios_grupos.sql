
-- CREACIÓN DE GRUPO
INSERT INTO ACT_ID_GROUP (ID_, REV_, NAME_, TYPE_) 
VALUES ('administracion', 1, 'Administración', 'security-role')
ON CONFLICT (ID_) DO NOTHING;

INSERT INTO ACT_ID_GROUP (ID_, REV_, NAME_, TYPE_) 
VALUES ('docentes', 1, 'Docentes', 'security-role')
ON CONFLICT (ID_) DO NOTHING;

-- CREACIÓN DE USUARIOS
-- Jefe Administrativo
INSERT INTO ACT_ID_USER (ID_, REV_, FIRST_, LAST_, EMAIL_, PWD_) 
VALUES ('jefe_admin', 1, 'Carlos', 'JefeAdmin', 'jefe.admin@institucion.edu.ar', '123')
ON CONFLICT (ID_) DO NOTHING;

-- Administrativo 2
INSERT INTO ACT_ID_USER (ID_, REV_, FIRST_, LAST_, EMAIL_, PWD_) 
VALUES ('admin_2', 1, 'Laura', 'Administrativa', 'laura.admin@institucion.edu.ar', '123')
ON CONFLICT (ID_) DO NOTHING;

-- Jefe Docente
INSERT INTO ACT_ID_USER (ID_, REV_, FIRST_, LAST_, EMAIL_, PWD_) 
VALUES ('jefe_docente', 1, 'Roberto', 'JefeDocente', 'jefe.docente@institucion.edu.ar', '123')
ON CONFLICT (ID_) DO NOTHING;

-- Docente 2
INSERT INTO ACT_ID_USER (ID_, REV_, FIRST_, LAST_, EMAIL_, PWD_) 
VALUES ('docente_2', 1, 'María', 'Docente', 'maria.docente@institucion.edu.ar', '123')
ON CONFLICT (ID_) DO NOTHING;

-- Docente 3
INSERT INTO ACT_ID_USER (ID_, REV_, FIRST_, LAST_, EMAIL_, PWD_) 
VALUES ('docente_3', 1, 'Juan', 'Docente', 'juan.docente@institucion.edu.ar', '123')
ON CONFLICT (ID_) DO NOTHING;

-- ASIGNACIÓN DE USUARIOS A GRUPOS (MEMBERSHIP)
-- Grupo Administración
INSERT INTO ACT_ID_MEMBERSHIP (USER_ID_, GROUP_ID_) VALUES ('jefe_admin', 'administracion') ON CONFLICT DO NOTHING;
INSERT INTO ACT_ID_MEMBERSHIP (USER_ID_, GROUP_ID_) VALUES ('admin_2', 'administracion') ON CONFLICT DO NOTHING;

-- Grupo Docentes
INSERT INTO ACT_ID_MEMBERSHIP (USER_ID_, GROUP_ID_) VALUES ('jefe_docente', 'docentes') ON CONFLICT DO NOTHING;
INSERT INTO ACT_ID_MEMBERSHIP (USER_ID_, GROUP_ID_) VALUES ('docente_2', 'docentes') ON CONFLICT DO NOTHING;
INSERT INTO ACT_ID_MEMBERSHIP (USER_ID_, GROUP_ID_) VALUES ('docente_3', 'docentes') ON CONFLICT DO NOTHING;
