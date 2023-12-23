from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated

from .serializers import (
    UserRegistrationSerializer,
    ActivationSerializer,
    LoginSerializer,
    PasswordChangeSerializer,
    ForgottenPasswordSerializer,
    SetNewForgottenPasswordSerializer
)


class RegistrationView(APIView):
    def post(self, request: Request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                data='Thank you for registration! An email with an activation code has been sent to your email.',
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AccountActivationView(APIView):
    def post(self, request: Request):
        serializer = ActivationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.activate_account()
            return Response(
                'Your account has been activated!',
                status=status.HTTP_200_OK
            )


class LoginView(ObtainAuthToken):
    serializer_class = LoginSerializer


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request: Request):
        user = request.user
        Token.objects.filter(user=user).delete()
        return Response(
            'You have logged out of your account.',
            status=status.HTTP_200_OK
        )


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.set_new_password()
            return Response(
                'Your password has been changed succesfully.',
                status=status.HTTP_200_OK
            )


class ChangeForgottenPasswordView(APIView):
    def post(self, request: Request):
        serializer = ForgottenPasswordSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.send_code()
            return Response(
                'A password recovery code has been sent to you.',
                status=status.HTTP_200_OK
            )


class ChangeForgottenPasswordCompleteView(APIView):
    def post(self, request: Request):
        serializer = SetNewForgottenPasswordSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.set_new_password()
            return Response(
                'Your password has been recovered successfully.',
                status=status.HTTP_200_OK
            )