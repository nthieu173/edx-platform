""" Password related views """

import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_http_methods

from edx_ace import ace
from edx_ace.recipient import Recipient
from openedx.core.djangoapps.ace_common.template_context import get_base_template_context
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
from openedx.core.djangoapps.theming.helpers import get_current_site
from openedx.core.djangoapps.user_api.accounts.api import request_password_change
from openedx.core.djangoapps.user_api.errors import (
    UserNotFound,
    UserAPIInternalError
)
from student.helpers import destroy_oauth_tokens
from student.message_types import PasswordReset
from util.bad_request_rate_limiter import BadRequestRateLimiter


AUDIT_LOG = logging.getLogger("audit")
log = logging.getLogger(__name__)
User = get_user_model()  # pylint:disable=invalid-name


@require_http_methods(['POST'])
def password_change_request_handler(request):
    """Handle password change requests originating from the account page.

    Uses the Account API to email the user a link to the password reset page.

    Note:
        The next step in the password reset process (confirmation) is currently handled
        by student.views.password_reset_confirm_wrapper, a custom wrapper around Django's
        password reset confirmation view.

    Args:
        request (HttpRequest)

    Returns:
        HttpResponse: 200 if the email was sent successfully
        HttpResponse: 400 if there is no 'email' POST parameter
        HttpResponse: 403 if the client has been rate limited
        HttpResponse: 405 if using an unsupported HTTP method

    Example usage:

        POST /account/password

    """

    limiter = BadRequestRateLimiter()
    if limiter.is_rate_limit_exceeded(request):
        AUDIT_LOG.warning("Password reset rate limit exceeded")
        return HttpResponseForbidden()

    user = request.user
    # Prefer logged-in user's email
    email = user.email if user.is_authenticated else request.POST.get('email')

    if email:
        try:
            request_password_change(email, request.is_secure())
            user = user if user.is_authenticated else User.objects.get(email=email)
            destroy_oauth_tokens(user)
        except UserNotFound:
            AUDIT_LOG.info("Invalid password reset attempt")
            # Increment the rate limit counter
            limiter.tick_bad_request_counter(request)

            # If enabled, send an email saying that a password reset was attempted, but that there is
            # no user associated with the email
            if configuration_helpers.get_value('ENABLE_PASSWORD_RESET_FAILURE_EMAIL',
                                               settings.FEATURES['ENABLE_PASSWORD_RESET_FAILURE_EMAIL']):

                site = get_current_site()
                message_context = get_base_template_context(site)

                message_context.update({
                    'failed': True,
                    'request': request,  # Used by google_analytics_tracking_pixel
                    'email_address': email,
                })

                msg = PasswordReset().personalize(
                    recipient=Recipient(username='', email_address=email),
                    language=settings.LANGUAGE_CODE,
                    user_context=message_context,
                )

                ace.send(msg)
        except UserAPIInternalError as err:
            log.exception('Error occured during password change for user {email}: {error}'
                          .format(email=email, error=err))
            return HttpResponse(_("Some error occured during password change. Please try again"), status=500)

        return HttpResponse(status=200)
    else:
        return HttpResponseBadRequest(_("No email address provided."))
