from django.urls import path
from .views import chatbot_view
from .views import chatbot_view, rne_info, contact_view
urlpatterns = [
    path('', chatbot_view, name='chatbot'),
    path('rne-info/', rne_info, name='rne_info'),
    path('contact/', contact_view, name='contact'),
]
