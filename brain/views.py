import json
import os
import tempfile
import traceback

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

from .models import Conversation, Message, Memory
from .services import BrainEngine
from .conversation_access import (
    get_session_key,
    conversation_belongs_to_user,
    unauthorized_conversation_response,
)
from .usage import (
    can_send_message,
    record_message,
    get_remaining_messages,
)
from .providers.factory import get_speech_provider




# =========================================================
# HELPERS
# =========================================================

def assign_conversation_owner(conversation, request):
    """
    مشخص کردن مالک گفتگو.

    کاربر واردشده:
        conversation.user = request.user

    مهمان:
        conversation.user = None
        conversation.session_key = session key
    """

    if request.user.is_authenticated:
        conversation.user = request.user
        conversation.session_key = None
    else:
        conversation.user = None
        conversation.session_key = get_session_key(request)

    conversation.save(
        update_fields=["user", "session_key"]
    )

    return conversation


def get_owned_conversation(request, conversation_id):
    """
    فقط گفتگویی را برمی‌گرداند که متعلق به همین
    کاربر یا session باشد.
    """

    conversation = Conversation.objects.get(
        id=conversation_id
    )

    if not conversation_belongs_to_user(
        conversation,
        request,
    ):
        return None

    return conversation


def serialize_memory(memory):
    return {
        "id": memory.id,
        "type": memory.memory_type,
        "title": memory.title,
        "content": memory.content,
        "importance": memory.importance,
        "created_at": memory.created_at,
    }


def serialize_message(message):
    return {
        "id": message.id,
        "role": message.role,
        "content": message.content,
        "created_at": message.created_at,
    }


# =========================================================
# MEMORY
# =========================================================

@csrf_exempt
def create_memory(request):

    if request.method != "POST":
        return JsonResponse(
            {"error": "Only POST requests are allowed"},
            status=405,
        )

    try:
        data = json.loads(request.body)

        title = data.get("title")
        content = data.get("content")

        if not title or not content:
            return JsonResponse(
                {
                    "error": "title and content are required"
                },
                status=400,
            )

        memory = Memory.objects.create(
            memory_type=data.get(
                "memory_type",
                "fact",
            ),
            title=title,
            content=content,
            importance=data.get(
                "importance",
                5,
            ),
        )

        return JsonResponse(
            {
                "message": "Memory created successfully",
                "memory": serialize_memory(memory),
            },
            status=201,
        )

    except Exception as e:
        traceback.print_exc()

        return JsonResponse(
            {"error": str(e)},
            status=400,
        )


def list_memories(request):

    memories = Memory.objects.all().order_by(
        "-created_at"
    )

    data = [
        serialize_memory(memory)
        for memory in memories
    ]

    return JsonResponse(
        {"memories": data}
    )


# =========================================================
# CHAT
# =========================================================

@csrf_exempt
def chat(request):

    if request.method != "POST":
        return JsonResponse(
            {"error": "Only POST requests are allowed"},
            status=405,
        )

    try:

        # -------------------------------------------------
        # 1. CHECK USAGE LIMIT
        # -------------------------------------------------

        if not can_send_message(request):

            remaining = get_remaining_messages(
                request
            )

            return JsonResponse(
                {
                    "error": "Daily message limit reached.",
                    "remaining_messages": remaining,
                },
                status=429,
            )

        # -------------------------------------------------
        # 2. READ REQUEST
        # -------------------------------------------------

        data = json.loads(request.body)

        message_text = data.get(
            "message",
            ""
        ).strip()

        conversation_id = data.get(
            "conversation_id"
        )

        if not message_text:

            return JsonResponse(
                {
                    "error": "Message is required."
                },
                status=400,
            )

        brain = BrainEngine()

        # -------------------------------------------------
        # 3. GET / CREATE CONVERSATION
        # -------------------------------------------------

        if conversation_id:

            try:
                conversation = get_owned_conversation(
                    request,
                    conversation_id,
                )

            except Conversation.DoesNotExist:

                return JsonResponse(
                    {
                        "error": "Conversation not found"
                    },
                    status=404,
                )

            if conversation is None:

                return unauthorized_conversation_response()

        else:

            title = (
                brain.generate_local_conversation_title(
                    message_text
                )
            )

            conversation = brain.create_conversation(
                title=title
            )

            assign_conversation_owner(
                conversation,
                request,
            )

        # -------------------------------------------------
        # 4. SAVE USER MESSAGE
        # -------------------------------------------------

        brain.add_message(
            conversation=conversation,
            role="user",
            content=message_text,
        )

        # -------------------------------------------------
        # 5. MEMORY ANALYSIS
        # -------------------------------------------------

        memory_created = None
        memory_updated = None
        memory_action = "none"

        memory_analysis = brain.analyze_memory(
            message_text
        )

        question = brain.is_question(
            message_text
        )

        if (
            memory_analysis.get(
                "should_remember"
            )
            and not question
        ):

            related_memory = (
                brain.find_related_memory(
                    message_text
                )
            )

            update_analysis = (
                brain.analyze_memory_update(
                    message_text,
                    related_memory,
                )
            )

            memory_action = (
                update_analysis.get(
                    "action",
                    "none",
                )
            )

            # ---------------------------------------------
            # NEW MEMORY
            # ---------------------------------------------

            if memory_action == "new":

                memory_created = brain.remember(

                    title=update_analysis.get(
                        "title",
                        memory_analysis.get(
                            "title",
                            "User Information",
                        ),
                    ),

                    content=update_analysis.get(
                        "content",
                        message_text,
                    ),

                    memory_type=update_analysis.get(
                        "memory_type",
                        memory_analysis.get(
                            "memory_type",
                            "fact",
                        ),
                    ),

                    importance=update_analysis.get(
                        "importance",
                        memory_analysis.get(
                            "importance",
                            5,
                        ),
                    ),
                )

            # ---------------------------------------------
            # UPDATE MEMORY
            # ---------------------------------------------

            elif (
                memory_action == "update"
                and related_memory
            ):

                related_memory.title = (
                    update_analysis.get(
                        "title",
                        related_memory.title,
                    )
                )

                related_memory.content = (
                    update_analysis.get(
                        "content",
                        related_memory.content,
                    )
                )

                related_memory.memory_type = (
                    update_analysis.get(
                        "memory_type",
                        related_memory.memory_type,
                    )
                )

                related_memory.importance = (
                    update_analysis.get(
                        "importance",
                        related_memory.importance,
                    )
                )

                related_memory.save()

                memory_updated = related_memory

            # ---------------------------------------------
            # DUPLICATE
            # ---------------------------------------------

            elif memory_action == "duplicate":

                # هیچ کاری انجام نمی‌دهیم.
                pass

        # -------------------------------------------------
        # 6. GENERATE BRAIN RESPONSE
        # -------------------------------------------------

        assistant_text = brain.generate_response(
            message=message_text,
            conversation=conversation,
        )

        # -------------------------------------------------
        # 7. SAVE ASSISTANT MESSAGE
        # -------------------------------------------------

        assistant_message = brain.add_message(
            conversation=conversation,
            role="assistant",
            content=assistant_text,
        )

        # -------------------------------------------------
        # 8. RECORD USAGE
        # -------------------------------------------------

        record_message(request)

        # -------------------------------------------------
        # 9. GET HISTORY
        # -------------------------------------------------

        history = brain.get_conversation_history(
            conversation
        )

        # -------------------------------------------------
        # 10. RESPONSE
        # -------------------------------------------------

        response_data = {

            "conversation_id":
                conversation.id,

            "history":
                history,

            "assistant_message": {
                "id":
                    assistant_message.id,

                "content":
                    assistant_message.content,
            },

            "memory_action":
                memory_action,

            "memory_created":
                bool(memory_created),

            "memory_updated":
                bool(memory_updated),

            "remaining_messages":
                get_remaining_messages(request),
        }

        # -------------------------------------------------
        # CREATED MEMORY
        # -------------------------------------------------

        if memory_created:

            response_data["memory"] = (
                serialize_memory(
                    memory_created
                )
            )

        # -------------------------------------------------
        # UPDATED MEMORY
        # -------------------------------------------------

        if memory_updated:

            response_data["updated_memory"] = (
                serialize_memory(
                    memory_updated
                )
            )

        return JsonResponse(
            response_data,
            status=201,
        )

    except Conversation.DoesNotExist:

        return JsonResponse(
            {
                "error":
                    "Conversation not found"
            },
            status=404,
        )

    except Exception as e:

        traceback.print_exc()

        return JsonResponse(
            {
                "error": str(e)
            },
            status=400,
        )


# =========================================================
# CONVERSATIONS
# =========================================================

def list_conversations(request):

    if request.method != "GET":

        return JsonResponse(
            {
                "error":
                    "Only GET requests are allowed"
            },
            status=405,
        )

    # -----------------------------------------------------
    # ONLY OWN CONVERSATIONS
    # -----------------------------------------------------

    if request.user.is_authenticated:

        conversations = (
            Conversation.objects
            .filter(
                user=request.user
            )
            .prefetch_related("messages")
            .order_by("-updated_at")
        )

    else:

        session_key = get_session_key(
            request
        )

        conversations = (
            Conversation.objects
            .filter(
                user__isnull=True,
                session_key=session_key,
            )
            .prefetch_related("messages")
            .order_by("-updated_at")
        )

    data = []

    for conversation in conversations:

        last_message = (
            conversation.messages
            .order_by("-created_at")
            .first()
        )

        data.append(
            {
                "id":
                    conversation.id,

                "title":
                    conversation.title,

                "preview":
                    (
                        last_message.content[:100]
                        if last_message
                        else ""
                    ),

                "updated_at":
                    conversation.updated_at,
            }
        )

    return JsonResponse(
        {
            "conversations":
                data
        }
    )


# =========================================================
# CONVERSATION HISTORY
# =========================================================

def conversation_history(
    request,
    conversation_id,
):

    if request.method != "GET":

        return JsonResponse(
            {
                "error":
                    "Only GET requests are allowed"
            },
            status=405,
        )

    try:

        conversation = get_owned_conversation(
            request,
            conversation_id,
        )

        if conversation is None:

            return unauthorized_conversation_response()

        messages = (
            conversation.messages
            .all()
            .order_by("created_at")
        )

        data = [
            serialize_message(message)
            for message in messages
        ]

        return JsonResponse(
            {
                "conversation_id":
                    conversation.id,

                "title":
                    conversation.title,

                "messages":
                    data,
            }
        )

    except Conversation.DoesNotExist:

        return JsonResponse(
            {
                "error":
                    "Conversation not found"
            },
            status=404,
        )


# =========================================================
# DELETE CONVERSATION
# =========================================================

@csrf_exempt
def delete_conversation(
    request,
    conversation_id,
):

    if request.method != "DELETE":

        return JsonResponse(
            {
                "error":
                    "Only DELETE requests are allowed"
            },
            status=405,
        )

    try:

        conversation = get_owned_conversation(
            request,
            conversation_id,
        )

        if conversation is None:

            return unauthorized_conversation_response()

        conversation.delete()

        return JsonResponse(
            {
                "message":
                    "Conversation deleted successfully"
            }
        )

    except Conversation.DoesNotExist:

        return JsonResponse(
            {
                "error":
                    "Conversation not found"
            },
            status=404,
        )


# =========================================================
# VOICE TEST
# =========================================================

@csrf_exempt
def voice_test(request):

    if request.method != "POST":

        return JsonResponse(
            {
                "error": "Only POST requests are allowed"
            },
            status=405,
        )

    # -----------------------------------------------------
    # 1. CHECK USAGE LIMIT
    # -----------------------------------------------------

    if not can_send_message(request):

        remaining = get_remaining_messages(request)

        return JsonResponse(
            {
                "error": "Daily message limit reached.",
                "remaining_messages": remaining,
            },
            status=429,
        )

    audio_file = request.FILES.get("audio")

    if not audio_file:

        return JsonResponse(
            {
                "error": "Audio file is required."
            },
            status=400,
        )

    temp_path = None

    try:

        # -------------------------------------------------
        # 2. SAVE TEMPORARY AUDIO FILE
        # -------------------------------------------------

        suffix = os.path.splitext(
            audio_file.name
        )[1]

        if not suffix:
            suffix = ".webm"

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix,
        ) as temp_file:

            for chunk in audio_file.chunks():
                temp_file.write(chunk)

            temp_path = temp_file.name

        # -------------------------------------------------
        # 3. SPEECH TO TEXT
        # -------------------------------------------------

        speech_provider = get_speech_provider()

        transcript = speech_provider.transcribe(
            temp_path
        )

        transcript = transcript.strip()

        if not transcript:

            return JsonResponse(
                {
                    "error": "Could not understand the audio."
                },
                status=400,
            )

        # -------------------------------------------------
        # 4. CREATE BRAIN
        # -------------------------------------------------

        brain = BrainEngine()

        # -------------------------------------------------
        # 5. GET / CREATE CONVERSATION
        # -------------------------------------------------

        conversation_id = request.POST.get(
            "conversation_id"
        )

        if conversation_id:

            try:

                conversation = get_owned_conversation(
                    request,
                    int(conversation_id),
                )

            except Conversation.DoesNotExist:

                return JsonResponse(
                    {
                        "error": "Conversation not found"
                    },
                    status=404,
                )

            if conversation is None:

                return unauthorized_conversation_response()

        else:

            title = (
                brain.generate_local_conversation_title(
                    transcript
                )
            )

            conversation = brain.create_conversation(
                title=title
            )

            assign_conversation_owner(
                conversation,
                request,
            )

        # -------------------------------------------------
        # 6. SAVE USER MESSAGE
        # -------------------------------------------------

        brain.add_message(
            conversation=conversation,
            role="user",
            content=transcript,
        )

        # -------------------------------------------------
        # 7. MEMORY ANALYSIS
        # -------------------------------------------------

        memory_created = None
        memory_updated = None
        memory_action = "none"

        memory_analysis = brain.analyze_memory(
            transcript
        )

        question = brain.is_question(
            transcript
        )

        if (
            memory_analysis.get(
                "should_remember"
            )
            and not question
        ):

            related_memory = (
                brain.find_related_memory(
                    transcript
                )
            )

            update_analysis = (
                brain.analyze_memory_update(
                    transcript,
                    related_memory,
                )
            )

            memory_action = (
                update_analysis.get(
                    "action",
                    "none",
                )
            )

            # ---------------------------------------------
            # NEW MEMORY
            # ---------------------------------------------

            if memory_action == "new":

                memory_created = brain.remember(

                    title=update_analysis.get(
                        "title",
                        memory_analysis.get(
                            "title",
                            "User Information",
                        ),
                    ),

                    content=update_analysis.get(
                        "content",
                        transcript,
                    ),

                    memory_type=update_analysis.get(
                        "memory_type",
                        memory_analysis.get(
                            "memory_type",
                            "fact",
                        ),
                    ),

                    importance=update_analysis.get(
                        "importance",
                        memory_analysis.get(
                            "importance",
                            5,
                        ),
                    ),
                )

            # ---------------------------------------------
            # UPDATE MEMORY
            # ---------------------------------------------

            elif (
                memory_action == "update"
                and related_memory
            ):

                related_memory.title = (
                    update_analysis.get(
                        "title",
                        related_memory.title,
                    )
                )

                related_memory.content = (
                    update_analysis.get(
                        "content",
                        related_memory.content,
                    )
                )

                related_memory.memory_type = (
                    update_analysis.get(
                        "memory_type",
                        related_memory.memory_type,
                    )
                )

                related_memory.importance = (
                    update_analysis.get(
                        "importance",
                        related_memory.importance,
                    )
                )

                related_memory.save()

                memory_updated = related_memory

            # ---------------------------------------------
            # DUPLICATE
            # ---------------------------------------------

            elif memory_action == "duplicate":

                pass

        # -------------------------------------------------
        # 8. GENERATE BRAIN RESPONSE
        # -------------------------------------------------

        assistant_text = brain.generate_response(
            message=transcript,
            conversation=conversation,
        )

        # -------------------------------------------------
        # 9. SAVE ASSISTANT MESSAGE
        # -------------------------------------------------

        assistant_message = brain.add_message(
            conversation=conversation,
            role="assistant",
            content=assistant_text,
        )

        # -------------------------------------------------
        # 10. RECORD USAGE
        # -------------------------------------------------

        record_message(request)

        # -------------------------------------------------
        # 11. GET HISTORY
        # -------------------------------------------------

        history = brain.get_conversation_history(
            conversation
        )

        # -------------------------------------------------
        # 12. RESPONSE
        # -------------------------------------------------

        response_data = {

            "success": True,

            "conversation_id":
                conversation.id,

            "transcript":
                transcript,

            "history":
                history,

            "assistant_message": {
                "id":
                    assistant_message.id,

                "content":
                    assistant_message.content,
            },

            "memory_action":
                memory_action,

            "memory_created":
                bool(memory_created),

            "memory_updated":
                bool(memory_updated),

            "remaining_messages":
                get_remaining_messages(request),
        }

        # -------------------------------------------------
        # CREATED MEMORY
        # -------------------------------------------------

        if memory_created:

            response_data["memory"] = (
                serialize_memory(
                    memory_created
                )
            )

        # -------------------------------------------------
        # UPDATED MEMORY
        # -------------------------------------------------

        if memory_updated:

            response_data["updated_memory"] = (
                serialize_memory(
                    memory_updated
                )
            )

        return JsonResponse(
            response_data,
            status=201,
        )

    except Conversation.DoesNotExist:

        return JsonResponse(
            {
                "success": False,
                "error": "Conversation not found",
            },
            status=404,
        )

    except Exception as e:

        traceback.print_exc()

        return JsonResponse(
            {
                "success": False,
                "error": str(e),
            },
            status=400,
        )

    finally:

        if temp_path:

            try:
                os.remove(temp_path)

            except OSError:
                pass
            
# =========================================================
# CHAT PAGE
# =========================================================

def chat_page(request):
    return render(
        request,
        "brain/chat.html"
    )


def login_page(request):
    return render(
        request,
        "brain/login.html"
    )
    
def account_page(request):
    return render(request, "brain/account.html")