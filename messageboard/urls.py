from django.urls import path
from .views import (
    message_board, moderator_view, approve_message, 
    delete_message, clear_messages, login_view, logout_view, 
    get_approved_messages, get_pending_messages, 
    approve_all, delete_all_pending, delete_all_published
)

urlpatterns = [
    path('', message_board, name='message_board'),
    path('moderator/', moderator_view, name='moderator_view'),
    path('approve/<int:message_id>/', approve_message, name='approve_message'),
    path('delete/<int:message_id>/', delete_message, name='delete_message'),
    path('clear_messages/', clear_messages, name='clear_messages'),

    # 🔹 API-reitit viestien hakemiselle
    path('get_approved_messages/', get_approved_messages, name='get_approved_messages'),
    path('get_pending_messages/', get_pending_messages, name='get_pending_messages'),

    # 🔹 API-reitit "Julkaise kaikki" ja "Poista kaikki julkaisemattomat" -toiminnoille
    path('approve_all/', approve_all, name='approve_all'),
    path('delete_all_pending/', delete_all_pending, name='delete_all_pending'),
    path('delete_all_published/', delete_all_published, name='delete_all_published'),

    # 🔹 Kirjautuminen ja uloskirjautuminen
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
]

