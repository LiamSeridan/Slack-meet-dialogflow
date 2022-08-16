from django.urls import include, path
from . import views
urlpatterns = [
    path('message_options/', views.message_options, name='message_options'),
    path('message_actions/', views.message_actions, name='message_actions'),
]