--ARCHIVOS--
+ Diagrama dado por el profe (.bpmn)
+ base_de_datos.sql: Tablas de la institución
+ usuarios_grupos.sql: Usuarios y grupos para Flowable
(Hay que tener Docker ya instalado)

Paso a paso:
1) Ir a la carpeta donde tenemos el archivo .yml de Docker (ej: ~/flowable-persistente)
2) Iniciar los contenedores con el siguiente comando:
   docker compose up -d
3) Verificar que todos estén Up:
   docker ps

Cargar los scripts SQL:
A) docker exec -i flowable-postgres psql -U postgres -d flowable < scripts/usuarios_grupos.sql
   (para cargar los usuarios y los grupos)
B) docker exec -i flowable-postgres psql -U postgres -d flowable < scripts/base_de_datos.sql
   (para cargar las tablas creadas)

Verificación:
Abrimos el navegador y vamos a: http://localhost:8080/flowable-ui
Entramos a "IDM App" con el usuario administrador (admin / test) y en las pestañas "Users" y "Groups" van a figurar los usuarios del script.

--ACLARACIONES--
* El diagrama que pasó el profe presenta observaciones en la configuración ejecutable, pero para importarlo solo entramos a "Modeler App", seleccionamos "Import Process", subimos el archivo .bpmn del proyecto y guardamos.
* Los nombres de los usuarios están definidos en el script y todos tienen de contraseña: 123
