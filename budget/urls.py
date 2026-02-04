from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('add-income/', views.add_income, name='add_income'),
    path('add-expense/', views.add_expense, name='add_expense'),
    path('add-category/', views.add_category, name='add_category'),

    path('update-income/<int:pk>/', views.update_income, name='update_income'),
    path('update-expense/<int:pk>/', views.update_expense, name='update_expense'),
    path('update-category/<int:pk>/', views.update_category, name='update_category'),

    path('delete-income/<int:pk>/', views.delete_income, name='delete_income'),
    path('delete-expense/<int:pk>/', views.delete_expense, name='delete_expense'),
    path('delete-category/<int:pk>/', views.delete_category, name='delete_category'),

]
