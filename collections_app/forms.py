from django import forms
from django.forms import inlineformset_factory

from .models import Collection, CollectionItem


class CollectionForm(forms.ModelForm):
    class Meta:
        model = Collection
        fields = ["title", "slug"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Например: Находки для кухни"}),
            "slug": forms.TextInput(attrs={"placeholder": "kitchen1"}),
        }
        help_texts = {
            "slug": "Только латинские буквы, цифры и дефис. После создания изменить нельзя.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["slug"].disabled = True


class CollectionItemForm(forms.ModelForm):
    class Meta:
        model = CollectionItem
        fields = ["title", "url"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Название товара (видно только вам)"}),
            "url": forms.URLInput(attrs={"placeholder": "https://ali.click/..."}),
        }


ItemFormSet = inlineformset_factory(
    Collection,
    CollectionItem,
    form=CollectionItemForm,
    extra=0,
    min_num=1,
    validate_min=True,
    can_delete=True,
)
