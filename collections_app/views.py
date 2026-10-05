from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def collection_list(request):
    return render(request, "manage/collection_list.html")
