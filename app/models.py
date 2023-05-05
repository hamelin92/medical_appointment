from django.db import models


class Patient(models.Model):
    name = models.CharField(max_length=30, help_text="환자명")


class Department(models.Model):
    name = models.CharField(max_length=30, help_text="진료과명")


class NonReimbursable(models.Model):
    name = models.CharField(max_length=30, help_text="비급여진료과목명")


class Doctor(models.Model):
    name = models.CharField(max_length=30, help_text="의사명")
    hospital = models.CharField(max_length=30, null=True, help_text="병원명")
    departments = models.ManyToManyField(
        Department, related_name="doctors", help_text="진료과"
    )
    non_reimbursable = models.ManyToManyField(
        NonReimbursable, related_name="doctors", help_text="비급여진료과목"
    )


class Schedule(models.Model):
    weekday = models.IntegerField(default=0)
    opening = models.TimeField(help_text="영업시작시간")
    closing = models.TimeField(help_text="영업종료시간")
    doctor = models.ForeignKey(
        Doctor, on_delete=models.CASCADE, related_name="business_hours"
    )


class Diagnosis(models.Model):
    doctor = models.ForeignKey(
        Doctor, on_delete=models.CASCADE, related_name="reservation"
    )
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="reservation"
    )
    desired = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField()
    is_accepted = models.BooleanField(default=False)
