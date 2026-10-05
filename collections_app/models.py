from django.core.validators import RegexValidator, URLValidator
from django.db import models

slug_validator = RegexValidator(
    regex=r"^[A-Za-z0-9-]+$",
    message="Только латинские буквы, цифры и дефис.",
)


class Collection(models.Model):
    title = models.CharField("Название", max_length=200)
    slug = models.CharField(
        "ID для адреса",
        max_length=64,
        unique=True,
        validators=[slug_validator],
    )
    created_at = models.DateTimeField("Создана", auto_now_add=True)
    updated_at = models.DateTimeField("Изменена", auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Подборка"
        verbose_name_plural = "Подборки"

    def __str__(self):
        return self.title


class CollectionItem(models.Model):
    collection = models.ForeignKey(
        Collection,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Подборка",
    )
    title = models.CharField("Название (для админки)", max_length=200)
    url = models.URLField(
        "Ссылка",
        max_length=2000,
        validators=[URLValidator(schemes=["http", "https"])],
    )
    position = models.PositiveIntegerField("Позиция", default=0)

    class Meta:
        ordering = ["position", "id"]
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        return self.title
