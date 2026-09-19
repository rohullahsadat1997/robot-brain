from django.utils import timezone

from .models import UserUsage


PLAN_LIMITS = {
    "guest": 10,
    "registered": 50,
    "premium": 500,
    "admin": None,  # unlimited
}


def get_daily_limit(plan):
    return PLAN_LIMITS.get(plan, 50)


def reset_if_needed(usage):
    today = timezone.localdate()

    if usage.last_reset != today:
        usage.daily_messages = 0
        usage.last_reset = today

        usage.save(
            update_fields=[
                "daily_messages",
                "last_reset",
            ]
        )


def get_user_usage(user):
    usage, created = UserUsage.objects.get_or_create(
        user=user,
        defaults={
            "plan": "registered",
        },
    )

    # Django superuser همیشه Admin است
    if user.is_superuser and usage.plan != "admin":
        usage.plan = "admin"
        usage.save(update_fields=["plan"])

    reset_if_needed(usage)

    return usage


def get_guest_usage(request):
    today = timezone.localdate().isoformat()

    session_date = request.session.get("usage_date")

    if session_date != today:
        request.session["usage_date"] = today
        request.session["guest_messages"] = 0

    return request.session.get("guest_messages", 0)


def can_send_message(request):
    # Guest
    if not request.user.is_authenticated:
        count = get_guest_usage(request)
        limit = get_daily_limit("guest")

        return count < limit

    # Registered / Premium / Admin
    usage = get_user_usage(request.user)

    limit = get_daily_limit(usage.plan)

    # Admin = unlimited
    if limit is None:
        return True

    return usage.daily_messages < limit


def record_message(request):
    # Guest
    if not request.user.is_authenticated:
        count = get_guest_usage(request)

        request.session["guest_messages"] = count + 1
        request.session.modified = True

        return

    # Registered / Premium / Admin
    usage = get_user_usage(request.user)

    # Admin is unlimited
    if usage.plan == "admin":
        return

    usage.daily_messages += 1

    usage.save(
        update_fields=[
            "daily_messages",
            "last_reset",
        ]
    )


def get_remaining_messages(request):
    # Guest
    if not request.user.is_authenticated:
        count = get_guest_usage(request)
        limit = get_daily_limit("guest")

        return max(limit - count, 0)

    # Registered / Premium / Admin
    usage = get_user_usage(request.user)

    limit = get_daily_limit(usage.plan)

    # Admin = unlimited
    if limit is None:
        return None

    return max(limit - usage.daily_messages, 0)