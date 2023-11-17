from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

hex_color_validator = RegexValidator(
    regex='^#([A-Fa-f0-9]{3,6})$',
    message='Введите корректный hex-код цвета',
    code='invalid_hex_color',
)


validator = RegexValidator(
    regex=r"^[a-zA-Z0-9]{4,16}$",
    message=(
        "Имя пользователя должно состоять из буквенно-цифровых символов, "
        'а также знаков ".", "@", "+", "-" и не содержать других символов.'
    ),
)

def validate_username(value):
    if value.lower() == 'me':
        raise ValidationError(
            ('Имя пользователя не может быть <me>.'),
            params={'value': value},
        )