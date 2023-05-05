from rest_framework import serializers

from app.models import Department, Diagnosis, Doctor, NonReimbursable, Patient, Schedule


class PatientCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=30)

    class Meta:
        model = Patient
        fields = ["name"]


class DepartmentCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=30)

    class Meta:
        model = Department
        fields = ["name"]


class NonReimbursableCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=30)

    class Meta:
        model = NonReimbursable
        fields = ["name"]


class DepartmentIndexSerializer(serializers.Serializer):
    id = serializers.IntegerField()

    class Meta:
        model = Department
        fields = ["id"]


class NonReimbursableIndexSerializer(serializers.Serializer):
    id = serializers.IntegerField()

    class Meta:
        model = NonReimbursable
        fields = ["id"]


class DiagnosisIndexSerializer(serializers.Serializer):
    diag_id = serializers.IntegerField()

    class Meta:
        model = Diagnosis
        fields = ["id"]


class ScheduleCreateSerializer(serializers.Serializer):
    day = serializers.IntegerField()
    open_hour = serializers.IntegerField()
    close_hour = serializers.IntegerField()
    open_minute = serializers.IntegerField(default=0)
    close_minute = serializers.IntegerField(default=0)


class DoctorCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=30)
    hospital = serializers.CharField(max_length=30)
    departments = DepartmentIndexSerializer(many=True)
    non_reimbursable = NonReimbursableIndexSerializer(many=True)
    schedules = ScheduleCreateSerializer(many=True)

    class Meta:
        model = Doctor
        fields = ["name", "hospital", "departments", "non_reimbursable", "schedules"]


class DoctorSearchSerializer(serializers.Serializer):
    string = serializers.CharField(help_text="통합 문자열 검색어", required=False)
    date = serializers.DateTimeField(
        format="%Y-%m-%d %H:%M:%S", help_text="영업일 기준 검색어", required=False
    )


class DoctorListSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text="의사id")
    name = serializers.CharField(help_text="의사명")

    class Meta:
        model = Doctor
        fields = ["id", "name"]


class DiagnosisSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    desired = serializers.DateTimeField()
    expired_at = serializers.DateTimeField()
    patient_name = serializers.CharField(source="patient.name", help_text="환자명")

    class Meta:
        model = Diagnosis
        fields = ["id", "patient_name", "desired", "expired_at"]


class DiagnosisResSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    desired = serializers.DateTimeField()
    expired_at = serializers.DateTimeField()
    patient_name = serializers.CharField(
        source="patient.name", help_text="환자명", read_only=True
    )
    doctor_name = serializers.CharField(source="doctor.name", read_only=True)

    class Meta:
        model = Diagnosis
        fields = ["id", "patient_name", "doctor_name", "desired", "expired_at"]


class DiagnosisCreateSerializer(serializers.Serializer):
    patient_id = serializers.IntegerField(help_text="환자 id")
    doctor_id = serializers.IntegerField(help_text="의사 id")
    desired = serializers.DateTimeField(
        input_formats="%Y-%m-%d %H:%M:%S", help_text="진료 희망 날짜"
    )


class DiagnosisAcceptSerializer(serializers.Serializer):
    class Meta:
        model = Diagnosis
        fields = ["is_accepted"]


class ScheduleSerializer(serializers.Serializer):
    # doctor_name = serializers.CharField(source="doctor.name")

    class Meta:
        model = Schedule
        fields = ["id", "weekday", "opening", "closing"]
