import webbrowser
from datetime import datetime

from django.core.exceptions import ValidationError

from core.choices import PREFIXES
from core.generalSupportRoutines import (isDemoUserAttemptingCCSA,
                                         isNotDemoUser, issueMessage,
                                         pluralize)


def isInEligible(thePoem):  # needs request
    ineligible = False
    # get current state of poem
    currentEntries = thePoem.nE2C
    currentNoSubmissions = thePoem.nS2M
    currentNoSPublications = thePoem.niP
    # get single use flag
    singleUse = not thePoem.mu
    if singleUse and (currentEntries > 0 or currentNoSubmissions > 0 or currentNoSPublications > 0):
        useIn = ''
        if currentEntries > 0: useIn += "competition entry "
        if currentNoSubmissions > 0: useIn += "magazine submission "
        if currentNoSPublications > 0: useIn += "publication content "
        raise ValidationError({'competition entry': ValidationError(
            u"This poem is already in use for a %s and multiple use is not permitted !" % useIn,
            code='invalid'), })
        ineligible = True
    return ineligible


def naturalisePoemTitle(text):
    text1 = text.strip().lower()
    words = text1.split(' ')
    word0 = words[0]
    for pfx in PREFIXES:
        pfxP, pfxS = pfx
        if word0 == pfxP:
            del words[0]
            return ' '.join(words) + pfxS
    return text


def isTitleNaturalised(text):
    words = text.split(' ')
    if len(words) > 1:
        lastWord = words[-1]
        for pfx in PREFIXES:
            pfxP, pfxS = pfx
            if pfxP == lastWord:
                if words[-2].endswith(','):
                    return True
    return False


def unNatrualise(text):
    words = text.split(' ')
    if len(words) > 1:
        newFirsttWord = words[-1]
        del words[-1]
        LastWord = words[-1]
        del words[-1]
        newLastWord = LastWord[:-1]
        return newFirsttWord + ' ' + ' '.join(words) + ' ' + newLastWord
    else:
        return text


def reassignMu(self, request, queryset):
    if isNotDemoUser(request, 'poem', '[reassign multiple use]'):
        newDfmu = request.session['Default_multiple_use']
        if newDfmu:
            assignment = "multiple"
        else:
            assignment = 'single'
        nPoems = len(queryset)
        for qs in queryset:
            qs.mu = newDfmu
            qs.save()
        if request.session['Verbose system messages']:
            message_bit = u'Info: %s poem%s assigned %s use' % (nPoems, pluralize(nPoems), assignment)
            issueMessage(request, message_bit)
    return


reassignMu.short_description = "Re-assign the use"


def fixDtlu(self, request, queryset):
    nowIsh = datetime.now()
    for qs in queryset:
        if qs.dtlu is None:
            qs.dtlu = nowIsh
            qs.save()
    return


fixDtlu.short_description = "fix Dtlu"


def fixTitles(self, request, queryset):
    if isNotDemoUser(request, 'poem', '[fix titles]'):
        handleTitle = request.session['Handle_titles']
        fix = ['doing nothing', 'capitalizing the first letter', 'making all lowercase', 'naturalising']
        noFixes = 0
        for qs in queryset:
            theTitle = qs.title
            isNaturalised = isTitleNaturalised(theTitle)
            if isNaturalised:
                unp = unNatrualise(theTitle)
            else:
                ntp = naturalisePoemTitle(theTitle)
            if handleTitle == 3:  # naturalise
                if not isNaturalised:
                    qs.title = ntp
                    qs.save()
                    noFixes += 1
                else:
                    pass
            elif handleTitle == 2:  # all lowercase
                if isNaturalised:
                    theNewTitle = unp.lower()
                else:
                    theNewTitle = theTitle.lower()
                qs.title = theNewTitle
                qs.save()
                noFixes += 1
            elif handleTitle == 1:  # capitalize 1st letter
                if isNaturalised:
                    theNewTitle = unp
                else:
                    theNewTitle = theTitle
                qs.title = theNewTitle.capitalize()
                qs.save()
                noFixes += 1
            elif handleTitle == 0:  # do nothing
                if isNaturalised:
                    theNewTitle = unp
                    qs.title = theNewTitle
                    qs.save()
                    noFixes += 1
        message_bit = u'Info: Fixed %s title%s by %s' % (noFixes, pluralize(noFixes), fix[handleTitle])
        if request.session['Verbose system messages']: issueMessage(request, message_bit)
    return


fixTitles.short_description = "Fix titles"


def openSourceDocument(self, request, queryset):
    if len(queryset) > 1:
        message_bit = u'Cannot open more than 1 source document at a time. Please re-select a single poem'
        issueMessage(request, message_bit)
    else:
        sd = queryset[0].sd
        try:
            webbrowser.open_new_tab(sd)  # will open http(s): & file:
        except webbrowser.error as wbe:
            message_bit = u'Error: %s attempting to open source document reference: %s' % (wbe, sd)
            issueMessage(request, message_bit)
    return


openSourceDocument.short_description = "Open a source document"


def reverseWIP_poem(self, request, queryset):
    if isDemoUserAttemptingCCSA(request, 'poem', '[reverse wip settings]'): return
    np = len(queryset)
    for qs in queryset:
        qs.wip = not qs.wip
        qs.save()
    message_bit = u'Info: Reversed the WIP setting%s for %s poem%s ' % (pluralize(np), np, pluralize(np))
    if request.session['Verbose system messages']: issueMessage(request, message_bit)
    return


reverseWIP_poem.short_description = "Reverse the WIP settings"


def reassignForm(self, request, queryset):
    if isDemoUserAttemptingCCSA(request, 'poem', '[reassign form]'): return
    # get default form id from
    newForm_id = int(request.session['Default_poetic_form'])
    np = len(queryset)
    for qs in queryset:
        qs.form_id = newForm_id
        qs.save()
    message_bit = u'Info: Reassigned the poetic form%s of %s poem%s' % (pluralize(np), np, pluralize(np))
    if request.session['Verbose system messages']: issueMessage(request, message_bit)
    return


reassignForm.short_description = "Re-assign form"


def fixTag(self, request, queryset):
    if isDemoUserAttemptingCCSA(request, 'poem', '[Fix tag]'): return
    assignedBatchTag = request.session['Assigned_batch_tag']
    np = queryset.count()
    for qs in queryset:
        qs.tag = assignedBatchTag
        qs.save()
    if request.session['Verbose system messages']:
        message_bit = u"Info: Changed %s tag%s to the assigned batch tag [%s] for the selected poem%s" % (
                        np, pluralize(np), assignedBatchTag, pluralize(np))
        issueMessage(request, message_bit)
    return


fixTag.short_description = "Fix tag"


def withdrawEntries(self, request, queryset):
    if isDemoUserAttemptingCCSA(request, 'poem', '[Withdraw entries]'): return
    # withdraw the poems by expiring them today
    np = len(queryset)
    np0 = 0
    for theEntry in queryset:
        # don't expire an entry already expired
        if theEntry.expiredOn is None:
            np0 += 1
            # expire the entry
            theEntry.withdrawEntry()
    if np0 == 1:
        ent = 'Entry'
    else:
        ent = 'Entries'
    message_bit = u"Info: %s %s withdrawn" % (np0, ent)
    if np0 != np:
        message_bit += u'. Requested %s to be withdrawn, %s had already been' % (np, np - np0)
    if request.session['Verbose system messages']: issueMessage(request, message_bit)


withdrawEntries.short_description = "Withdraw entries"


def withdrawSubmissions(self, request, queryset):
    if isDemoUserAttemptingCCSA(request, 'poem', '[Withdraw submissions]'): return
    np = len(queryset)
    np0 = 0
    for theSubmsn in queryset:
        # don't expire an submission already expired
        if theSubmsn.expiredOn is None:
            np0 += 1
            # expire the submission
            theSubmsn.withdrawSubmission()
    message_bit = u"Info: %s submission%s withdrawn" % (np0, pluralize(np0))
    if np0 != np:
        message_bit += u'. Requested %s to be withdrawn, %s had already been' % (np, np - np0)
    if request.session['Verbose system messages']: issueMessage(request, message_bit)


withdrawSubmissions.short_description = "Withdraw submissions"
