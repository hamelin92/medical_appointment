from datetime import timedelta

from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import *
from .serializers import (
    DepartmentCreateSerializer,
    DiagnosisCreateSerializer,
    DiagnosisIndexSerializer,
    DiagnosisResSerializer,
    DiagnosisSerializer,
    DoctorCreateSerializer,
    DoctorListSerializer,
    DoctorSearchSerializer,
    NonReimbursableCreateSerializer,
    PatientCreateSerializer,
    ScheduleCreateSerializer,
    ScheduleSerializer,
)


@swagger_auto_schema(
    method="get",
    query_serializer=DoctorSearchSerializer,
)
@swagger_auto_schema(method="post", request_body=DoctorCreateSerializer)
@api_view(["GET", "POST"])
def search_or_create_doctor(request):

    def search_doctor(request):
        queries = request.query_params
        serializer = DoctorSearchSerializer(data=queries)
        if serializer.is_valid(raise_exception=True):
            q = Q()
            if queries.get("string"):
                query = queries["string"]
                q |= Q(name__icontains=query)
                q |= Q(hospital__icontains=query)
                q |= Q(departments__name__icontains=query)
                q |= Q(non_reimbursable__name__icontains=query)
            if queries.get("date"):
                date = timezone.datetime.strptime(queries["date"], "%Y-%m-%d %H:%M:%S")
                time = date.time()
                q &= Q(business_hours__weekday=date.weekday())
                q &= Q(business_hours__opening__lte=time)
                q &= Q(business_hours__closing__gt=time)
            doctors = Doctor.objects.filter(q).distinct()
            res = DoctorListSerializer(doctors, many=True)
            return Response(res.data, status=200)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def create_doctor(request):
        serializer = DoctorCreateSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            data = request.data
            doctor = Doctor.objects.create(name=data["name"], hospital=data["hospital"])
            if data["departments"]:
                for dep_id in data["departments"]:
                    doctor.departments.add(dep_id["id"])
            if data["non_reimbursable"]:
                for nrm_id in data["non_reimbursable"]:
                    doctor.non_reimbursable.add(nrm_id["id"])
            if data["schedules"]:
                Schedule.objects.bulk_create(
                    [
                        Schedule(
                            weekday=schedule["day"],
                            opening=f'{schedule["open_hour"]}:{schedule["open_minute"]}:00',
                            closing=f'{schedule["close_hour"]}:{schedule["close_minute"]}:00',
                            doctor=doctor,
                        )
                        for schedule in data["schedules"]
                    ]
                )
            return Response(data=serializer.data, status=201)
    if request.method == "GET":
        return search_doctor(request)
    if request.method == "POST":
        return create_doctor(request)


@swagger_auto_schema(method="post", request_body=ScheduleCreateSerializer(many=True))
@api_view(["POST"])
def add_schedule(request, dr_id):
    doctor = get_object_or_404(Doctor, pk=dr_id)
    serializer = ScheduleCreateSerializer(data=request.data, many=True)
    if serializer.is_valid(raise_exception=True):
        Schedule.objects.bulk_create(
            [
                Schedule(
                    weekday=schedule["day"],
                    opening=f'{schedule["open_hour"]}:{schedule["open_minute"]}:00',
                    closing=f'{schedule["close_hour"]}:{schedule["close_minute"]}:00',
                    doctor=doctor,
                )
                for schedule in request.data
            ]
        )
    return Response(data=serializer.data, status=201)


@swagger_auto_schema(method="post", request_body=DepartmentCreateSerializer)
@api_view(["POST"])
def add_department(request):
    serializer = DepartmentCreateSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        Department.objects.create(name=request.data["name"])
        return Response(data=serializer.data, status=201)


@swagger_auto_schema(method="post", request_body=NonReimbursableCreateSerializer)
@api_view(["POST"])
def add_non_reimbursable(request):
    serializer = NonReimbursableCreateSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        NonReimbursable.objects.create(name=request.data["name"])
        return Response(data=serializer.data, status=201)


@swagger_auto_schema(method="post", request_body=PatientCreateSerializer)
@api_view(["POST"])
def create_patient(request):
    serializer = PatientCreateSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        Patient.objects.create(name=request.data["name"])
        return Response(data=serializer.data, status=201)


@api_view(["GET"])
def search_diagnosis(request, dr_id: int):
    diagnosis = Diagnosis.objects.filter(doctor=dr_id, is_accepted=False)
    serializer = DiagnosisSerializer(diagnosis, many=True)
    return Response(data=serializer.data, status=200)


@swagger_auto_schema(method="post", request_body=DiagnosisCreateSerializer)
@swagger_auto_schema(method="put", request_body=DiagnosisIndexSerializer)
@api_view(["POST", "PUT"])
def create_or_update_appointment(request):
    res = {}
    data = request.data
    message = "영업 중"
    if request.method == "POST":
        # 진료 요청 ( 생성 )
        patient_id = data.get("patient_id")
        doctor_id = data.get("doctor_id")
        desired = timezone.datetime.strptime(data.get("desired"), "%Y-%m-%d %H:%M:%S")
        doctor = get_object_or_404(Doctor, id=doctor_id)
        able = doctor.business_hours.filter(
            weekday=desired.weekday(),
            opening__lte=desired.time(),
            closing__gt=desired.time(),
        ).first()
        expired_at = desired + timedelta(minutes=20)
        if not able:
            message = "의사의 영업시간이 아님."
            for delta in range(7):
                if delta == 0:
                    next_schedule = (
                        doctor.business_hours.filter(
                            weekday=desired.weekday(), opening__gt=desired.time()
                        )
                        .order_by("opening")
                        .first()
                    )
                else:
                    next_schedule = (
                        doctor.business_hours.filter(
                            weekday=(desired.weekday() + delta) % 7
                        )
                        .order_by("opening")
                        .first()
                    )
                if next_schedule is not None:
                    expired_at = timezone.datetime.combine(
                        (desired + timedelta(days=delta)).date(), next_schedule.opening
                    ) + timedelta(minutes=15)
                    break
        diagnosis = Diagnosis.objects.create(
            patient_id=patient_id,
            doctor_id=doctor_id,
            desired=desired,
            expired_at=expired_at,
        )
        serializer = DiagnosisResSerializer(diagnosis)
        return Response({"message": message, "data": serializer.data}, status=200)
    elif request.method == "PUT":
        # 진료 요청 수락
        diag_id = request.data.get("diag_id")
        diagnosis = get_object_or_404(Diagnosis, id=diag_id)
        diagnosis.is_accepted = True
        diagnosis.save()
        serializer = DiagnosisSerializer(diagnosis)
        return Response(data=serializer.data, status=200)
