from django.urls import path
from . import views

urlpatterns = [
    path('', views.main),
    path('students/', views.students, name='students'),
    path('test-csrf/', views.test_csrf, name='test_csrf'),
    path("evaluate_answers/", views.evaluate_answers, name='evaluate_answers'),
]