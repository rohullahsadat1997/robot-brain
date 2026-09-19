from django.urls import path

from .views import (
    create_memory,
    list_memories,
    list_conversations,
    conversation_history,
    delete_conversation,
    chat,
    chat_page,
    login_page,
    voice_test,
    account_page,
)
from .auth_views import (
    register,
    register_page,
    login_view,
    logout_view,
    current_user,
    account_api,
)
urlpatterns = [
    path("", chat_page, name="chat_page"),
    path("memories/", list_memories, name="list_memories"),
    path("memories/create/", create_memory, name="create_memory"),
    path(
    "conversations/",
    list_conversations,
    name="list_conversations",
),
    
    path(
    "conversations/<int:conversation_id>/",
    conversation_history,
    name="conversation_history",
),
    path("chat/", chat, name="chat"),
    path("voice-test/", voice_test, name="voice_test"),
    
    path(
    "conversations/<int:conversation_id>/delete/",
    delete_conversation,
    name="delete_conversation",
),
    
    path("auth/register/", register, name="register"),
path("auth/login/", login_view, name="login"),
path("auth/logout/", logout_view, name="logout"),
path("auth/me/", current_user, name="current_user"),
path("login/", login_page, name="login_page"),
path("register/", register_page, name="register_page"),
path("account/", account_page, name="account_page"),
path("auth/account/", account_api, name="account_api"),
]