from django import forms
from .models import CustomUser

class CustomUserCreationForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'city', 'roles']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Если пользователь не суперпользователь, блокируем редактирование поля города
        if not self.current_user.is_superuser:
            self.fields['city'].disabled = True

    def save(self, commit=True):
        # Если город заблокирован, но пользователь создается впервые, задаем его значение
        user = super().save(commit=False)
        if not self.current_user.is_superuser and not user.pk:
            user.city = self.current_user.city
        if commit:
            user.save()
        return user
