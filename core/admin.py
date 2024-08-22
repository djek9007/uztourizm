from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm
from .models import CustomUser, City, Payment, Ticket, Configuration, Role


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_staff', 'list_cities',)
    search_fields = ('username', 'email')

    def get_form(self, request, obj=None, **kwargs):
        # Указываем форму для использования
        kwargs['form'] = CustomUserCreationForm
        form = super().get_form(request, obj, **kwargs)
        form.current_user = request.user  # Передаем текущего пользователя в форму
        return form

    def save_model(self, request, obj, form, change):
        # При создании пользователя обычным администратором автоматически назначаем город
        if not obj.pk and not request.user.is_superuser:
            obj.city = request.user.city
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        # Ограничиваем видимость пользователей для администратора его городом
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(city=request.user.city)


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Payment)
admin.site.register(Ticket)

@admin.register(Configuration)
class ConfigurationAdmin(admin.ModelAdmin):
    list_display = ('enable_payment_system', 'enable_test_mode', 'created_date', 'edit_date',)
    fields = ('enable_payment_system', 'enable_test_mode')

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_date', 'edit_date','published',)
    fields = ('name','published','slug',)
    prepopulated_fields = {"slug": ["name"]}

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_date', 'edit_date',)
    fields = ('name','description',)
