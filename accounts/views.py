from django.contrib.auth.models import User

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required

from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from django.conf import settings

from django.utils import timezone

from .forms import (
    SignupForm,
    LoginForm,
    # ForgotPasswordForm,
    PasswordResetForm,
    EditProfileForm,
    ProfilePictureForm,
    ChangePasswordForm,
    PrivacyForm,
    NotificationForm
    
)

import random

# =====================================================
# TAB CLOSE AUTO LOGOUT
# =====================================================

@require_POST
def tab_close_logout_view(request):

    logout(request)

    return JsonResponse(
        {
            "success": True
        }
    )




# =========================================================
# SIGNUP
# =========================================================

def signup_view(request):

    if request.method == "POST":

        form = SignupForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect("login")

    else:

        form = SignupForm()

    return render(
        request,
        "accounts/signup.html",
        {"form": form},
    )

# =========================================================
# LOGIN
# =========================================================
# =========================================================
# LOGIN
# =========================================================

def login_view(request):

    # =====================================================
    # POST REQUEST
    # =====================================================

    if request.method == "POST":

        form = LoginForm(
            request,
            data=request.POST
        )


        # =================================================
        # SUCCESSFUL LOGIN
        # =================================================

        if form.is_valid():

            user = form.get_user()


            # ---------------------------------------------
            # RESET FAILED LOGIN ATTEMPTS
            # ---------------------------------------------

            request.session[
                "login_attempts"
            ] = 0


            # ---------------------------------------------
            # CLEAR OLD RECOVERY SESSION
            # ---------------------------------------------

            request.session.pop(
                "recovery_user_id",
                None
            )

            request.session.pop(
                "recovery_account",
                None
            )


            # ---------------------------------------------
            # LOGIN USER
            # ---------------------------------------------

            login(
                request,
                user
            )


            return redirect(
                "home"
            )


        # =================================================
        # FAILED LOGIN
        # =================================================

        attempts = request.session.get(
            "login_attempts",
            0
        )

        attempts += 1


        request.session[
            "login_attempts"
        ] = attempts


        # =================================================
        # THIRD FAILED LOGIN
        # =================================================

        if attempts >= 3:

            username = request.POST.get(
                "username",
                ""
            ).strip()


            # ---------------------------------------------
            # FIND USER BY USERNAME
            # ---------------------------------------------

            user = User.objects.filter(
                username__iexact=username
            ).first()


            # ---------------------------------------------
            # USER FOUND
            # ---------------------------------------------

            if user is not None:

                request.session[
                    "recovery_user_id"
                ] = user.id

                request.session[
                    "recovery_account"
                ] = user.username


                # -----------------------------------------
                # RESET RECOVERY STATE
                # -----------------------------------------

                request.session[
                    "recovery_verified"
                ] = False

                request.session.pop(
                    "recovery_code",
                    None
                )

                request.session.pop(
                    "recovery_code_created",
                    None
                )

                request.session[
                    "otp_attempts"
                ] = 0


                request.session.pop(
                    "otp_locked_until",
                    None
                )


                # -----------------------------------------
                # RESET LOGIN ATTEMPTS
                # -----------------------------------------

                request.session[
                    "login_attempts"
                ] = 0


                request.session.modified = True


                # -----------------------------------------
                # GO TO ACCOUNT RECOVERY
                # -----------------------------------------

                return redirect(
                    "account_recovery"
                )


            # ---------------------------------------------
            # USER NOT FOUND
            # ---------------------------------------------

            request.session[
                "login_attempts"
            ] = 0

            request.session.modified = True


    # =====================================================
    # GET REQUEST
    # =====================================================

    else:

        form = LoginForm()


    # =====================================================
    # SHOW LOGIN PAGE
    # =====================================================

    return render(
        request,
        "accounts/login.html",
        {
            "form": form,
        },
    )


# =========================================================
# LOGOUT
# =========================================================

def logout_view(request):

    logout(request)

    return redirect("login")


# =========================================================
# START FORGOT PASSWORD
# =========================================================

def forgot_password_start_view(request):

    # Only POST allowed
    if request.method != "POST":

        return redirect("login")


    # Get username from login form
    username = request.POST.get(
        "username",
        ""
    ).strip()


    # =====================================================
    # USERNAME EMPTY
    # =====================================================

    if not username:

        return redirect("login")


    # =====================================================
    # CHECK USERNAME IN DATABASE
    # =====================================================

    user = User.objects.filter(
        username__iexact=username
    ).first()


    # =====================================================
    # USER NOT FOUND
    # =====================================================

    if user is None:

        return render(
            request,
            "accounts/login.html",
            {
                "error":
                "Invalid username. Please enter a valid username."
            }
        )


    # =====================================================
    # USER FOUND
    # =====================================================

    request.session[
        "recovery_user_id"
    ] = user.id

    request.session[
        "recovery_account"
    ] = user.username


    # =====================================================
    # GO TO ACCOUNT RECOVERY
    # =====================================================

    return redirect(
        "account_recovery"
    )

# =========================================================
# ACCOUNT RECOVERY
# =========================================================

def account_recovery_view(request):

    # =====================================================
    # GET RECOVERY USER
    # =====================================================

    user_id = request.session.get(
        "recovery_user_id"
    )

    recovery_account = request.session.get(
        "recovery_account"
    )


    # =====================================================
    # RECOVERY SESSION REQUIRED
    # =====================================================

    if not user_id or not recovery_account:

        return redirect(
            "login"
        )


    # =====================================================
    # VERIFY USER STILL EXISTS
    # =====================================================

    try:

        user = User.objects.get(
            id=user_id
        )

    except User.DoesNotExist:

        request.session.pop(
            "recovery_user_id",
            None
        )

        request.session.pop(
            "recovery_account",
            None
        )

        return redirect(
            "login"
        )


    # =====================================================
    # KEEP SESSION ACCOUNT CONSISTENT
    # =====================================================

    request.session[
        "recovery_account"
    ] = user.username


    # =====================================================
    # SHOW ACCOUNT RECOVERY
    # =====================================================

    return render(
        request,
        "accounts/account_recovery.html",
        {
            "account": user.username,
        },
    )

# =========================================================
# FORGOT PASSWORD / SEND OTP
# =========================================================

def forgot_password_view(request):

    # =====================================================
    # RECOVERY USER MUST EXIST
    # =====================================================

    user_id = request.session.get(
        "recovery_user_id"
    )

    if not user_id:

        return redirect(
            "login"
        )


    # =====================================================
    # GET USER FROM DATABASE
    # =====================================================

    try:

        user = User.objects.get(
            id=user_id
        )

    except User.DoesNotExist:

        request.session.flush()

        return redirect(
            "login"
        )


    # =====================================================
    # CHECK REGISTERED EMAIL
    # =====================================================

    if not user.email:

        return render(
            request,
            "accounts/account_recovery.html",
            {
                "account": user.username,

                "error":
                "This account does not have a registered email address.",
            },
        )


    # =====================================================
    # GENERATE 6-DIGIT OTP
    # =====================================================

    verification_code = str(
        random.randint(
            100000,
            999999
        )
    )


    # =====================================================
    # SAVE RECOVERY SESSION
    # =====================================================

    request.session[
        "recovery_user_id"
    ] = user.id

    request.session[
        "recovery_account"
    ] = user.username

    request.session[
        "recovery_code"
    ] = verification_code

    request.session[
        "recovery_code_created"
    ] = timezone.now().timestamp()

    request.session[
        "recovery_verified"
    ] = False


    # Reset OTP attempts
    request.session[
        "otp_attempts"
    ] = 0


    # =====================================================
    # DEVELOPMENT TERMINAL OUTPUT
    # =====================================================

    print(
        "========================================"
    )

    print(
        "MEETCLONE PASSWORD RESET"
    )

    print(
        "OTP:",
        verification_code
    )

    print(
        "SEND TO:",
        user.email
    )

    print(
        "VALID FOR: 5 MINUTES"
    )

    print(
        "========================================"
    )


    # =====================================================
    # SEND OTP
    # =====================================================

    send_mail(

        subject=(
            "MeetClone Password Reset Code"
        ),

        message=(

            "Hello,\n\n"

            "Your MeetClone password "
            "reset verification code is:\n\n"

            f"{verification_code}\n\n"

            "This code is valid for "
            "5 minutes only.\n\n"

            "If you did not request a "
            "password reset, you can safely "
            "ignore this email.\n\n"

            "Regards,\n"
            "MeetClone"
        ),

        from_email=(
            settings.DEFAULT_FROM_EMAIL
        ),

        recipient_list=[
            user.email
        ],

        fail_silently=False,
    )


    # =====================================================
    # GO TO OTP PAGE
    # =====================================================

    return redirect(
        "password_reset_verify"
    )





# =========================================================
# PASSWORD RESET OTP VERIFICATION
# =========================================================

def password_reset_verify_view(request):

    user_id = request.session.get(
        "recovery_user_id"
    )

    verification_code = request.session.get(
        "recovery_code"
    )

    created_timestamp = request.session.get(
        "recovery_code_created"
    )


    # =====================================================
    # CHECK RECOVERY SESSION
    # =====================================================

    if (
        not user_id
        or not verification_code
        or not created_timestamp
    ):

        return redirect(
            "forgot_password"
        )


    # =====================================================
    # OTP EXPIRY
    # =====================================================

    current_timestamp = (
        timezone.now().timestamp()
    )

    otp_age = (
        current_timestamp
        - created_timestamp
    )

    OTP_EXPIRY_SECONDS = 5 * 60


    # =====================================================
    # OTP EXPIRED
    # =====================================================

    if otp_age >= OTP_EXPIRY_SECONDS:

        request.session.pop(
            "recovery_code",
            None
        )

        request.session.pop(
            "recovery_code_created",
            None
        )

        request.session[
            "recovery_verified"
        ] = False


        return render(
            request,
            "accounts/password_reset_verify.html",
            {
                "account":
                request.session.get(
                    "recovery_account",
                    ""
                ),

                "error":
                "This verification code has expired. Please request a new code."
            },
        )


    # =====================================================
    # POST
    # =====================================================

    if request.method == "POST":

        entered_code = request.POST.get(
            "verification_code",
            ""
        ).strip()


        # =================================================
        # EMPTY OTP
        # =================================================

        if not entered_code:

            return render(
                request,
                "accounts/password_reset_verify.html",
                {
                    "account":
                    request.session.get(
                        "recovery_account",
                        ""
                    ),

                    "error":
                    "Please enter the verification code."
                },
            )


        # =================================================
        # INVALID FORMAT
        # =================================================

        if (
            len(entered_code) != 6
            or not entered_code.isdigit()
        ):

            return render(
                request,
                "accounts/password_reset_verify.html",
                {
                    "account":
                    request.session.get(
                        "recovery_account",
                        ""
                    ),

                    "error":
                    "Please enter a valid 6-digit verification code."
                },
            )


        # =================================================
        # CORRECT OTP
        # =================================================

        if entered_code == verification_code:

            request.session[
                "recovery_verified"
            ] = True


            # OTP cannot be reused

            request.session.pop(
                "recovery_code",
                None
            )

            request.session.pop(
                "recovery_code_created",
                None
            )


            return redirect(
                "password_reset"
            )


        # =================================================
        # WRONG OTP
        # =================================================

        return render(
            request,
            "accounts/password_reset_verify.html",
            {
                "account":
                request.session.get(
                    "recovery_account",
                    ""
                ),

                "error":
                "Invalid verification code. Please check the code and try again."
            },
        )


    # =====================================================
    # GET
    # =====================================================

    return render(
        request,
        "accounts/password_reset_verify.html",
        {
            "account":
            request.session.get(
                "recovery_account",
                ""
            ),
        },
    )


# =========================================================
# REGENERATE / RESEND OTP
# =========================================================

def resend_otp_view(request):

    # Only POST allowed
    if request.method != "POST":

        return redirect(
            "password_reset_verify"
        )


    user_id = request.session.get(
        "recovery_user_id"
    )


    # =====================================================
    # CHECK RECOVERY USER
    # =====================================================

    if not user_id:

        return redirect(
            "login"
        )


    # =====================================================
    # GET USER
    # =====================================================

    try:

        user = User.objects.get(
            id=user_id
        )

    except User.DoesNotExist:

        request.session.flush()

        return redirect(
            "login"
        )


    # =====================================================
    # CHECK EMAIL
    # =====================================================

    if not user.email:

        return render(
            request,
            "accounts/password_reset_verify.html",
            {
                "account": user.username,

                "error":
                "No email address is registered with this account."
            },
        )


    # =====================================================
    # GENERATE NEW OTP
    # =====================================================

    verification_code = str(
        random.randint(
            100000,
            999999
        )
    )


    # =====================================================
    # SAVE NEW OTP
    # =====================================================

    request.session[
        "recovery_code"
    ] = verification_code

    request.session[
        "recovery_code_created"
    ] = timezone.now().timestamp()

    request.session[
        "recovery_verified"
    ] = False


    # New OTP starts fresh
    request.session[
        "otp_attempts"
    ] = 0


    # =====================================================
    # DEVELOPMENT TERMINAL
    # =====================================================

    print(
        "========================================"
    )

    print(
        "MEETCLONE NEW PASSWORD RESET OTP"
    )

    print(
        "OTP:",
        verification_code
    )

    print(
        "SEND TO:",
        user.email
    )

    print(
        "VALID FOR: 5 MINUTES"
    )

    print(
        "========================================"
    )


    # =====================================================
    # SEND NEW OTP
    # =====================================================

    send_mail(

        subject=(
            "MeetClone New Password Reset Code"
        ),

        message=(

            "Hello,\n\n"

            "Your new MeetClone password "
            "reset verification code is:\n\n"

            f"{verification_code}\n\n"

            "This code is valid for "
            "5 minutes only.\n\n"

            "If you did not request a "
            "password reset, you can safely "
            "ignore this email.\n\n"

            "Regards,\n"
            "MeetClone"
        ),

        from_email=(
            settings.DEFAULT_FROM_EMAIL
        ),

        recipient_list=[
            user.email
        ],

        fail_silently=False,
    )


    # =====================================================
    # RETURN TO OTP PAGE
    # =====================================================

    return redirect(
        "password_reset_verify"
    )

# =========================================================
# CREATE NEW PASSWORD PAGE
# =========================================================

def password_reset_view(request):

    user_id = request.session.get(
        "recovery_user_id"
    )

    verified = request.session.get(
        "recovery_verified",
        False
    )


    # =====================================================
    # OTP MUST BE VERIFIED
    # =====================================================

    if not user_id or not verified:

        return redirect(
            "forgot_password"
        )


    # =====================================================
    # GET USER
    # =====================================================

    try:

        user = User.objects.get(
            id=user_id
        )

    except User.DoesNotExist:

        request.session.flush()

        return redirect(
            "login"
        )


    # =====================================================
    # POST
    # =====================================================

    if request.method == "POST":

        form = PasswordResetForm(
            request.POST
        )

        if form.is_valid():

            new_password = form.cleaned_data[
                "new_password"
            ]


            # =============================================
            # SET NEW PASSWORD
            # =============================================

            user.set_password(
                new_password
            )

            user.save()


            # =============================================
            # CLEAR RECOVERY SESSION
            # =============================================

            request.session.pop(
                "recovery_user_id",
                None
            )

            request.session.pop(
                "recovery_account",
                None
            )

            request.session.pop(
                "recovery_code",
                None
            )

            request.session.pop(
                "recovery_code_created",
                None
            )

            request.session.pop(
                "recovery_verified",
                None
            )

            request.session.pop(
                "otp_attempts",
                None
            )

            request.session.pop(
                "otp_locked_until",
                None
            )


            request.session.modified = True


            # =============================================
            # PASSWORD RESET COMPLETE
            # =============================================

            return redirect(
                "login"
            )


    else:

        form = PasswordResetForm()


    # =====================================================
    # SHOW NEW PASSWORD PAGE
    # =====================================================

    return render(
        request,
        "accounts/password_reset.html",
        {
            "form": form,

            "account": user.username,
        },
    )

# =========================================================
# PROFILE
# =========================================================

@login_required
def profile_view(request):

    profile = request.user.profile

    return render(
        request,
        "accounts/profile.html",
        {
            "profile": profile,
        },
    )


# =========================================================
# EDIT PROFILE
# =========================================================

@login_required
def edit_profile_view(request):

    # =====================================================
    # GET CURRENT PROFILE
    # =====================================================

    profile = request.user.profile


    # =====================================================
    # POST
    # =====================================================

    if request.method == "POST":

        user_form = EditProfileForm(
            request.POST,
            instance=request.user
        )

        profile_form = ProfilePictureForm(
            request.POST,
            request.FILES,
            instance=profile
        )


        # =================================================
        # VALIDATE BOTH FORMS
        # =================================================

        if (
            user_form.is_valid()
            and profile_form.is_valid()
        ):

            # ---------------------------------------------
            # SAVE USER INFORMATION
            # ---------------------------------------------

            user_form.save()


            # ---------------------------------------------
            # SAVE PROFILE INFORMATION
            # ---------------------------------------------

            profile_form.save()


            # ---------------------------------------------
            # RETURN TO PROFILE
            # ---------------------------------------------

            return redirect(
                "profile"
            )


    # =====================================================
    # GET
    # =====================================================

    else:

        user_form = EditProfileForm(
            instance=request.user
        )

        profile_form = ProfilePictureForm(
            instance=profile
        )


    # =====================================================
    # EDIT PROFILE PAGE
    # =====================================================

    return render(
        request,
        "accounts/edit_profile.html",
        {
            "user_form": user_form,
            "profile_form": profile_form,
            "profile": profile,
        },
    )


# =========================================================
# CHANGE PASSWORD
# =========================================================

@login_required
def change_password_view(request):

    # =====================================================
    # CURRENT USER
    # =====================================================

    user = request.user


    # =====================================================
    # POST
    # =====================================================

    if request.method == "POST":

        form = ChangePasswordForm(
            request.POST
        )


        # =================================================
        # FORM VALIDATION
        # =================================================

        if form.is_valid():

            current_password = form.cleaned_data[
                "current_password"
            ]

            new_password = form.cleaned_data[
                "new_password"
            ]


            # =================================================
            # CHECK CURRENT PASSWORD
            # =================================================

            if not user.check_password(
                current_password
            ):

                form.add_error(
                    "current_password",
                    "Current password is incorrect. Please try again."
                )


            else:

                # =============================================
                # SET NEW PASSWORD
                # =============================================

                user.set_password(
                    new_password
                )

                user.save()


                # =============================================
                # KEEP USER LOGGED IN
                # =============================================

                from django.contrib.auth import (
                    update_session_auth_hash
                )

                update_session_auth_hash(
                    request,
                    user
                )


                # =============================================
                # SUCCESS
                # =============================================

                return redirect(
                    "profile"
                )


    # =====================================================
    # GET
    # =====================================================

    else:

        form = ChangePasswordForm()


    # =====================================================
    # SHOW CHANGE PASSWORD PAGE
    # =====================================================

    return render(
        request,
        "accounts/change_password.html",
        {
            "form": form,

            # Current logged-in user
            "account": user,

            # Actual Django User ID
            "user_id": user.id,

            # Username
            "username": user.username,

            # Email
            "email": user.email,
        },
    )

# =========================================================
# ACCOUNT SETTINGS
# =========================================================

@login_required
def account_settings_view(request):

    return render(
        request,
        "accounts/account_settings.html",
    )

# =========================================================
# PRIVACY SETTINGS
# =========================================================

@login_required
def privacy_view(request):

    # =====================================================
    # CURRENT USER PROFILE
    # =====================================================

    profile = request.user.profile


    # =====================================================
    # POST
    # =====================================================

    if request.method == "POST":

        form = PrivacyForm(
            request.POST
        )


        # =================================================
        # FORM VALIDATION
        # =================================================

        if form.is_valid():

            # =============================================
            # SAVE PROFILE VISIBILITY
            # =============================================

            profile.profile_visibility = (
                form.cleaned_data[
                    "profile_visibility"
                ]
            )


            # =============================================
            # SAVE MESSAGE PRIVACY
            # =============================================

            profile.message_privacy = (
                form.cleaned_data[
                    "message_privacy"
                ]
            )


            # =============================================
            # SAVE PROFILE
            # =============================================

            profile.save()


            # =============================================
            # REDIRECT AFTER SAVE
            # =============================================

            return redirect(
                "privacy"
            )


    # =====================================================
    # GET
    # =====================================================

    else:

        form = PrivacyForm(
            initial={
                "profile_visibility":
                    profile.profile_visibility,

                "message_privacy":
                    profile.message_privacy,
            }
        )


    # =====================================================
    # SHOW PRIVACY PAGE
    # =====================================================

    return render(
        request,
        "accounts/privacy.html",
        {
            "form": form,
            "profile": profile,
        },
    )


# =========================================================
# NOTIFICATION SETTINGS
# =========================================================

@login_required
def notifications_view(request):

    # =====================================================
    # CURRENT USER PROFILE
    # =====================================================

    profile = request.user.profile


    # =====================================================
    # POST
    # =====================================================

    if request.method == "POST":

        form = NotificationForm(
            request.POST
        )


        # =================================================
        # FORM VALIDATION
        # =================================================

        if form.is_valid():

            # =============================================
            # EMAIL NOTIFICATIONS
            # =============================================

            profile.email_notifications = (
                form.cleaned_data[
                    "email_notifications"
                ]
            )


            # =============================================
            # LOGIN ALERTS
            # =============================================

            profile.login_alerts = (
                form.cleaned_data[
                    "login_alerts"
                ]
            )


            # =============================================
            # MEETING NOTIFICATIONS
            # =============================================

            profile.meeting_notifications = (
                form.cleaned_data[
                    "meeting_notifications"
                ]
            )


            # =============================================
            # ACCOUNT ACTIVITY
            # =============================================

            profile.account_activity_notifications = (
                form.cleaned_data[
                    "account_activity_notifications"
                ]
            )


            # =============================================
            # SAVE
            # =============================================

            profile.save()


            # =============================================
            # REDIRECT
            # =============================================

            return redirect(
                "notifications"
            )


    # =====================================================
    # GET
    # =====================================================

    else:

        form = NotificationForm(
            initial={
                "email_notifications":
                    profile.email_notifications,

                "login_alerts":
                    profile.login_alerts,

                "meeting_notifications":
                    profile.meeting_notifications,

                "account_activity_notifications":
                    profile.account_activity_notifications,
            }
        )


    # =====================================================
    # SHOW PAGE
    # =====================================================

    return render(
        request,
        "accounts/notifications.html",
        {
            "form": form,
            "profile": profile,
        },
    )

@login_required
def account_home_view(request):

    return render(
        request,
        "accounts/account_home.html",
    )

# =========================================================
# ACCOUNT INFORMATION
# =========================================================

@login_required
def account_info_view(request):

    user = request.user

    return render(
        request,
        "accounts/account_info.html",
        {
            "user": user,
        },
    )



# =========================================================
# TERMS OF SERVICE
# =========================================================


def terms_view(request):

    return render(
        request,
        "accounts/terms.html",
    )


# =========================================================
# HELP CENTER
# =========================================================


def help_view(request):

    return render(
        request,
        "accounts/help.html",
    )