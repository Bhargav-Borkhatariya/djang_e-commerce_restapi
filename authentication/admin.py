from django.contrib import admin
from authentication.models import (
    ForgetPasswordOtp,
    ActivationOTP,
    )


@admin.register(ForgetPasswordOtp)
class ForgetPasswordOtpAdmin(admin.ModelAdmin):
    list_display = ("user", "otp", "created_at")
    list_filter = ("created_at",)


@admin.register(ActivationOTP)
class ActivationOTPAdmin(admin.ModelAdmin):
    list_display = ("user", "otp", "created_at")
    list_filter = ("created_at",)
