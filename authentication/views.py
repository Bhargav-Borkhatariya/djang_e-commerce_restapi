import services.emailsender as emailsender
from authentication.models import ActivationOTP, ForgetPasswordOtp
from authentication.serializers import UserSerializer
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_200_OK,
    HTTP_404_NOT_FOUND,
    HTTP_403_FORBIDDEN,
)
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import AllowAny
from django.utils.crypto import get_random_string
from django.db.models import Q
from django.contrib.auth import login


class RegistrationAPIView(APIView):
    """
    API View to register a new user.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """
        Create a new user account by accepting user details

        Parameters:
        request (Request): The incoming request object

        Returns:
        Response: JSON response containing the user's details and
                  the authentication token if successful.
                  Error response if request is invalid or
                  user with the same email already exists.
        """
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Generate OTP and save to the database
            otp = get_random_string(length=6, allowed_chars="0123456789")
            ActivationOTP.objects.create(user=user, otp=otp)

            # Send email with OTP to the user
            emailsender.send_activation_otp_email(user, otp)

            return Response({
                "status": True,
                "message": "User created successfully",
                "data": None,
            }, status=HTTP_201_CREATED)
        else:
            return Response({
                "status": False,
                "errors": serializer.errors,
                "data": None
            }, status=HTTP_400_BAD_REQUEST)


class VerifyActivationOtpView(APIView):
    """
    API View for verifying user OTP during account activation.
    """

    def post(self, request):
        """
        Verifies the OTP provided by the user for account activation.

        Parameters:
        request (HttpRequest): The HTTP request object containing the OTP.

        Returns:
        response (HttpResponse): A JSON response containing the status of
                OTP verification and a new auth token if verification is successful.
        """
        otp = request.data.get("otp")

        # Check if OTP is present in request data, if not then return an error response
        if not otp:
            return Response({
                "status": False,
                "message": "OTP is required field.",
                "data": None,
            }, status=HTTP_400_BAD_REQUEST)

        # Fetch user by OTP
        try:
            user_activation_otp = ActivationOTP.objects.get(otp=otp)
        except ObjectDoesNotExist:
            # If no user activation entry with the provided OTP is found, return an error response
            return Response({
                "status": False,
                "message": "Invalida OTP Provide",
                "data": None,
            }, status=HTTP_401_UNAUTHORIZED)

        # Get the user associated with the user activation entry
        user = user_activation_otp.user

        # Update the user activation status to True
        user.is_active = True
        user.save()

        # Return success response with the new auth token and user activation status update
        return Response({
            "status": True,
            "message": "OTP is Verified Successfully.",
            "data": None,
        }, status=HTTP_200_OK)


class SendOtpAcivationAPIView(APIView):
    """
    API View for sending OTP during account activation.
    """

    def post(self, request):
        """
        Sends an OTP to the user's email for account activation.

        Parameters:
        request (HttpRequest): The HTTP request object containing the email.

        Returns:
        response (HttpResponse): A JSON response containing the status of
                OTP sending.
        """
        email = request.data.get("email")

        if email:
            # Check if user exists
            users = User.objects.filter(email=email)
            if not users.exists():
                return Response({
                    "status": False,
                    "message": "User does not exist",
                    "data": None
                }, status=HTTP_404_NOT_FOUND)

            user = users.first()

            # Delete any existing activation otp entry
            Activationotp = ActivationOTP.objects.filter(user=user)
            if Activationotp:
                Activationotp.delete()

            # Generate random OTP
            otp = get_random_string(length=6, allowed_chars="0123456789")

            # Send email with OTP to the user
            emailsender.send_activation_otp_email(user, otp)

            # Save OTP to activation entry
            Activationotp = ActivationOTP(user=user, otp=otp)
            Activationotp.save()

            return Response({
                "status": True,
                "message": "OTP sent successfully",
                "data": None,
            }, status=HTTP_200_OK)
        else:
            return Response({
                    "status": False,
                    "message": "Missing email field",
                    "data": None,
                }, status=HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):
    """
    API View for user email or username-based login.
    """

    def post(self, request):
        """
        Authenticate a user and generate a new authentication token by
        accepting user email or username and password.

        Parameters:
        request (Request): The incoming request object

        Returns:
        Response: JSON response containing the authentication token
            if successful.
            Error response if email or password is missing or invalid.
        """
        email_or_username = request.data.get("email_or_username")
        password = request.data.get("password")
        if email_or_username and password:
            users = User.objects.filter(Q(email=email_or_username) | Q(username=email_or_username))
            if not users.exists():
                return Response({
                    "status": False,
                    "message": "User does not exist",
                    "data": None
                }, status=HTTP_404_NOT_FOUND)

            user = users.first()
            if user.check_password(password):
                if user.is_active:
                    # Delete the old auth token
                    token = Token.objects.filter(user=user).first()
                    if token:
                        token.delete()

                    # Generate auth token and return it in response
                    token = Token.objects.create(user=user)
                    login(request, user)

                    return Response({
                        "status": True,
                        "message": "User Login successfully",
                        "data": {"token": token.key},
                    }, status=HTTP_200_OK)
                else:
                    return Response({
                        "status": False,
                        "message": "User account is not active",
                        "data": None,
                    }, status=HTTP_403_FORBIDDEN)
            else:
                return Response({
                    "status": False,
                    "message": "Invalid email or password",
                    "data": None,
                }, status=HTTP_401_UNAUTHORIZED)
        else:
            return Response({
                    "status": False,
                    "message": "Missing username or password field",
                    "data": None,
                }, status=HTTP_400_BAD_REQUEST)


class SendForgetPasswordOtpAPIView(APIView):
    """
    API View for user password reset.
    """

    def post(self, request):
        """
        This code defines an API view for resetting user password.
        When a POST request is received with an email address,
        it generates a random OTP, sends it to the user's email address,
        and saves the OTP in the ForgetPassword model.
        If the email address is not provided or the user is inactive,
        it returns an appropriate error message.
        """
        email = request.data.get("email")

        if email:
            users = User.objects.filter(email=email)
            if not users.exists():
                return Response({
                    "status": False,
                    "message": "User does not exist",
                    "data": None
                }, status=HTTP_404_NOT_FOUND)

            user = users.first()
            if user.is_active:

                # Delete any existing forget password entry
                forget_password = ForgetPasswordOtp.objects.filter(user=user)
                if forget_password:
                    forget_password.delete()

                # Generate random OTP
                otp = get_random_string(length=6, allowed_chars="0123456789")

                # Send email with OTP to the user
                emailsender.send_forget_password_otp_email(user, otp)

                # Save OTP to forget password entry
                forget_password = ForgetPasswordOtp(user=user, otp=otp)
                forget_password.save()

                return Response({
                    "status": True,
                    "message": "OTP sent successfully",
                    "data": None,
                }, status=HTTP_200_OK)
            else:
                return Response({
                    "status": False,
                    "message": "User is not active",
                    "data": None,
                }, status=HTTP_403_FORBIDDEN)
        else:
            return Response({
                    "status": False,
                    "message": "Missing email field",
                    "data": None,
                }, status=HTTP_400_BAD_REQUEST)


class ResetPasswordAPIView(APIView):
    """
    API View for resetting user password using OTP.
    """

    def post(self, request):
        """
        This code defines an API view for resetting user password.
        When a POST request is received with an email address and OTP,
        it checks if the OTP is valid and belongs to the user with the given email.
        If the OTP is valid and the new password is different from the old one, it updates
        the user's password and deletes the OTP entry.
        If the email address or OTP is not provided or invalid, it returns an appropriate error message.
        """
        email = request.data.get("email")
        otp = request.data.get("otp")
        password = request.data.get("password")

        if email and otp and password:
            users = User.objects.filter(email=email)
            if not users.exists():
                return Response({
                    "status": False,
                    "message": "User does not exist",
                    "data": None
                }, status=HTTP_404_NOT_FOUND)

            user = users.first()
            forget_password = ForgetPasswordOtp.objects.filter(user=user, otp=otp)
            if not forget_password.exists():
                return Response({
                    "status": False,
                    "message": "Invalid OTP",
                    "data": None,
                }, status=HTTP_401_UNAUTHORIZED)

            # Check if new password is different from old password
            if check_password(password, user.password):
                return Response({
                    "status": False,
                    "message": "New password must be different from old password",
                    "data": None,
                }, status=HTTP_400_BAD_REQUEST)

            user.password = make_password(password)
            user.save()
            forget_password.delete()

            return Response({
                "status": True,
                "message": "Password reset successfully",
                "data": None,
            }, status=HTTP_200_OK)
        else:
            return Response({
                    "status": False,
                    "message": "Missing email, OTP or password field",
                    "data": None,
                }, status=HTTP_400_BAD_REQUEST)
