from allauth.account.views import LoginView
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext_lazy as _


class AdminLoginView(LoginView):
    template_name = "admin/staff_login.html"

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "title": _("Log in"),
            "has_permission": False,
        }


@login_required
def continue_after_setup(request):
    destination = request.session.pop("staff_mfa_next", "")
    if not url_has_allowed_host_and_scheme(
        destination,
        {request.get_host()},
        require_https=request.is_secure(),
    ):
        destination = reverse("admin:index")
    return HttpResponseRedirect(destination)
