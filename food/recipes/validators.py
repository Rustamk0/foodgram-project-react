from django.core.validators import RegexValidator
from django.contrib.auth.validators import UnicodeUsernameValidator

uni_validator = UnicodeUsernameValidator()

hex_color_validator = RegexValidator(
    regex='^#([A-Fa-f0-9]{3,6})$',
    message='Введите корректный hex-код цвета',
    code='invalid_hex_color',
)


ingrent_validator = RegexValidator(
    regex=r"^[$%^&#:;!]",
    message=(
        "Имя пользователя должно состоять из буквенно-цифровых символов, "
        'не содержать симолов "&", "%", "$", "#",":", ";","!"'
    ),
)

