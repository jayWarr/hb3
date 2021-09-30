import os
import platform
import random
import socket
import string
import urllib
import webbrowser
from datetime import date, datetime
from urllib.parse import quote, urljoin

import django
from cuser.middleware import CuserMiddleware
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.core.exceptions import ValidationError
from django.forms import URLField
from filehash import FileHash
from maintenance.models import Profile, SystemParameters
import hashlib
import uuid

def isNotDemoUser(request, model=None, name=None):
    # ---- enable to allow demo user to create records
    return True
    # ------------------------------------------------
    if request.session['is Demo User'] and model != None and name != None:
        if type(name) == 'string' and name.startswith('[') and name.endswith(']'):  # attempted action
            scriptMessages(request,
                           u"Error: The action  %s  on %ss has not been undertaken!\nError: As a demo user you cannot action ANY change!" % (
                           name, model))
        else:
            scriptMessages(request,
                           u"Error: The %s  '%s'  is UNCHANGED and/or NOT SAVED !\nError: As a demo user you cannot change or save ANY information !" % (
                           model, name))
    return not request.session['is Demo User']


def terminateUserSessionsandForceLockOut(user):
    # delete multiple session objects
    [s.delete() for s in Session.objects.all() if s.get_decoded().get('_auth_user_id') == user.id]
    # lock them out
    user.is_active = False
    user.save()


def IntPlusIntPositive(i1, i2):
    return bool((i1 + i2) > 0)



def get_UserProfileIntoSessionValues(request):
    theUser = request.user
    theUser_id = theUser.id
    request.session['User_id'] = theUser_id
    request.session['User_name'] = theUser.username
    if theUser_id == settings.THE_DEMO_ID:
        request.session['is_Demo_user'] = True
    else:
        request.session['is_Demo_user'] = False
    if theUser_id == settings.THE_ADMIN_ID:
        request.session['is_Admin'] = True
    else:
        request.session['is_Admin'] = False

    try:
        up = Profile.objects.get(user=theUser_id)
        request.session['First_time_flag'] = up.ftfg
        request.session['Wait_period_for_competitions_entries'] = up.wd4c
        request.session['Wait_period_for_submissions'] = up.wd4s
        request.session['Wait_period_for_publishers_response'] = up.wd4p
        request.session['Advanced_days_warning_of_competition_closure'] = up.dacw
        request.session['Default_multiple_use'] = up.dfmu
        if up.hklr is None:
            request.session['Last_HK_run_on'] = None
        else:
            request.session['Last_HK_run_on'] = up.hklr.isoformat()
        request.session['Default_update_tag'] = up.dutg
        request.session['Assigned_batch_tag'] = up.abtg
        request.session['Default_poetic_form'] = str(up.dfpf_id)
        request.session['Handle_titles'] = up.enct
        request.session['Last_upload_details'] = up.ludt
        request.session['poem listing display'] = up.pldo
        request.session['Current_WIP_poem'] = str(up.wipp_id)
        if up.wipp_id is None:
            request.session['has_Current_WIP_poem'] = False
        else:
            request.session['has_Current_WIP_poem'] = True
        request.session['Country_preference'] = up.cnty
        request.session['Show competitions closing in country'] = up.scty
        request.session['Require bug fix reports'] = up.rbfr
        request.session['logo'] = up.logo
        request.session['logo choice'] = up.lgch
        request.session['highlight poem'] = up.hpom
        request.session['highlight note'] = up.hnot
        request.session['highlight competitions'] = up.hcmp
        request.session['highlight submissions'] = up.hsub
        request.session['highlight publishers'] = up.hpub
        request.session['Verbose system messages'] = up.vsmg
        # get hummingbird version details
        sp = SystemParameters.objects.get(id=1)
        yyyyymmdd = sp.vndt
        yymmmdd = yyyyymmdd.strftime('%d%b%y')
        request.session['Version_details'] = u"candidate: %s   version: %s     released: %s" % (
        sp.vncd, sp.vnno, yymmmdd)
        # get python, django & baton details
        bu = 'Built using'
        bu += ' Python_v' + platform.python_version()
        bu += ', Django_v' + django.get_version()
        bu += ' & Baton_v' + settings.BATON_VERSION
        request.session['Python_Django_Baton_versions'] = bu
        return
    except Profile.DoesNotExist:
        #	terminate session
        print('******************************************')
        print('*         Terminating session            *')
        print('******************************************')
        terminateUserSessionsandForceLockOut(theUser)


def set_UserProfileFromSessionValues(request):
    theUser = request.user
    theUser_id = theUser.id
    up = Profile.objects.get(user=theUser_id)
    up.ftfg = request.session['First_time_flag']
    up.wd4c = request.session['Wait_period_for_competitions_entries']
    up.wd4s = request.session['Wait_period_for_submissions']
    up.wd4p = request.session['Wait_period_for_publishers_response']
    up.dacw = request.session['Advanced_days_warning_of_competition_closure']
    up.dfmu = request.session['Default_multiple_use']
    up.hklr = datetime.strptime(request.session['Last_HK_run_on'], '%Y-%m-%d').date()
    up.dutg = request.session['Default_update_tag']
    up.abtg = request.session['Assigned_batch_tag']
    up.dfpf_id = int(request.session['Default_poetic_form'])
    up.enct = request.session['Handle_titles']
    up.ludt = request.session['Last_upload_details']
    try:
        up.wipp_id = int(request.session['Current_WIP_poem'])
    except:
        up.wipp_id = None
    up.cnty = request.session['Country_preference']
    up.scty = request.session['Show competitions closing in country']
    up.rbfr = request.session['Require bug fix reports']
    up.pldo = request.session['poem listing display']
    up.logo = request.session['logo']
    up.lgch = request.session['logo choice']
    up.hpom = request.session['highlight poem']
    up.hnot = request.session['highlight note']
    up.hcmp = request.session['highlight competitions']
    up.hsub = request.session['highlight submissions']
    up.hpub = request.session['highlight publishers']
    up.vsmg = request.session['Verbose system messages']
    up.save()
    return


def successMsg(request, model, name):
    if request.session['Verbose system messages']: scriptMessages(request, u"Success: The %s: %s has been successfully changed/saved" % (model, name))
    return


def isDemoUserAttemptingCCSA(request, model, action):
    #
    # if this is the Demo user attempting to:
    # Create,Change,Save or Action then issue
    # an Error message
    #
    if request.session['is_Demo_user'] is True:
        msg = "Error: As a DEMO user you are not permitted to "
        if action.startswith('[') and action.endswith(']'):  # attempted an action
            msg += u"perform the action %s on %ss." % (action, model)
        else:
            msg += u"%s a %s" % (action, model)
        scriptMessages(request, msg)
    return request.session['is_Demo_user']


def terminateUserSessionsandForceLockOut(user):
    # delete multiple session objects
    [s.delete() for s in Session.objects.all() if s.get_decoded().get('_auth_user_id') == user.id]
    # lock them out
    user.is_active = False
    user.save()


def make_url(base_url, *res, **params):
    url = base_url
    for r in res:
        url = '{}/{}'.format(url, r)
    if params:
        url = '{}?{}'.format(url, urllib.urlencode(params))
    return url


def dateTimeNow():
    return datetime.now().strftime("on %Y-%b-%d at %H:%M")


def pid_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def validate_url(url):
    url_form_field = URLField()
    try:
        url = url_form_field.clean(url)
    except ValidationError:
        return False
    return True


def scriptMessages(request, msg):
    if msg != '':
        lines = msg.splitlines()
        for line in lines:
            tl = line.strip()
            if tl != '': issueMessage(request, tl)
    return


def issueMessage(request, msg):
    if msg[:6] == "Error:" or msg[:6] == "Alert:":
        messages.error(request, msg[7:])
    elif msg[:8] == "Warning:":
        messages.warning(request, msg[9:])
    elif msg[:5] == "Info:":
        messages.info(request, msg[6:])
    elif msg[:8] == "Success:":
        messages.success(request, msg[9:])
    elif msg[:6] == "Debug:":
        messages.debug(request, msg[7:])
    elif msg != "":
        # NB without header string all messages default to info
        messages.info(request, msg)
    return


def pluralize(n):
    if n == 1:
        return ''
    else:
        return 's'


def is_are(n):
    if n > 1:
        return 'are'
    else:
        return 'is'


def has_have(n):
    if n == 1:
        return 'has'
    else:
        return 'have'

def y_ies(n):
    if n==1:
        return 'y'
    else:
        return 'ies'


def get_hostNameAndIP():
    try:
        host_name = socket.gethostname()
        host_ip = socket.gethostbyname(host_name)
        return [host_name, host_ip]
    except:
        return ['', '']


def open_Link(self, request, queryset, message_bit):
    NoOf = len(queryset)
    if NoOf != 1:
        theMessage = u'Error: You may only open 1 %s at a time!' % (message_bit)
        issueMessage(request, theMessage)
    else:
        for qs in queryset:
            theURL = qs.url
            open_URL(theURL)
    return


def open_URL(theURL):
    # if missing http(s):// prefix with file://
    if theURL[:6] != 'http://' and theURL[:7] != 'https://' and theURL[0] == '/': theURL = quote(
        urljoin('file://', theURL))
    try:
        webbrowser.open_new_tab(theURL)
    except webbrowser.Error:
        raise webbrowser.Error
    return


def get_Version(select):
    # also gets & displays user PID
    sp = SystemParameters.objects.get(id=1)
    versionNo = sp.vnno
    versionDT = sp.vndt
    versionCD = sp.vncd
    if select == 1:
        vd = u'version: %s' % versionNo
    elif select == 2:
        vd = u'released: %s' % versionDT
    elif select == 3:
        vd = u'Candidate: %s' % versionCD
    else:
        # PID=getUserPID()
        vd = u' candidate: %s   version: %s released: %s' % (versionCD, versionNo, versionDT)
    return vd


def getUserPID():
    # extract 6 chars from 3rd $ delimited component of password
    # can be used to encrypt uploads
    theUser = CuserMiddleware.get_user()
    if theUser == None: return ''
    theUser_id = theUser.id
    u = User.objects.get(id=theUser_id)
    encryptedPassword = u.password
    ep = encryptedPassword.split('$')
    return ep[3][:6]


def MaintenanceDetails(select):
    sp = SystemParameters.objects.get(id=1)
    switchedOff = sp.mmso
    switchON = sp.mmer
    if sp.mmpd == 'M':
        thePeriod = 'minute'
    elif sp.mmpd == 'H':
        thePeriod = 'hour'
    elif sp.mmpd == 'D':
        thePeriod = 'day'
    else:
        thePeriod = 'week'
    period = u'%s %s%s' % (sp.mmno, thePeriod, pluralize(sp.mmno))
    msg1 = u"hummingBird was switched off on %s for %s" % (switchedOff.strftime(settings.FORMAT_DATETIME), period)
    msg2 = u'The website will be operational on or before %s' % switchON.strftime(settings.FORMAT_DATETIME)
    msg3 = u'Reason: %s' % sp.mmmg
    if select == 1:
        return msg1
    elif select == 2:
        return msg2
    elif select == 3:
        return msg3
    else:
        return u'%s \n %s \n %s' % (msg1, msg2, msg3)

def validateAndReadTamperProofFile(theFile,uploadFilePath=None):
# last updated 29-Aug- 21
# validates tamper proof upload file
# (location defaults to desktop)
# by reading & removing the file hash suffix
# substituting the filename re-writing the file
# computing the file hash, comparing
# & if OK returning a list of file lines
# & if NOT OK returning an empty list of lines
#
# This is the complement to the routine:
# writeTamperProofUploadFile
# in _utilities_.getPoemTitles_v6.py
#
    theLines=[]
    try:
        # get desktop file path
        if uploadFilePath==None:
            uploadFilePath = os.path.join(os.path.normpath(os.path.expanduser("~" + os.path.sep + "Desktop")), theFile)
        # read lines of file
        with open(uploadFilePath, "r") as uf:
            theLines=uf.readlines()
        # extract filehash
        filehash=theLines[-1]
        # subsitute filename
        theLines[-1]=theFile
        # re-write the file
        with open(uploadFilePath, "w") as uf:
            uf.write(''.join(theLines))
        # compute sha256 file hash
        sha256hasher = FileHash('sha256')
        computedfileHash = sha256hasher.hash_file(uploadFilePath)
        # compare hashs if EQ return lines without suffix
        if filehash == computedfileHash:
            del theLines[-1]
    except:
        pass # empty lines
    return theLines
