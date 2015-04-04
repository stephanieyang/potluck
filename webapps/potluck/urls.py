from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    url(r'^$', 'potluck.views.home'),
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name':'login.html'}, name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout_then_login', name='logout'),
    url(r'^register/$', 'potluck.views.register', name='register'),
    url(r'^buy/$', 'potluck.views.buy', name='buy'),
    url(r'^sell/$', 'potluck.views.sell', name='sell'),
    url(r'^search/$', 'potluck.views.search', name='search'),
    url(r'^profile/(?P<id>\d+)/$', 'potluck.views.profile', name='profile'),
    url(r'^edit_profile/$', 'potluck.views.edit_profile', name='edit_profile'),
    url(r'^edit_sale/$', 'potluck.views.edit_sale', name='edit_sale'),
    url(r'^slash_price/(?P<id>\d+)/(?P<amt>\d+)$', 'potluck.views.slash_price', name='slash_price'),
    url(r'^avatar/(?P<id>\d+)$', 'potluck.views.get_avatar', name='avatar'),
    url(r'^picture/(?P<id>\d+)$', 'potluck.views.get_picture', name='picture'),
    url(r'^forgotpassword/$', 'potluck.views.forgotpassword', name='forgot'),
    url(r'^resetpassword/$', 'potluck.views.resetpassword', name='reset'),
    url(r'^resetpassword-confirm/(?P<username>[a-zA-Z0-9_@\+\-]+)/(?P<token>[a-z0-9\-]+)$', 'potluck.views.resetpassword_confirm', name='reset-confirm'),
    url(r'^resetpassword-check/(?P<username>[a-zA-Z0-9_@\+\-]+)$', 'potluck.views.resetpassword_check', name='reset-check'),
    url(r'^confirm-registration/(?P<username>[a-zA-Z0-9_@\+\-]+)/(?P<token>[a-z0-9\-]+)$', 'potluck.views.confirm_registration', name='confirm'),
)
