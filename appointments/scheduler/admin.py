from django.contrib import admin
from .models import Weekday, WorkingHour, Service, Doctor, Patient, Appointment, ClinicalHistory

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

    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Name'


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'date_of_birth', 'gender', 'phone')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')

    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Name'


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('date', 'time', 'get_doctor_name', 'get_patient_name', 'service', 'status')
    list_filter = ('doctor', 'status', 'date')
    search_fields = (
        'patient__user__first_name',
        'patient__user__last_name',
        'doctor__user__last_name'
    )
    ordering = ['-date', '-time']

    def get_doctor_name(self, obj):
        return obj.doctor.user.get_full_name()
    get_doctor_name.short_description = 'Doctor'

    def get_patient_name(self, obj):
        return obj.patient.user.get_full_name()
    get_patient_name.short_description = 'Patient'


@admin.register(ClinicalHistory)
class ClinicalHistoryAdmin(admin.ModelAdmin):
    list_display = ('appointment', 'reason', 'follow_up_needed', 'created_at')
    list_filter = ('follow_up_needed',)
    search_fields = ('appointment__patient__user__first_name', 'diagnosis')
    ordering = ['-created_at']