from django.urls import path

from .views import (
    signup_view,
    login_view,
    logout_view,

    account_recovery_view,
    forgot_password_start_view,
    forgot_password_view,
    password_reset_verify_view,
    resend_otp_view,
    password_reset_view,

    account_home_view,

    profile_view,
    edit_profile_view,

    change_password_view,

    account_settings_view,
    privacy_view,
    notifications_view,
    account_info_view,
    terms_view,
    help_view,
    tab_close_logout_view,
)


urlpatterns = [

    # =====================================================
    # AUTHENTICATION
    # =====================================================

    path(
        "signup/",
        signup_view,
        name="signup",
    ),

    path(
        "login/",
        login_view,
        name="login",
    ),

    path(
        "logout/",
        logout_view,
        name="logout",
    ),


    # =====================================================
    # ACCOUNT RECOVERY
    # =====================================================

    path(
        "account-recovery/",
        account_recovery_view,
        name="account_recovery",
    ),

    path(
        "forgot-password/start/",
        forgot_password_start_view,
        name="forgot_password_start",
    ),

    path(
        "forgot-password/",
        forgot_password_view,
        name="forgot_password",
    ),

    path(
        "password-reset/verify/",
        password_reset_verify_view,
        name="password_reset_verify",
    ),

    path(
        "password-reset/resend-otp/",
        resend_otp_view,
        name="resend_otp",
    ),

    path(
        "password-reset/",
        password_reset_view,
        name="password_reset",
    ),


    # =====================================================
    # ACCOUNT HOME
    # =====================================================

    path(
        "",
        account_home_view,
        name="accounts_home",
    ),


    # =====================================================
    # PROFILE
    # =====================================================

    path(
        "profile/",
        profile_view,
        name="profile",
    ),

    path(
        "profile/edit/",
        edit_profile_view,
        name="edit_profile",
    ),


    # =====================================================
    # ACCOUNT SECURITY
    # =====================================================

    path(
        "change-password/",
        change_password_view,
        name="change_password",
    ),


    # =====================================================
    # ACCOUNT SETTINGS
    # =====================================================

    path(
        "settings/",
        account_settings_view,
        name="account_settings",
    ),

    path(
        "privacy/",
        privacy_view,
        name="privacy",
    ),

    path(
        "notifications/",
        notifications_view,
        name="notifications",
    ),

    path(
        "account-info/",
        account_info_view,
        name="account_info",
    ),

    path(
        "terms/",
        terms_view,
        name="terms",
    ),

    path(
    "help/",
    help_view,
    name="help",
),
# =====================================================
# TAB CLOSE AUTO LOGOUT
# =====================================================

path(
    "tab-close-logout/",
    tab_close_logout_view,
    name="tab_close_logout",
),

]