from allauth.account.urls import urlpatterns as account_urls
from django.urls import include
from django.urls import path

urlpatterns = [
    *(pattern for pattern in account_urls if pattern.name != "account_login"),
    path("2fa/", include("allauth.mfa.urls")),
]
