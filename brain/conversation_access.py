from django.http import JsonResponse


def get_session_key(request):
    if not request.session.session_key:
        request.session.create()

    return request.session.session_key


def conversation_belongs_to_user(conversation, request):
    # Logged-in user
    if request.user.is_authenticated:
        return (
            conversation.user_id == request.user.id
        )

    # Guest user
    session_key = get_session_key(request)

    return (
        conversation.user_id is None
        and conversation.session_key == session_key
    )


def unauthorized_conversation_response():
    return JsonResponse(
        {
            "error": "You do not have access to this conversation."
        },
        status=403,
    )