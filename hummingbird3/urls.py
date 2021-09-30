"""hummingbird3 URL Configuration

Last updated:
    16-Jan-21 added 1st time message to look at GDPR & ePR

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from urllib.error import URLError

import debug_toolbar
from baton.autodiscover import admin
from django.conf import settings
from django.conf.urls import include, url
from django.contrib.auth.signals import user_logged_in
from django.shortcuts import redirect
# from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView

from collection.models import Note, Poem
from core.generalSupportRoutines import (get_UserProfileIntoSessionValues,
                                         issueMessage, open_URL,
                                         scriptMessages,
                                         set_UserProfileFromSessionValues)
from core.utilitySupportRoutines import (get_Current_WIP_details, houseKeeping,
                                         initialiseCategories)
from hummingbird3.views import admin_search
from maintenance.models import Profile, SystemParameters

admin.site.site_url = None  # Removes the 'View Site' link

urlpatterns = [

    path('baton/', include('baton.urls')),
    path('accounts/', include('allauth.urls')),
    url(r'^favicon\.ico$', RedirectView.as_view(url='/static/images/favicon.ico')),
    path('admin/search/', admin_search),
    path('admin/contact', include('contactus.urls')),
    path('admin/doc/', include('django.contrib.admindocs.urls')),  # admin docs
    url(r'^error/', include('error_report.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    # redirect original admin/login to allauth accounts/login
    path('admin/login/',RedirectView.as_view(url='/accounts/login/', permanent=False)),
    url(r'^admin/$', RedirectView.as_view(url='/admin/collection/poem/', permanent=False)),
    path('admin/', admin.site.urls),
]

# for debug toolbar
if settings.DEBUG:
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

# ==========EXECUTED AFTER USER LOGIN =================================
def logged_in_message(sender, user, request, **kwargs):

# get user parameters into session veriables
    get_UserProfileIntoSessionValues(request)

#	Check for a system wide ADMIN message to everyone
    sp=SystemParameters.objects.get(id=1)
    if sp.aumg != '_NONE_':
        theMsg = sp.aumg
    else:
        theMsg=''

# check for demo user
    if request.session['is_Demo_user']:
        theMsg += u'As a Demo User you have limited workbench functionality. You can access any of the demonstration data; \n' \
                   'You can also list, view, report and practice changing any data - it will have no permanent effect.\n' \
                   'You are not permitted to delete data. You may revisit the workbench as a demo user at any time. \n' \
                   'If you wish to make use of the workbench as a regular user you should take the Sign Up option on the login page.'

# display message - if there is one
    if theMsg != '':
        scriptMessages(request, 'Info: ' + theMsg)

# get WIP details if present
    get_Current_WIP_details(request)

# if admin or demo user DON"T proceed
    if request.session['is_Demo_user'] or request.session['is_Admin']:
        return

# Check for the very first time login by a regular user - if so issue welcome message
    if request.session['First_time_flag']:
        scriptMessages(request, u"Info: %s, welcome to hummingBird poets' workbook!\nFor Information or Help at any time click on the I ot H icons below." % request.session['User_name'])
        # request new user display cookie consent modal overlay form
        issueMessage(request,'Error: IMPORTANT - PLEASE ACCESS AND READ THE MENU OPTIONS: RESOURCES -> GDPR & ePR notice')
        # turn off first time user flag
        request.session['First_time_flag']=False
        # save changed parameters
        set_UserProfileFromSessionValues(request)
        # initialise categories for user
        initialiseCategories(request.session['User_id'],request.session['User_name'])

# perform housekeeping - N.B. will only be done once per day at first logon
    houseKeeping(request)

    return

user_logged_in.connect(logged_in_message)

