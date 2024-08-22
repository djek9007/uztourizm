"""
URL configuration for museum project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include
from django.contrib.auth import views as auth_views
from core.views import AdminPanelView, CashierPanelView, CustomLoginView, ErrorPanelView, AddCashierView, home_redirect

urlpatterns = [

    path('admin/', admin.site.urls),
    # Маршрут для панели администратора
    path('admin-panel/', AdminPanelView.as_view(), name='admin_panel'),
    path('admin-panel/add-cashier/', AddCashierView.as_view(), name='add_cashier'),

    # Маршрут для панели кассира
    path('cashier-panel/', CashierPanelView.as_view(), name='cashier_panel'),

    #  Маршрут когда не назначили роль
    path('error-panel/', ErrorPanelView.as_view(), name='error_panel'),

    # Перенаправление на нужную страницу в зависимости от авторизации
    path('', home_redirect, name='home'),



    # Включение URL-маршрутов для аутентификации
    path('accounts/', include('django.contrib.auth.urls')),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),


]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)