from django.urls import path
from oauth2_provider import views
from oauth2_provider.urls import dcr_urlpatterns
from oauth2_provider.urls import management_urlpatterns

from space_game.control.oauth import StaffAuthorizationView

app_name = "oauth2_provider"
urlpatterns = [
    path("authorize/", StaffAuthorizationView.as_view(), name="authorize"),
    path("token/", views.TokenView.as_view(), name="token"),
    path("revoke_token/", views.RevokeTokenView.as_view(), name="revoke-token"),
    *management_urlpatterns,
    *dcr_urlpatterns,
]
