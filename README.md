
🦷 Sistema de Gestión Dental

Este es un sistema web desarrollado en Django para la gestión de una clínica dental. Permite registrar y administrar pacientes, doctores, horarios de atención, días de la semana disponibles, y visualizar el historial clínico de cada paciente mediante un calendario interactivo utilizando FullCalendar. La interfaz de administración está personalizada con django-jazzmin para una mejor experiencia de usuario.

🚀 Funcionalidades principales

Gestión de pacientes: Registro, edición y consulta de información personal.

Gestión de doctores: Registro de doctores, especialidades y disponibilidad.

Horarios y días disponibles: Administración de horarios de atención y días laborables.

Historial clínico: Registro de tratamientos, citas y observaciones para cada paciente.

Calendario interactivo: Visualización del historial clínico en un calendario con FullCalendar.

Panel de administración personalizado: Estilizado y mejorado con django-jazzmin.

🛠️ Tecnologías utilizadas

Backend: Django (Python)

Frontend: HTML, CSS, JS, FullCalendar

Administrador: Django Admin + django-jazzmin

Base de datos: SQLite (puede configurarse para PostgreSQL u otro motor)


⚙️ Instalación

Clona el repositorio:

git clone https://github.com/danielschez/SmileCore.git
cd tu-repositorio


Crea y activa un entorno virtual:

python -m venv env
source env/bin/activate  # En Windows: env\Scripts\activate


Instala las dependencias:

pip install -r requirements.txt


Aplica las migraciones:

python manage.py migrate


Crea un superusuario:

python manage.py createsuperuser


Ejecuta el servidor:

python manage.py runserver

🔑 Acceso al panel de administración

Visita http://localhost:8000/admin
 e inicia sesión con tu superusuario para acceder al panel personalizado por Jazzmin.

📅 Visualización del historial clínico

Cada paciente tiene un historial clínico asociado que puede visualizarse en un calendario interactivo con FullCalendar, permitiendo una vista clara y rápida de los tratamientos o citas registrados.


✅ Pendientes / Próximas mejoras

 Envío de recordatorios por correo o WhatsApp.

 Reportes descargables en PDF.

 Módulo de facturación.

 Panel para pacientes (self-service).

📄 Licencia

Este proyecto está licenciado bajo MIT / GPL / u otra (dependiendo de lo que elijas).

