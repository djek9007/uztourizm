from datetime import timedelta

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView
from django.shortcuts import redirect
from django.contrib.auth import views as auth_views

from core.forms import CustomUserCreationForm
from core.models import City, CustomUser, Role

def home_redirect(request):
    # Если пользователь авторизован, перенаправляем на соответствующую панель
    if request.user.is_authenticated:
        if request.user.roles.filter(name='Администратор').exists():
            return redirect('admin_panel')
        elif request.user.roles.filter(name='Кассир').exists():
            return redirect('cashier_panel')
        else:
            return redirect('error_panel')
    else:
        # Если пользователь не авторизован, перенаправляем на страницу логина
        return redirect('login')
class RoleRequiredMixin(UserPassesTestMixin):
    """
    Миксин для проверки роли пользователя.
    Позволяет контролировать доступ на основе ролей пользователя, таких как кассир или администратор.
    """
    required_role = None

    def test_func(self):
        # Проверяем, есть ли у пользователя требуемая роль
        if self.required_role:
            return self.request.user.roles.filter(name=self.required_role).exists()
        return False

    def handle_no_permission(self):
        # Перенаправляем на страницу входа, если пользователь не имеет доступа
        return redirect('login')


    def handle_no_permission(self):
        # Перенаправляем на страницу входа, если пользователь не имеет доступа
        return redirect('login')

# Представление для панели администратора
class AdminPanelView(LoginRequiredMixin, RoleRequiredMixin, TemplateView):
    template_name = "admin-panel.html"
    required_role = 'Администратор'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получаем города, которые привязаны к пользователю и опубликованы
        context['cities'] = self.request.user.city.filter(published=True)
        # Проверяем, является ли пользователь администратором
        context['is_admin'] = self.request.user.roles.filter(name='Администратор').exists()
        return context

class AddCashierView(LoginRequiredMixin, CreateView):
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'add_cashier.html'
    success_url = reverse_lazy('admin_panel')  # Перенаправление после успешного добавления

    def form_valid(self, form):
        # Устанавливаем город и роль кассира автоматически
        user = form.save(commit=False)
        user.city = self.request.user.city
        user.save()
        # Добавляем кассиру роль "Кассир"
        cashier_role = Role.objects.get(name='Кассир')
        user.roles.add(cashier_role)
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'current_user': self.request.user})
        return kwargs


# Представление для панели кассира
class CashierPanelView(LoginRequiredMixin, RoleRequiredMixin, TemplateView):
    # Указываем шаблон, который будет отображаться для кассира
    template_name = "kassir-panel.html"
    # Устанавливаем роль, требуемую для доступа
    required_role = 'cashier'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Здесь можно добавить дополнительные данные в контекст шаблона, если нужно
        return context

class ErrorPanelView(TemplateView):
    template_name = 'error-panel.html'

class CustomLoginView(auth_views.LoginView):
    def form_valid(self, form):
        response = super().form_valid(form)

        remember_me = self.request.POST.get('remember_me', False)
        if remember_me:
            self.request.session.set_expiry(timedelta(days=30))
        else:
            self.request.session.set_expiry(0)

        # Проверка ролей пользователя
        if self.request.user.roles.filter(name='Администратор').exists():
            return redirect('admin_panel')
        elif self.request.user.roles.filter(name='Кассир').exists():
            return redirect('cashier_panel')
        else:
            return redirect('error_panel')  # Перенаправление на другую страницу

        return response