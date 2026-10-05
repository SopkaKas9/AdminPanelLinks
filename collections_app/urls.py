from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = "manage"

urlpatterns = [
    path("", views.collection_list, name="collection_list"),
    path("collections/new/", views.collection_edit, name="collection_create"),
    path("collections/<int:pk>/edit/", views.collection_edit, name="collection_edit"),
    path("collections/<int:pk>/delete/", views.collection_delete, name="collection_delete"),
    path(
        "login/",
        auth_views.LoginView.as_view(redirect_authenticated_user=True),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
