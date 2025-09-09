from django.db import models
from django.contrib.auth.models import User


# ─────────────────────────────
#       Perfiles de Usuario
# ─────────────────────────────

class Doctor(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_doctors')

    full_name = models.CharField(max_length=255)  # Nombre del doctor
    specialty = models.CharField(max_length=100)
    license_number = models.CharField(max_length=50, unique=True)
    phone = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Dr. {self.full_name} - {self.specialty}"
    
    class Meta:
        verbose_name = "Doctor"
        verbose_name_plural = "Doctores"
        ordering = ['full_name']


class Patient(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_patients')

    full_name = models.CharField(max_length=255)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ], blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True, null=True)
    blood_type = models.CharField(max_length=3, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name
    
    class Meta:
        verbose_name = "Patient"
        verbose_name_plural = "Pacientes"
        ordering = ['full_name']


# ─────────────────────────────
#       Calendario Laboral
# ─────────────────────────────

class Weekday(models.Model):
    day = models.CharField(max_length=10)  # Ej: Monday, Tuesday
    status = models.BooleanField(default=True)  # Activo/inactivo

    def __str__(self):
        return self.day

    class Meta:
        verbose_name = "Weekday"
        verbose_name_plural = "Días de la Semana"
        ordering = ['id']


class WorkingHour(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='working_hours')
    day = models.ForeignKey(Weekday, on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.doctor} - {self.day}: {self.start_time} to {self.end_time}"

    class Meta:
        verbose_name = "Working Hour"
        verbose_name_plural = "Horas Laborales"
        ordering = ['doctor', 'day__id', 'start_time']


# ─────────────────────────────
#           Servicios
# ─────────────────────────────

class Service(models.Model):
    name = models.CharField(max_length=100)
    duration = models.DurationField()  # Ej: timedelta(minutes=30)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Service"
        verbose_name_plural = "Servicios"
        ordering = ['name']


# ─────────────────────────────
#           Citas
# ─────────────────────────────

class Appointment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='appointments')

    date = models.DateField()
    time = models.TimeField()
    description = models.TextField(blank=True)

    status = models.CharField(max_length=20, choices=[
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], default='scheduled')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.date} {self.time} - {self.patient} with {self.doctor}"

    class Meta:
        verbose_name = "Appointment"
        verbose_name_plural = "Citas"
        ordering = ['-date', '-time']


# ─────────────────────────────
#      Historial Clínico
# ─────────────────────────────

class ClinicalHistory(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='clinical_history')

    reason = models.CharField(max_length=255, help_text="Motivo de la consulta")
    diagnosis = models.TextField(blank=True, null=True)
    treatment = models.TextField(blank=True, null=True)
    prescription = models.TextField(blank=True, null=True)

    follow_up_needed = models.BooleanField(default=False)
    follow_up_date = models.DateTimeField(blank=True, null=True)

    notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Historial {self.appointment} ({self.appointment.date})"

    class Meta:
        verbose_name = "Clinical History"
        verbose_name_plural = "Historiales Clínicos"
        ordering = ['-appointment__date']

