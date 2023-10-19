from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import UserAccount, CompletedTasks, UserTasksSent
from rest_framework.exceptions import ValidationError
from django.contrib.auth import authenticate, password_validation

def check_mobile_number(value):
    if len(value) == 10 and value.isdigit():
        return True
    raise ValidationError("Please enter a valid mobile number.")


class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        required=True,
        validators=[
            UniqueValidator(
                queryset=UserAccount.objects.all(),
                message=("Username already exists!"),
            )
        ],
    )
    email = serializers.EmailField(
        required=True,
        validators=[
            UniqueValidator(
                queryset=UserAccount.objects.all(),
                message=("Email is already registered. Please login!"),
            )
        ],
    )
    password = serializers.CharField(write_only=True, required=True, validators=[password_validation.validate_password])
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    college = serializers.CharField(
        required=True,
    )
    year = serializers.IntegerField(required=True)
    phone_no = serializers.CharField(required=True, validators=[check_mobile_number])
    whatsapp_no = serializers.CharField(required=True, validators=[check_mobile_number])
    postal_address = serializers.CharField(max_length=255, required=True)
    pin_code = serializers.IntegerField()
    why_choose = serializers.CharField(max_length=255)
    were_you_ca = serializers.BooleanField(default=False)

    class Meta:
        model = UserAccount
        fields = "__all__"

def check(data):
    return authenticate(email=data["email"], password=data["password"])



class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField()

    class Meta:
        model = UserAccount
        fields = ("username", "password")


class CompletedTasksSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompletedTasks
        fields = "__all__"


class UserTaskSentSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTasksSent
        fields = ["task"]