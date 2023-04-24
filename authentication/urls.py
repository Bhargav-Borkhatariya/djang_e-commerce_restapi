from django.urls import path
from authentication.views import (
    RegistrationAPIView,
    VerifyActivationOtpView,
    SendOtpAcivationAPIView,
    LoginAPIView,
    SendForgetPasswordOtpAPIView,
    ResetPasswordAPIView,
)

urlpatterns = [
    # Registration API endpoint
    path("register/",
         RegistrationAPIView.as_view(),
         name="register"),

    # User Verify OTP for Activation API endpoint
    path("verify-activationotp/",
         VerifyActivationOtpView.as_view(),
         name="verify-activationotp"),

    # Activate-Account API endpoint
    path("sendotp-activation/",
         SendOtpAcivationAPIView.as_view(),
         name="sendotp-activation"),

    # Email Login API endpoint
    path("login/",
         LoginAPIView.as_view(),
         name="login"),

    # Forget Password API endpoint
    path("sendotp-forget/",
         SendForgetPasswordOtpAPIView.as_view(),
         name="sendotp-forget"),

    # Forget Password API endpoint
    path("forget-password/",
         ResetPasswordAPIView.as_view(),
         name="forget-password"),

]
