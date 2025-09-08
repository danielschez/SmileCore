from django.contrib import admin
from django.urls import path
from django.template.response import TemplateResponse
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Weekday, WorkingHour, Service, Doctor, Patient, Appointment, ClinicalHistory
import json
from datetime import datetime, timedelta

@admin.register(Weekday)
class WeekdayAdmin(admin.ModelAdmin):
    list_display = ('id', 'day', 'status')
    list_editable = ('status',)
    ordering = ['id']


@admin.register(WorkingHour)
class WorkingHourAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'day', 'start_time', 'end_time')
    list_filter = ('doctor', 'day')
    ordering = ['doctor', 'day', 'start_time']


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'duration', 'price')
    search_fields = ('name',)
    ordering = ['name']


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'specialty', 'license_number', 'phone')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')

    def full_name(self, obj):
        return obj.user.get_full_name()
    full_name.short_description = 'Name'


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'date_of_birth', 'gender', 'phone')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')

    def full_name(self, obj):
        return obj.user.get_full_name()
    full_name.short_description = 'Name'


@admin.register(ClinicalHistory)
class ClinicalHistoryAdmin(admin.ModelAdmin):
    list_display = ('appointment', 'reason', 'follow_up_needed', 'created_at')
    list_filter = ('follow_up_needed',)
    search_fields = ('appointment__patient__user__first_name', 'diagnosis')
    ordering = ['-created_at']


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('date', 'time', 'patient', 'doctor', 'status')
    list_filter = ('status', 'doctor', 'date')
    search_fields = ('patient__user__first_name', 'patient__user__last_name', 'doctor__user__first_name')
    
    # Sobrescribir el template de changelist
    change_list_template = 'admin/scheduler/appointment/change_list.html'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('check-availability/', self.check_availability_view, name='scheduler_appointment_check_availability'),
            path('create-appointment/', self.create_appointment_view, name='scheduler_appointment_create'),
            path('get-events/', self.get_events_view, name='scheduler_appointment_get_events'),  # Nueva URL
        ]
        return custom_urls + urls

    def get_events_view(self, request):
        """Vista para obtener eventos del calendario"""
        try:
            # Obtener todas las citas
            appointments = Appointment.objects.select_related(
                'patient__user', 'doctor__user', 'service'
            ).all()
            
            events = []
            print(f"Cargando {appointments.count()} eventos para el calendario")
            
            for appt in appointments:
                try:
                    # Formatear la fecha y hora a una única cadena ISO 8601
                    start_iso = datetime.combine(appt.date, appt.time).isoformat()
                    
                    # Calcular duración y hora de fin
                    duration = getattr(appt.service, 'duration', timedelta(minutes=30)) if hasattr(appt, 'service') and appt.service else timedelta(minutes=30)
                    
                    if not isinstance(duration, timedelta):
                        # Asumir que es un entero y convertirlo
                        duration = timedelta(minutes=duration)
                    
                    end_dt = datetime.combine(appt.date, appt.time) + duration
                    end_iso = end_dt.isoformat()
                    
                    # Nombres completos
                    patient_name = appt.patient.user.get_full_name() or appt.patient.user.username
                    doctor_name = appt.doctor.user.get_full_name() or appt.doctor.user.username
                    
                    # Crear el evento con los campos 'start' y 'end' corregidos
                    event = {
                        'id': str(appt.id),
                        'title': f"{patient_name} - {doctor_name}",  # Título más completo para el calendario
                        'start': start_iso,
                        'end': end_iso,
                        'backgroundColor': self.get_status_color(appt.status),
                        'borderColor': self.get_status_color(appt.status),
                        'textColor': '#ffffff',
                        'url': f"/admin/scheduler/appointment/{appt.id}/change/",
                        'extendedProps': {
                            'doctor': doctor_name,
                            'patient': patient_name,
                            'status': appt.status,
                            'service': appt.service.name if appt.service else 'Consulta General',
                            'time': appt.time.strftime('%H:%M')
                        }
                    }
                    
                    events.append(event)
                    
                except Exception as e:
                    print(f"Error procesando cita {appt.id}: {e}")
                    continue
            
            print(f"Eventos procesados: {len(events)}")
            
            return JsonResponse({
                'success': True,
                'events': events,
                'count': len(events)
            })
            
        except Exception as e:
            print(f"Error en get_events_view: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e),
                'events': []
            }, status=500)

    def changelist_view(self, request, extra_context=None):
        # Obtener las citas para el template (fallback)
        appointments = Appointment.objects.select_related('patient__user', 'doctor__user', 'service')
        events = []

        print(f"Total de citas encontradas para template: {appointments.count()}")

        for appt in appointments:
            try:
                start_dt = datetime.combine(appt.date, appt.time)
                
                # Obtener la duración del servicio o usar 30 minutos por defecto
                duration = getattr(appt.service, 'duration', timedelta(minutes=30)) if hasattr(appt, 'service') and appt.service else timedelta(minutes=30)
                
                # Asegurar que `duration` es un objeto timedelta
                if not isinstance(duration, timedelta):
                    duration = timedelta(minutes=duration)
                
                end_dt = start_dt + duration
                
                patient_name = appt.patient.user.get_full_name() or appt.patient.user.username
                doctor_name = appt.doctor.user.get_full_name() or appt.doctor.user.username

                event = {
                    'id': appt.id,
                    'title': f"{patient_name}",
                    'start': start_dt.isoformat(),
                    'end': end_dt.isoformat(),
                    'url': f"/admin/scheduler/appointment/{appt.id}/change/",
                    'backgroundColor': '#417690',  # Azul, color de tus botones
                    'borderColor': '#417690',
                    'textColor': '#ffffff' if appt.status in ['scheduled', 'completed', 'cancelled'] else '#000000',
                    'doctor': doctor_name,
                    'patient': patient_name,
                    'status': appt.status,
                    'time': appt.time.strftime('%H:%M')
                }
                events.append(event)
            except Exception as e:
                print(f"Error procesando cita {appt.id}: {e}")

        # Obtener doctores, pacientes y servicios para el formulario
        doctors = Doctor.objects.select_related('user').all().order_by('user__first_name')
        patients = Patient.objects.select_related('user').all().order_by('user__first_name')
        services = Service.objects.all().order_by('name')
        
        # Convertir doctores a lista serializable para JSON
        doctors_data = []
        for doctor in doctors:
            doctors_data.append({
                'id': doctor.id,
                'name': doctor.user.get_full_name() or doctor.user.username,
                'specialty': getattr(doctor, 'specialty', '') or ''
            })
        
        extra_context = extra_context or {}
        extra_context.update({
            'events': events,
            'doctors': doctors,  # Para usar en el template HTML
            'patients': patients,  # Para usar en el template HTML
            'services': services,  # Para usar en el template HTML
            'doctors_data': doctors_data,  # Para serializar a JSON
        })
        
        return super().changelist_view(request, extra_context=extra_context)

    @method_decorator(csrf_exempt, name='dispatch')
    def check_availability_view(self, request):
        """Verificar disponibilidad de una fecha y hora específica"""
        if request.method != 'POST':
            return JsonResponse({'error': 'Método no permitido'}, status=405)

        try:
            data = json.loads(request.body)
            date_str = data.get('date')
            time_str = data.get('time')
            doctor_id = data.get('doctor_id')
            
            print(f"Verificando disponibilidad: {data}")  # Debug
            
            # Validar que todos los campos estén presentes
            if not all([date_str, time_str, doctor_id]):
                return JsonResponse({
                    'available': False,
                    'message': 'Faltan datos requeridos (fecha, hora, doctor)'
                }, status=400)
            
            # Convertir strings a objetos datetime
            try:
                appointment_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                appointment_time = datetime.strptime(time_str, '%H:%M').time()
            except ValueError as e:
                return JsonResponse({
                    'available': False,
                    'message': f'Formato de fecha u hora inválido: {str(e)}'
                }, status=400)
                
            appointment_datetime = datetime.combine(appointment_date, appointment_time)
            
            # Validar que no sea una fecha/hora pasada
            if appointment_datetime <= datetime.now():
                return JsonResponse({
                    'available': False,
                    'message': 'No se pueden crear citas en fechas y horas pasadas'
                })
            
            # Verificar si el doctor existe
            try:
                doctor = Doctor.objects.get(id=doctor_id)
            except Doctor.DoesNotExist:
                return JsonResponse({
                    'available': False,
                    'message': 'Doctor no encontrado'
                }, status=400)
            
            # Verificar si ya existe una cita en esa fecha/hora para ese doctor
            existing_appointment = Appointment.objects.filter(
                date=appointment_date,
                time=appointment_time,
                doctor_id=doctor_id,
                status__in=['scheduled', 'pending']  # Solo citas activas
            ).exists()
            
            if existing_appointment:
                return JsonResponse({
                    'available': False,
                    'message': 'Ya hay una cita programada en este horario para este doctor'
                })
            
            # Verificar horario de trabajo del doctor
            weekday = appointment_date.weekday() + 1  # Django usa 1-7, Python 0-6
            
            # Verificar si el día está habilitado
            day_enabled = Weekday.objects.filter(id=weekday, status=True).exists()
            if not day_enabled:
                return JsonResponse({
                    'available': False,
                    'message': 'El día seleccionado no está habilitado para citas'
                })
            
            # Verificar horario de trabajo específico del doctor
            working_hour = WorkingHour.objects.filter(
                doctor_id=doctor_id,
                day_id=weekday,
                start_time__lte=appointment_time,
                end_time__gte=appointment_time
            ).exists()
            
            if not working_hour:
                return JsonResponse({
                    'available': False,
                    'message': f'El Dr. {doctor.user.get_full_name()} no tiene horario de trabajo en esta fecha y hora'
                })
            
            return JsonResponse({
                'available': True,
                'message': f'Horario disponible para Dr. {doctor.user.get_full_name()}'
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'available': False,
                'message': 'Datos JSON inválidos'
            }, status=400)
        except Exception as e:
            print(f"Error en check_availability: {e}")
            return JsonResponse({
                'available': False,
                'message': 'Error interno del servidor'
            }, status=500)

    @method_decorator(csrf_exempt, name='dispatch')  
    def create_appointment_view(self, request):
        """Crear una nueva cita"""
        if request.method != 'POST':
            return JsonResponse({'error': 'Método no permitido'}, status=405)

        try:
            data = json.loads(request.body)
            print(f"Datos recibidos para crear cita: {data}")  # Debug
            
            # Validar datos requeridos
            required_fields = ['date', 'time', 'doctor_id', 'patient_id']
            for field in required_fields:
                if not data.get(field):
                    return JsonResponse({
                        'success': False,
                        'error': f'Campo requerido faltante: {field}'
                    }, status=400)
            
            # Convertir datos
            try:
                appointment_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
                appointment_time = datetime.strptime(data['time'], '%H:%M').time()
            except ValueError as e:
                return JsonResponse({
                    'success': False,
                    'error': f'Formato de fecha u hora inválido: {str(e)}'
                }, status=400)
                
            appointment_datetime = datetime.combine(appointment_date, appointment_time)
            
            # Validar que no sea una fecha/hora pasada
            if appointment_datetime <= datetime.now():
                return JsonResponse({
                    'success': False,
                    'error': 'No se pueden crear citas en fechas y horas pasadas'
                }, status=400)
            
            # Verificar que el doctor existe
            try:
                doctor = Doctor.objects.get(id=data['doctor_id'])
            except Doctor.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Doctor no encontrado'
                }, status=400)
            
            # Verificar que el paciente existe
            try:
                patient = Patient.objects.get(id=data['patient_id'])
            except Patient.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Paciente no encontrado'
                }, status=400)
            
            # Obtener o asignar un servicio
            service = None
            if data.get('service_id'):
                try:
                    service = Service.objects.get(id=data['service_id'])
                except Service.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'error': 'Servicio no encontrado'
                    }, status=400)
            else:
                # Asignar un servicio por defecto o crear uno genérico
                service = Service.objects.first()
                if not service:
                    # Si no hay servicios, crear uno genérico
                    service = Service.objects.create(
                        name='Consulta General',
                        duration=30,
                        price=0.00
                    )
            
            # Verificar disponibilidad nuevamente antes de crear
            existing = Appointment.objects.filter(
                date=appointment_date,
                time=appointment_time,
                doctor_id=data['doctor_id'],
                status__in=['scheduled', 'pending']
            ).exists()
            
            if existing:
                return JsonResponse({
                    'success': False,
                    'error': 'Ya existe una cita en este horario'
                }, status=400)
            
            # Verificar horario de trabajo
            weekday = appointment_date.weekday() + 1
            working_hour = WorkingHour.objects.filter(
                doctor_id=data['doctor_id'],
                day_id=weekday,
                start_time__lte=appointment_time,
                end_time__gte=appointment_time
            ).exists()
            
            if not working_hour:
                return JsonResponse({
                    'success': False,
                    'error': 'El doctor no tiene horario de trabajo en esta fecha y hora'
                }, status=400)
            
            # Crear la cita CON el servicio
            appointment = Appointment.objects.create(
                date=appointment_date,
                time=appointment_time,
                doctor=doctor,
                patient=patient,
                service=service,  # Importante: incluir el servicio
                status='scheduled'
            )
            
            print(f"Cita creada exitosamente: ID {appointment.id}")  # Debug
            
            return JsonResponse({
                'success': True,
                'message': 'Cita creada exitosamente',
                'appointment_id': appointment.id,
                'appointment_details': {
                    'date': appointment.date.strftime('%Y-%m-%d'),
                    'time': appointment.time.strftime('%H:%M'),
                    'doctor': doctor.user.get_full_name() or doctor.user.username,
                    'patient': patient.user.get_full_name() or patient.user.username,
                    'service': service.name,
                    'status': appointment.status
                }
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Datos JSON inválidos'
            }, status=400)
        except Exception as e:
            print(f"Error en create_appointment: {e}")
            return JsonResponse({
                'success': False,
                'error': f'Error interno del servidor: {str(e)}'
            }, status=500)

    def get_status_color(self, status):
        """Obtener color según el estado de la cita"""
        status_colors = {
            'scheduled': '#007bff',    # Azul para programadas
            'completed': '#28a745',    # Verde para completadas
            'cancelled': '#dc3545',    # Rojo para canceladas
            'pending': '#ffc107',      # Amarillo para pendientes
            'in_progress': '#17a2b8',  # Cian para en progreso
            'no_show': '#6c757d',      # Gris para no presentados
        }
        return status_colors.get(status, '#6c757d')

    def has_add_permission(self, request):
        """Permitir agregar citas"""
        return True

    def has_change_permission(self, request, obj=None):
        """Permitir editar citas"""
        return True

    def has_delete_permission(self, request, obj=None):
        """Permitir eliminar citas"""
        return True