from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .usage import get_user_usage, get_daily_limit, get_remaining_messages

import json


# =========================================================
# REGISTER
# =========================================================
def register_page(request):
    return render(request, "brain/register.html")
@csrf_exempt
def register(request):

    if request.method != "POST":
        return JsonResponse(
            {"error": "Only POST requests are allowed"},
            status=405,
        )

    try:
        data = json.loads(request.body)

        username = data.get("username", "").strip()
        email = data.get("email", "").strip().lower()
        password = data.get("password", "")

        if not username or not email or not password:
            return JsonResponse(
                {
                    "error": "Username, email and password are required."
                },
                status=400,
            )

        if User.objects.filter(username=username).exists():
            return JsonResponse(
                {
                    "error": "Username already exists."
                },
                status=400,
            )

        if User.objects.filter(email=email).exists():
            return JsonResponse(
                {
                    "error": "Email already exists."
                },
                status=400,
            )

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )

        login(request, user)

        return JsonResponse(
            {
                "message": "Registration successful.",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                },
            },
            status=201,
        )

    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON."},
            status=400,
        )

    except Exception as e:
        return JsonResponse(
            {"error": str(e)},
            status=400,
        )


# =========================================================
# LOGIN
# =========================================================

@csrf_exempt
def login_view(request):

    if request.method != "POST":
        return JsonResponse(
            {"error": "Only POST requests are allowed"},
            status=405,
        )

    try:
        data = json.loads(request.body)

        email = data.get("email", "").strip().lower()
        password = data.get("password", "")

        if not email or not password:
            return JsonResponse(
                {
                    "error": "Email and password are required."
                },
                status=400,
            )

        try:
            user_by_email = User.objects.get(email=email)
        except User.DoesNotExist:
            user_by_email = None

        user = None

        if user_by_email:
            user = authenticate(
                request,
                username=user_by_email.username,
                password=password,
            )

        if user is None:
            return JsonResponse(
                {
                    "error": "Invalid email or password."
                },
                status=401,
            )

        login(request, user)

        return JsonResponse(
            {
                "message": "Login successful.",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                },
            },
            status=200,
        )

    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON."},
            status=400,
        )

    except Exception as e:
        return JsonResponse(
            {"error": str(e)},
            status=400,
        )


# =========================================================
# LOGOUT
# =========================================================

@csrf_exempt
def logout_view(request):

    if request.method != "POST":
        return JsonResponse(
            {"error": "Only POST requests are allowed"},
            status=405,
        )

    logout(request)

    return JsonResponse(
        {
            "message": "Logout successful."
        },
        status=200,
    )


# =========================================================
# CURRENT USER
# =========================================================

def current_user(request):

    if not request.user.is_authenticated:
        return JsonResponse(
            {
                "authenticated": False,
                "user": None,
            }
        )

    return JsonResponse(
        {
            "authenticated": True,
            "user": {
                "id": request.user.id,
                "username": request.user.username,
                "email": request.user.email,
            },
        }
    )
    

def account_api(request):

    if not request.user.is_authenticated:
        return JsonResponse(
            {
                "authenticated": False,
                "error": "Authentication required."
            },
            status=401
        )

    usage = get_user_usage(request.user)
    limit = get_daily_limit(usage.plan)
    remaining = get_remaining_messages(request)

    return JsonResponse({
        "authenticated": True,

        "user": {
            "id": request.user.id,
            "username": request.user.username,
            "email": request.user.email,
        },

        "usage": {
            "plan": usage.plan,
            "daily_messages": usage.daily_messages,
            "limit": limit,
            "remaining": remaining,
        }
    })