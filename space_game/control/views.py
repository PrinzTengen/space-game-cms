from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme


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
