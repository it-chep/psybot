from django.contrib import admin
from django.urls import path, include, re_path
from .views import *

urlpatterns = [
    path('not_in_base/', NotInBase.as_view(), name='phone_not_found'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('verificate_email/', VerificationEmail.as_view(), name='verfi_email'),
    path('verificate_email/get_token/', GetToken.as_view(), name='get_token'),
    path('forgot_password/', ForgotPassword.as_view(), name='forgot_password'),
    path('forgot_password/validate_token/', ValidateToken.as_view(), name='validate_token'),
    path('forgot_password/validate_token/error', InvalidToken.as_view(), name='invalid_token'),
    path('forgot_password/validate_token/change_password/', ChangePassword.as_view(), name='change_password'),
    path('auth/from_telegram/signup/', TelegramSignIN.as_view(), name='auth_from_tg'),

    # re_path(r'^forgot_password/validate_token/change_password/(?P<token>\w+?)/$', ChangePassword.as_view(),
    #         name='change_password'),
    path('', SignUpView.as_view(), name='signup')
]
