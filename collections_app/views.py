from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CollectionForm, ItemFormSet
from .models import Collection


@login_required
def collection_list(request):
    collections = Collection.objects.annotate(items_count=Count("items"))
    return render(request, "manage/collection_list.html", {"collections": collections})


@login_required
def collection_edit(request, pk=None):
    collection = get_object_or_404(Collection, pk=pk) if pk else None

    if request.method == "POST":
        form = CollectionForm(request.POST, instance=collection)
        formset = ItemFormSet(request.POST, instance=form.instance)
        form_ok = form.is_valid()
        formset_ok = formset.is_valid()
        if form_ok and formset_ok:
            with transaction.atomic():
                saved = form.save()
                position = 0
                for item_form in formset.forms:
                    if item_form.cleaned_data.get("DELETE"):
                        if item_form.instance.pk:
                            item_form.instance.delete()
                        continue
                    if not item_form.cleaned_data:
                        continue
                    item = item_form.save(commit=False)
                    item.collection = saved
                    item.position = position
                    item.save()
                    position += 1
            messages.success(request, "Подборка сохранена.")
            return redirect("manage:collection_edit", pk=saved.pk)
    else:
        form = CollectionForm(instance=collection)
        formset = ItemFormSet(instance=form.instance)

    return render(
        request,
        "manage/collection_form.html",
        {"form": form, "formset": formset, "collection": collection},
    )


@login_required
def collection_delete(request, pk):
    collection = get_object_or_404(Collection, pk=pk)
    if request.method == "POST":
        collection.delete()
        messages.success(request, "Подборка удалена.")
        return redirect("manage:collection_list")
    return render(request, "manage/collection_confirm_delete.html", {"collection": collection})

def public_collection(request, slug):
    collection = get_object_or_404(Collection, slug=slug)
    items = list(collection.items.all())
    return render(
        request,
        "public/collection.html",
        {"collection": collection, "items": items},
    )
