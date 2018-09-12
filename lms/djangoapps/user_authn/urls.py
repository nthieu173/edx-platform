""" URLs for User Authentication """
from django.conf import settings
from django.conf.urls import url

from openedx.core.djangoapps.user_api.accounts import settings_views as account_settings_views
from student import views as deprecated_views
from .views import login as login_views, password as password_views


urlpatterns = [
    url(r'^account/finish_auth$', login_views.finish_auth, name='finish_auth'),
    url(r'^account/password$', password_views.password_change_request_handler, name='password_change_request'),

    # this should really be declared in the user_api app
    url(r'^account/settings$', account_settings_views.account_settings, name='account_settings'),
]


if settings.FEATURES.get('ENABLE_COMBINED_LOGIN_REGISTRATION'):
    # Backwards compatibility with old URL structure, but serve the new views
    urlpatterns += [
        url(r'^login$', login_views.login_and_registration_form,
            {'initial_mode': 'login'}, name='signin_user'),
        url(r'^register$', login_views.login_and_registration_form,
            {'initial_mode': 'register'}, name='register_user'),
    ]
else:
    # Serve the old views
    urlpatterns += [
        url(r'^login$', deprecated_views.signin_user, name='signin_user'),
        url(r'^register$', deprecated_views.register_user, name='register_user'),
    ]
