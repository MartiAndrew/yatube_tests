from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()


class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')
        labels = {
            'first_name': 'Имя:',
            'last_name': 'Фамилия:',
            'username': 'Никнэйм:',
            'email': 'Адрес e-mail:',
        }
        help_texts = {
            'first_name': 'Ваше имя',
            'last_name': 'Ваша фамилия',
            'username': 'Ваш никнэйм',
            'email': 'Ваш адрес email: user@usermail.com',
        }
