from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
    path("doctors", views.search_doctor),
    path("data", views.create_doctor),
    path("schedule/<int:dr_id>", views.add_schedule),
    path("patients", views.create_patient),
    path("departments", views.add_department),
    path("nonreimbursable", views.add_non_reimbursable),
    path("diagnosis", views.create_or_update_appointment),
    path("diagnosis/<int:dr_id>", views.search_diagnosis),
]
