import collections
import operator
import os
import os.path
import tempfile
import zipfile
from datetime import datetime, timedelta, timezone
from urllib.parse import unquote, urlparse
from urllib.request import urlopen

from bs4 import BeautifulSoup
from collection.models import Category, Categorize, Note, Poem
from core.choices import (MAJOR_CATEGORIES, SUB_CATEGORIES, REMOVE_CATEGORY_PREFIX, ADD_CATEGORY_PREFIX,
						  RENAME_CATEGORY_PREFIX,
						  CATEGORIZED_TITLE_PREFIX, CATEGORY_DELIM, COMMENT_PREFIX)
from core.generalSupportRoutines import (get_UserProfileIntoSessionValues,
										 get_Version, has_have, is_are,
										 pluralize, scriptMessages,
										 set_UserProfileFromSessionValues,
										 validateAndReadTamperProofFile,
										 y_ies)
from datetime import datetime
from dateutil import parser
from django.conf import settings
from django.db.models import Count, Q
from entries.models import Competition, Entry
from maintenance.models import (Help, Profile, SystemParameters, Download, webResource)
from publishing.models import Publisher
from submissions.models import Magazine, Submission
from taggit.managers import TaggableManager
from json import dump as jsondump
from django.views.static import serve
from django.http.response import HttpResponse
import mimetypes


def get_Current_WIP_details(request):
	if request.session['has_Current_WIP_poem']:
		thePoem = Poem.objects.get(id=int(request.session['Current_WIP_poem']))
		request.session['Current_WIP_title'] = thePoem.title
		theWIPNotes = Note.objects.filter(poem_id=request.session['Current_WIP_poem'], type='_wip_').order_by(
			'-updated')
		if theWIPNotes.count() == 0:
			# create the current WIP nate
			with open(settings.INITIAL_POEM_DRAFT, 'r') as f:
				tempContent = f.read()
			theContent = tempContent % {"title": thePoem.title}
			Note.objects.create(poem=thePoem, type='_wip_', topic='_00', content=theContent)
			theWIPNotes = Note.objects.filter(poem=thePoem, type='_wip_').order_by('-created')
		wipNote = theWIPNotes[0]  # latest
		request.session['Current_WIP_note_URL'] = u'/admin/collection/note/%s/change' % wipNote.id
	else:
		request.session['Current_WIP_title'] = None
		request.session['Current_WIP_note_URL'] = None
	return


def validPoem(poem_id):
	try:
		thePoem = Poem.objects.get(poem_id=poem_id)
		return True, thePoem
	except:
		return False, None


def poemHasAnSD(poem_id):
	isValid, thePoem = validPoem(poem_id)
	if isValid:
		if thePoem.sd is not None and thePoem.sd != '':
			return True
	return False


def getSupportLookup(theContext):
	diag = True
	o = urlparse(theContext)
	thePath = o.path
	pathBits = thePath.split('/')
	i = -1
	theNewPath = ''
	for bit in pathBits:
		i += 1
		if bit == '' or bit == 'admin':
			continue
		elif bit.isdigit():
			pathBits[i] = settings.HELP_SUBSITUTE_FOR_NUMBERS
		theNewPath += (pathBits[i] + "/")
	try:
		hlp = Help.objects.get(context=theNewPath)
		theLookup = settings.HELP_URL_PREFIX + hlp.lookup + '.html'
	except Help.DoesNotExist:
		theLookup = "SorryThereIsNoSupport"
	if diag is True:
		return ''
	else:
		return theLookup


def initialiseCategories(userID, userName):
	Category.objects.create(name=userName, poet_id=userID)
	theParent = Category.objects.get(name=userName, poet_id=userID)
	for i in range(0, len(MAJOR_CATEGORIES)):
		Category.objects.create(name=MAJOR_CATEGORIES[i], parent=theParent, poet_id=userID)
	for i in range(0, len(SUB_CATEGORIES)):
		prnt, ctgry = SUB_CATEGORIES[i]
		theParent = Category.objects.get(name=prnt, poet_id=userID)
		Category.objects.create(name=ctgry, parent=theParent, poet_id=userID)
	return


def get_QuerysetFPLIDs(qs, currentID):
	IDs = []
	for q in qs:
		IDs.append(q[0])
	noIDs = len(IDs)
	if noIDs == 1:
		return currentID, currentID, currentID, currentID
	else:
		firstID = IDs[0]
		lastID = IDs[-1]
		i = IDs.index(currentID)
		if i == 0:
			previousID = lastID
		else:
			previousID = IDs[i - 1]
		if i == noIDs - 1:
			nextID = firstID
		else:
			nextID = IDs[i + 1]
		return firstID, previousID, nextID, lastID


def versionCurrentWIPNote(self, request, queryset):
	# get current WIP
	wip_id = int(request.session['Current_WIP_poem'])
	qs = queryset[0]
	if qs.poem_id != wip_id or qs.type != '_wip_' or queryset.count() != 1:
		scriptMessages(request, 'Error: Can only version the current Wip note')
		return
	# get current wip note number & increment
	try:
		newTopic = "_{:02d}".format((int(qs.topic[-2:]) + 1))
	except:
		newTopic = u'%s_%s' % (qs.topic, '00')
	Note.objects.create(poem_id=qs.poem_id, type=qs.type, topic=newTopic, content=qs.content)
	qs.type = '_vrn_'
	qs.save()
	get_Current_WIP_details(request)

versionCurrentWIPNote.short_description = 'make a new version of the current WIP'


def unsetTheCurrentWIP(request, wip_id):
	# unset the current WIP
	up = Profile.objects.get(user=request.session['User_id'])
	up.wipp_id = None
	up.save()
	get_UserProfileIntoSessionValues(request)
	get_Current_WIP_details(request)
	# unset the poem as WIP
	wipPoem = Poem.objects.get(id=wip_id)
	wipPoem.wip = False
	wipPoem.save()
	if request.session['Verbose system messages']: scriptMessages(request,
				   u"The current WIP poem '%s' status has been revoked and a finished note made" % wipPoem.title)
	return


def createAFinishedVersionOfTheCurrentWIPPoem(self, request, queryset):
	# get current WIP
	wip_id = int(request.session['Current_WIP_poem'])
	qs = queryset[0]
	if qs.poem_id != wip_id or qs.type != '_wip_' or queryset.count() != 1:
		scriptMessages(request, 'Error: Can only creat a finished version the current Wip poem note')
		return
	# create finished note
	Note.objects.create(poet=qs.poet, poem_id=qs.poem_id, type=None, subtype='_fin_', topic='', content=qs.content)
	unsetTheCurrentWIP(request, wip_id)
	return

createAFinishedVersionOfTheCurrentWIPPoem.short_description = 'create a finished version of the current WIP'


def theAlert4CompsClosing(self, request, queryset):
	message_bit = alert2CompsClosing(request)
	scriptMessages(request, message_bit)
	return

theAlert4CompsClosing.short_description = "Alert for competitions closing"


def compsLastUpdated(self, request, queryset):
	sp = SystemParameters.objects.get(pk=1)
	compLu = luFormat('Competitions', sp.cplu, sp.cpui)
	scriptMessages(request, compLu)
	return

compsLastUpdated.short_description = "Competitions last updated"


def magsLastUpdated(self, request, queryset):
	sp = SystemParameters.objects.get(pk=1)
	mgzLu = luFormat('Magazines', sp.mzlu, sp.mzui)
	scriptMessages(request, mgzLu)
	return

magsLastUpdated.short_description = "Magazines last updated"


def pubsLastUpdated(self, request, queryset):
	sp = SystemParameters.objects.get(pk=1)
	pubLu = luFormat('Publishers', sp.pblu, sp.pbui)
	scriptMessages(request, pubLu)
	return

pubsLastUpdated.short_description = "Publishers last updated"


def luFormat(cpp, lastUpdated, updateInterval):
	nextUpdate = (lastUpdated + timedelta(days=updateInterval))
	lu = lastUpdated.strftime('%A %d %B')
	nu = nextUpdate.strftime('%A %d %B')
	now = datetime.now(timezone.utc)
	if nextUpdate > now:
		return u'Last updated %s: on  %s,  their update interval is %s days, the next update is due on %s\n' \
			   % (cpp, lu, updateInterval, nu)
	else:
		return u'Last updated %s: on  %s,  their update interval is %s days, the next update is overdue!\n' \
			   % (cpp, lu, updateInterval)


def lastUpdated():
	sp = SystemParameters.objects.get(pk=1)
	compLu = luFormat('Competitions', sp.cplu, sp.cpui)
	mgzLu = luFormat('Magazines', sp.mzlu, sp.mzui)
	pubLu = luFormat('Publishers', sp.pblu, sp.pbui)
	return compLu + mgzLu + pubLu


def alert2CompsClosing(request):
	msg = ''
	countryPref = request.session['Country_preference']
	# get closing window dates
	alertWindowDays = request.session['Advanced_days_warning_of_competition_closure']
	msgClosingIn = ['' for days in range(alertWindowDays + 1)]
	nCT = [0 for days in range(alertWindowDays + 1)]
	nowDate = datetime.now().date()
	endWindowDate = nowDate + timedelta(days=alertWindowDays)
	# get competitons that are closing
	compsClosing = Competition.objects.filter((Q(poet=request.user) | Q(poet_id=settings.THE_ADMIN_ID)),
											  closingDate__gte=nowDate, closingDate__lte=endWindowDate, ).order_by(
		'closingDate')
	nocompsClosing = compsClosing.count()
	if nocompsClosing == 0:
		if request.session['Verbose system messages']: msg += u'Info: There are no competitions closing within the next %s days.\n' % (alertWindowDays)
	else:
		# get counts by country
		countsClosingByCountry = compsClosing.values('country').annotate(countByC=Count('country'))
		ccbc = ''
		for eachCount in countsClosingByCountry:
			if eachCount['country'] == request.session['Show competitions closing in country'] or request.session[
				'Show competitions closing in country'] == 'ALL':
				ccbc += u' %s has %s ,' % (eachCount['country'], eachCount['countByC'])
		if request.session['Show competitions closing in country'] == 'ALL':
			countriesPrefix = 'Across all countries there'
		else:
			countriesPrefix = 'There'
		msg += u'Info: %s %s %s competition%s closing within the next %s days the %s\n' % (countriesPrefix,
																						   is_are(nocompsClosing),
																						   nocompsClosing,
																						   pluralize(nocompsClosing),
																						   alertWindowDays, ccbc[:-1])
		# process each comp
		for cc in compsClosing:
			country = cc.country
			# only show comps for requested or ALL
			if country == request.session['Show competitions closing in country'] or request.session[
				'Show competitions closing in country'] == 'ALL':
				countrySuffix = ''
				if country != countryPref: countrySuffix = u' - %s' % country
				cd = cc.closingDate
				dDiff = cd - nowDate
				cDays = dDiff.days
				if cDays <= alertWindowDays:
					nCT[cDays] += 1
					msgClosingIn[cDays] += u' %s%s |' % (cc.name, countrySuffix)
		for nDay in range(alertWindowDays + 1):
			if nCT[nDay] != 0:
				if nDay == 0:
					nCT0 = nCT[0]
					msg += u'Alert: %s competition%s %s closing today ! %s\n' % (
						nCT0, pluralize(nCT0), is_are(nCT0), msgClosingIn[0][:-1])
				else:
					msg += u'Info: %s day%s to the closure of %s competition%s: %s\n' % (
						nDay, pluralize(nDay), nCT[nDay], pluralize(nCT[nDay]), msgClosingIn[nDay][:-1])
	return msg


def poemsThatHaveExpired(request):
	from datetime import datetime
	today = datetime.now()
	expMsg=''
	# expired competitions
	themsgE = ''
	noOfEntriesExpired = 0
	expiredEntries = Entry.objects.filter(expiredOn=None).filter(committedUntil__lt=today)
	for ee in expiredEntries:
		thePoem_id = ee.poem_id
		thePoem = Poem.objects.get(id=thePoem_id)
		#  check for one of ours
		if thePoem.poet_id == request.user.id:
			# expire the poem
			ee.expireEntry('unp')
			noOfEntriesExpired += 1
			themsgE += u'Info: The entry of the poem: %s to the competition: %s has expired\n' % \
					   (thePoem.title, ee.competition)
	if noOfEntriesExpired == 0:
		if request.session['Verbose system messages']: expMsg = "There are no expired competition entries.\n"
	else:
		expMsg = u"There %s %s expired entries.\n%s" % (is_are(noOfEntriesExpired), noOfEntriesExpired, themsgE)

	# expired submissions
	themsgS = ''
	noOfSubmissionsExpired = 0
	expiredSubmissions = Submission.objects.filter(expiredOn=None).filter(committedUntil__lt=today)
	for ss in expiredSubmissions:
		thePoem_id = ss.poem_id
		thePoem = Poem.objects.get(id=thePoem_id)
		#  check for one of ours
		if thePoem.poet_id == request.user.id:
			# expire the poem
			ss.expireSubmission('exprd')
			noOfSubmissionsExpired += 1
			themsgS += u'The poem: %s which was a submission to the magazine: %s has expired\n' % (
				thePoem.title, ss.magazine)
	if noOfSubmissionsExpired == 0:
		if request.session['Verbose system messages']: expMsg += "There are no expired submissions to magazines.\n"
	else:
		expMsg += u"There %s %s expired submissions.\n%s" % (
			is_are(noOfSubmissionsExpired), noOfSubmissionsExpired, themsgS)

	return expMsg


def updatesToDownloads(request, lastHK):
	utdrMsg = ''
	theOS = request.user_agent.os.family
	dR = Download.objects.filter((Q(os=theOS) | Q(os="All")) & Q(updated__lte=lastHK))
	dRCount = dR.count()
	if dRCount > 0:
		utdrMsg = u'%s download%s %s been updated' % (dRCount, pluralize(dRCount), has_have(dRCount))
	return utdrMsg


def houseKeeping(request):
	# safety check - admin does not do housekeeping
	if request.session['is_Admin']:
		return
	nowDate = datetime.now().date()
	if request.session['Last_HK_run_on'] is None:  # not run before so set to yesterday
		lastTime4hkDate = nowDate - timedelta(days=1)
	else:
		lastTime4hkDate = datetime.strptime(request.session['Last_HK_run_on'], '%Y-%m-%d').date()
	# check ok to perform only do it once a day for each user
	msg = ''
	if lastTime4hkDate < nowDate:
		version = get_Version(1)
		if request.session['Verbose system messages']: msg = u"Success: BEGIN HOUSEKEEPING\n"
		msg += alert2CompsClosing(request) + '\n'
		msg += poemsThatHaveExpired(request) + '\n'
		msg += updatesToDownloads(request, lastTime4hkDate) + '\n'
		if request.session['Verbose system messages']: msg += u"Success: END HOUSEKEEPING\n"
		# update hk run on
		request.session['Last_HK_run_on'] = nowDate.isoformat()
		set_UserProfileFromSessionValues(request)
	if msg != '':
		scriptMessages(request, msg)
	return


def lookupId(id, demo, newUser):
	theIndex = demo.index(id)
	return newUser[theIndex]


def download_page(url):
	return urlopen(url).read().decode('utf-8')


def updateAllCompetitions(self, request, queryset):
	updateUKComps(self, request, queryset)

	updateUSAComps(self, request, queryset)

	removeClosedCompetitions(self, request, queryset)

	return

updateAllCompetitions.short_description = 'Update all Competitions'


def updateUKComps(self, request, queryset):
	# 21-Feb-21 fix
	# & added problem trapping & reporting
	# 07-Feb-20 changed to accomodate webresource
	# nb can't get prize info diectly from website

	today = datetime.now()

	compCountUK = 0
	probCountUK = 0
	probComps = ''
	if len(queryset) == 0:
		empty = True
	else:
		empty = False

	ukComp = webResource.objects.get(country='GBR', type=1)

	compLu = luFormat('UK Competitions', ukComp.updated, ukComp.updateInterval)

	# check if overdue
	if not ('overdue' in compLu):
		scriptMessages(request, u'Warning: %s' % compLu)
	else:
		sth = ukComp.refSource  # nb refSource is a URL string
		target_home = unquote(sth)  # convert to string
		target_link = ukComp.reflink  # nb reflink is string
		link_head = u'%s/' % target_link

		# loop through pages - max 10
		for i in range(10):
			target_url = target_home + target_link
			if i > 0: target_url += '?page=' + str(i)
			nplComps_html = download_page(target_url)
			soup = BeautifulSoup(nplComps_html, 'html.parser')
			links = soup.find_all('a', href=True)
			previous_link = ''
			for link in links:
				link_href = link['href']
				if link_head in link_href:
					if link_href != previous_link:
						previous_link = link_href
						comp_link = target_home + link_href
						comp_html = download_page(comp_link)
						soup = BeautifulSoup(comp_html, 'html.parser')
						competition_name = soup.find_all('h1')[1]  # fix 21-Feb-21
						cd = soup.find('div',
									   class_='field field--name-field-date-override field--type-text field--label-hidden')
						if cd is None:
							cd = soup.find('div',
										   class_='field field--name-field-api-comp-date field--type-date field--label-hidden')
						try:
							clsngDt = parser.parse(cd.string)
						except:
							probCountUK += 1
							probComps += competition_name.string + ' - '
							continue
						fee = soup.find('div',
										class_='field field--name-field-price-text field--type-text field--label-hidden')
						ef0 = fee.string
						ef1 = ef0.replace('|', '')
						ef = ef1.strip()
						entryfee = ef[:40]
						comp_Link = soup.find('a', text='find out more')
						comp_Link_href = comp_Link['href']
						# add as new comp if closingdate gt today & not already got
						noOfComps = Competition.objects.filter(name=competition_name.string).count()
						if (clsngDt >= today) and (empty or (noOfComps == 0)):  # changed from get to filter
							newComp = Competition(name=competition_name.string, closingDate=clsngDt, url=comp_Link_href,
												  access='Public', entryFee=entryfee, country='GBR')
							newComp.save()
							compCountUK += 1
	# update counts
	ukComp.additions = compCountUK
	ukComp.noOfUpdates += 1
	ukComp.save()
	if compCountUK != 0: scriptMessages(request, u'%sInfo: Updated with %s new UK competition%s' %
										(compLu, compCountUK, pluralize(compCountUK)))
	if probCountUK != 0: scriptMessages(request, u'Warning: Problems with %s retrieval%s: %s' %
										(probCountUK, pluralize(probCountUK), probComps[:-3]))
	return


updateUKComps.short_description = 'Update UK Competitions'


def updateUSAComps(self, request, queryset):
	# 07-Feb-20 changed to accomodate webresource
	# web scraping changed becuase site reformatted info.

	today = datetime.now()
	usaComp = webResource.objects.get(country='USA', type=1)
	compCountUSA = 0
	probCount = 0
	probComps = ''
	# get last updated & interval
	compLu = luFormat('USA Competitions', usaComp.updated, usaComp.updateInterval)
	# check if overdue
	if not ('overdue' in compLu):
		scriptMessages(request, u'Warning: %s' % compLu)
	else:
		sth = usaComp.refSource  # nb refSource is a URL string
		target_home = unquote(sth)  # convert to string
		target_link = usaComp.reflink  # nb reflink is string
		target_url = target_home + target_link
		usaComps_html = download_page(target_url)
		soup = BeautifulSoup(usaComps_html, 'html.parser')
		# get compNmaes & links
		links = []
		compNames = []
		for tag in soup.find_all('h3'):
			for anchor in tag.find_all('a'):
				links.append(anchor['href'])
				compNames.append(anchor.get_text())
		ed = []
		noOfCompNames = len(compNames) - 1
		for tag in soup.find_all('div'):
			for anchor in tag.find_all('font'):
				ed.append(anchor.get_text())
		closingDate = []
		fee = []
		prize = []
		i = -1
		for txt in ed:
			if "Entry Deadline:" in txt:
				i += 1
				txts = txt.split(' ')
				date0 = txts[2]
				fee0 = txts[4]
				date1 = date0[:-5]
				fee1 = fee0[:-6]
				try:
					theCD = datetime.strptime(date1, '%m/%d/%Y')
					closingDate.append(theCD)
					fee.append(fee1)
					prize.append(txts[5])
				except:
					closingDate.append('')
					fee.append('')
					prize.append('')
				if i == noOfCompNames: break

		i = 0
		for lnk in links:
			if closingDate[i] != '':
				if closingDate[i] >= today and len(Competition.objects.filter(name=compNames[i])) == 0:
					newUSComp = Competition(name=compNames[i], closingDate=closingDate[i], url=lnk, access='Public',
											entryFee=fee[i], prize=prize[i], country='USA')
					newUSComp.save()
					compCountUSA += 1
			else:
				probCount += 1
				probComps += compNames[i] + ' - '
			i += 1
	# update latest count
	usaComp.additions = compCountUSA
	usaComp.noOfUpdates += 1
	usaComp.save()
	# inform
	if compCountUSA != 0: scriptMessages(request, u'%sInfo: Updated with %s new USA competition%s' % (
		compLu, compCountUSA, pluralize(compCountUSA)))
	if probCount != 0:    scriptMessages(request, u'Warning: Problems with %s retrieval%s: %s' % (
		probCount, pluralize(probCount), probComps[:-3]))
	return


updateUSAComps.short_description = 'Update USA Competitions'


def removeClosedCompetitions(self, request, queryset):
	# remove all public, closed competitions that don't have entries 27-Jan-20
	today = datetime.now()
	oldComps = Competition.objects.filter(closingDate__lt=today).filter(access='Public')
	if len(oldComps) > 0:
		removedComps = 0
		for oC in oldComps:
			oCid = oC.id
			ocEntries = Entry.objects.filter(competition_id=oCid)
			if len(ocEntries) == 0:
				Competition.objects(id=oCid).delete()
				removedComps += 1
		if removedComps != 0:
			scriptMessages(request,
						   u'Info: Removed %s competition%s whose closing date%s had expired & had no entries' % removedComps,
						   pluralize(removedComps), pluralize(removedComps))
	return


removeClosedCompetitions.short_description = 'Remove closaed Competitions'


def updateMagazines(self, request, queryset):
	updateUKMagazines(self, request, queryset)

	return


updateMagazines.short_description = 'Update Magazines'


def updateUKMagazines(self, request, queryset):
	"""
		Extract details of poetry Magazines
		from the National Poetry Library website
		last updated:	 2019-Mar-20
		modifications:	 2019-Sep-26
	"""
	# get last updated & interval

	ukMgz = webResource.objects.get(country='GBR', type=2)
	# mgzCountUK = 0
	# get last updated & interval
	mgzLu = luFormat('UK Magaziness', ukMgz.updated, ukMgz.updateInterval)

	# check if overdue
	if not ('overdue' in mgzLu):
		scriptMessages(request, u'Warning: %s' % mgzLu)
		return

	if len(queryset) == 0:
		empty = True
	else:
		empty = False

	# today = datetime.now()

	sth = ukMgz.refSource  # nb refSource is a URL string
	target_home = unquote(sth)  # convert to string
	target_link = ukMgz.reflink  # nb reflink is string
	link_head = u'%s/' % target_link

	newMagcount = 0

	for i in range(25):

		target_url = target_home + target_link
		if i > 0: target_url += '?page=' + str(i)
		nplMags_html = download_page(target_url)
		soup = BeautifulSoup(nplMags_html, 'html.parser')
		links = soup.find_all('a', href=True)
		previous_link = ''

		for link in links:
			link_href = link['href']

			if link_head in link_href:
				if link_href != previous_link:
					previous_link = link_href
					mag_link = target_home + link_href
					mag_html = download_page(mag_link)
					soup = BeautifulSoup(mag_html, 'html.parser')

					magazine_name = soup.find_all('h1')[1]  # fix 21-Feb-21

					try:
						mag_Link = soup.find('a', text='Visit website')
						mag_Link_href = mag_Link['href']
					except:
						mag_Link_href = mag_link
					if empty or len(Magazine.objects.filter(name=magazine_name.string)) == 0:
						newMag = Magazine(name=magazine_name.string, url=mag_Link_href, access='Public')
						newMag.save()
						newMagcount += 1

	# update last updated
	ukMgz.additions = newMagcount
	ukMgz.noOfUpdates += 1
	ukMgz.save()
	if newMagcount > 0: scriptMessages(request,
									   u'Info: Updated with %s new UK magazine%s' % (newMagcount, pluralize(newMagcount)))
	return


def updatePublishers(self, request, queryset):
	updateUKPublishers(self, request, queryset)

	return


def updateUKPublishers(self, request, queryset):
	"""
		Extract detaills of poetry Publications
		from the National Poetry Library website
		last updated:	 2019-Mar-16
		modifications:   2019-Sep-26
	"""

	ukPub = webResource.objects.get(country='GBR', type=3)

	# get last updated & interval
	pubLu = luFormat('UK Magaziness', ukPub.updated, ukPub.updateInterval)

	# check if overdue
	if not ('overdue' in pubLu):
		scriptMessages(request, u'Warning: %s' % pubLu)
		return

	if len(queryset) == 0:
		empty = True
	else:
		empty = False

	sth = ukPub.refSource  # nb refSource is a URL string
	target_home = unquote(sth)  # convert to string
	target_link = ukPub.reflink  # nb reflink is string
	link_head = u'%s/' % target_link

	newPubcount = 0

	for i in range(25):

		target_url = target_home + target_link
		if i > 0: target_url += '?page=' + str(i)
		nplComps_html = download_page(target_url)
		soup = BeautifulSoup(nplComps_html, 'html.parser')
		links = soup.find_all('a', href=True)
		previous_link = ''

		for link in links:
			link_href = link['href']

			if link_head in link_href:
				if link_href != previous_link:
					previous_link = link_href
					pub_link = target_home + link_href
					pub_html = download_page(pub_link)
					soup = BeautifulSoup(pub_html, 'html.parser')

					publication_name = soup.find_all('h1')[1]  # fix 22-Feb-21

					try:
						pub_Link = soup.find('a', text='Visit website')
						pub_Link_href = pub_Link['href']
					except:
						pub_Link_href = pub_link

					if empty or len(Publisher.objects.filter(name=publication_name.string)) == 0:
						newPub = Publisher(name=publication_name.string, url=pub_Link_href, access='Public',
										   country='GBR')
						newPub.save()
						newPubcount += 1
	# update last updated
	ukPub.additions = newPubcount
	ukPub.noOfUpdates += 1
	ukPub.save()
	if newPubcount > 0: scriptMessages(request,
									   u'Info: Updated with %s new UK publisher%s' % (newPubcount, pluralize(newPubcount)))
	return


updatePublishers.short_description = 'Update Publishers'


def is_binary_file(filepathname):
	textchars = bytearray([7, 8, 9, 10, 12, 13, 27]) + bytearray(range(0x20, 0x7f)) + bytearray(range(0x80, 0x100))
	is_binary_string = lambda bytes: bool(bytes.translate(None, textchars))
	if is_binary_string(open(filepathname, 'rb').read(1024)):
		return True
	else:
		return False


def processUploads(self, request, queryset):
	# 29-Feb-20 removed encryption & replaced with checksum sha256
	# 05-Mar-20 added hidden filename to filelist resaved file
	#           computed checksum, processsed file without filename

	# 25-Aug-21 revised the file validation
	#           add capability to process changes to categories
	#           and titles that have been categorized
	#
	# get user parameters
	defaultUpdateTag = request.session['Default_update_tag']
	thedefaultPoeticForm = 1  # blank
	normalseTitle = request.session['Handle_titles']
	# initialise counts
	poemCount = 0
	duplicateTitleCount = 0
	uploadCount = 0
	titlesDocCount = 0
	logoImageCount = 0
	rejectedCount = 0
	rejected = '\nWarning: The Upload file has been removed !'
	removedCategoriesCount=0
	addedCategoriesCount=0
	renamedCategoriesCount=0
	titlesCategorizedCount=0

	for q in queryset:
		uploadCount += 1
		if q.type == 1:  # logo image
			logoImageCount += 1
			theDocument = str(q.logo)
			upFile = os.path.join(settings.MEDIA_ROOT, theDocument)
			# check if already have logo and if so remove the file\
			# NB if multiple logp's only the LAST one will be retained !
			if request.session['logo'] != '' and request.session['logo'] is not None:
				os.remove(request.session['logo'])
			request.session['logo'] = upFile
			request.session['logo choice'] = 1  # set to personal
			set_UserProfileFromSessionValues(request)
		else:  # it's titles document
			titlesDocCount += 1
			theDocument = str(q.document)
			theFilePath = os.path.join(settings.MEDIA_ROOT, theDocument)
			# check that the file is NOT binary
			if is_binary_file(theFilePath):
				scriptMessages(request, u"Error: %s is not a valid titles document (text file) %s" % (theDocument, rejected))
				os.remove(upFile)
				continue
			thepoetID, theHbUploadFile = theDocument.split(os.path.sep)
			# check for duplicate file will have _ + 7 random chars suffix
			nparts = ()
			nparts = theHbUploadFile.split('_')
			if len(nparts) >= 7:
				msg = u"\nError: %s is a duplicate file - the original may have already been processed." \
					  u"\nError: The file has been rejected and the titles have not been processed." % theDocument
				scriptMessages(request, msg)
				rejectedCount += 1
				continue  # there maybe more upload files
			lines=validateAndReadTamperProofFile(theDocument, theFilePath )
			noOfTitles = len(lines)
			if  noOfTitles==0:
				msg = u"\nError: Unable to validate and/or read the upload file: %s" \
					  u"\nError: Suspect that the file may have been tampered with, or become damaged or unreadable. " \
					  u"\nError: The file's processing has been abandoned" % theDocument
				scriptMessages(request, msg)
				break
			for aline in lines:
				line = aline.rstrip('\n')
				# ignore ... comment lines
				if line.startswith(COMMENT_PREFIX):
					continue
				# check for html
				if bool(BeautifulSoup(line, "html.parser").find()):
					msg = u"\nError: Found the following HTML in the upload file %s ?!" \
						  u"\nError: %s\n" \
						  u"\nError: The 'title' is rejected and this upload file processing has been abandoned" % (
							  theHbUploadFile, line)
					scriptMessages(request, msg)
					break
				# no HTML found
				haveTitle=False
				if line.startswith(ADD_CATEGORY_PREFIX) or line.startswith(REMOVE_CATEGORY_PREFIX) or line.startswith(RENAME_CATEGORY_PREFIX):
					subcat, majorcat = line[2:].split(CATEGORY_DELIM)
					subcat=subcat.strip()
					majorcat = majorcat.strip()
					if majorcat=='*':
						majorcat=request.session['User_name']
					mc=Category.objects.get(poet=request.user,name=majorcat)
					majorcat_id=mc.id
					if line.startswith(ADD_CATEGORY_PREFIX):
					# check that majorCat exists and subcat does NOT exist
						try:
							cat=Category.objects.get(poet_id=request.user.id,name=subcat,parent_id=majorcat_id)
							msg = u"\nError: Atempting to add this category with the line" \
								  u"\nError: %s (category | parent)\n" \
								  u"\nError: fromthe upload file: %s" \
								  u"\nError: and discovered it already exists. " \
								  u"\nError: The upload file processing has been abandoned." % (line,  theHbUploadFile)
							scriptMessages(request, msg)
							break
						except (Category.DoesNotExist):
								newCat=Category.objects.create(poet_id=request.user.id,name=subcat,parent_id=majorcat_id)
								# newSubCat=OrderedInsertion.objects.create(name=subcat, parent=majorcat)
								Category.objects.rebuild()
								# newCat.refresh_from_db()
								addedCategoriesCount +=1
					elif line.startswith(REMOVE_CATEGORY_PREFIX):
						# check that majorCat and subcat exist
						try:
							cat = Category.objects.get(poet_id=request.user.id, name=subcat, parent_id=majorcat_id)
							# check that there are no poems assigned to the category
							sc = Category.objects.get(poet=request.user, name=subcat)
							subcat_id = sc.id
							nPoemsAssignedToCat=Categorize.objects.filter(poet_id=request.user.id, category_id=subcat_id).count()
							if  nPoemsAssignedToCat >0:
								msg = u"\nError: Atempting to remove this category with the line" \
									  u"\nError: %s (category | parent)\n" \
									  u"\nError: from the upload file: %s" \
									  u"\nError: and discovered it has %s titles assigned.. " \
									  u"\nError: The upload file processing has been abandoned." % (
									  line, theHbUploadFile, nPoemsAssignedToCat)
								scriptMessages(request, msg)
								break
							Category.objects.get(poet_id=request.user.id, name=subcat, parent_id=majorcat_id).delete()
							Category.objects.rebuild()
							removedCategoriesCount+=1
						except (Category.DoesNotExist):
							msg = u"\nError: Atempting to remove this category with the line" \
								  u"\nError: %s (category | parent)\n" \
								  u"\nError: from the upload file: %s" \
								  u"\nError: and discovered it does not  exist. " \
								  u"\nError: The upload file processing has been abandoned." % (line, theHbUploadFile)
							scriptMessages(request, msg)
							break
					elif line.startswith(RENAME_CATEGORY_PREFIX):
						oldcat=subcat
						newcat=majorcat
						msg=''
						# check that oldCat exists and newCat does not exist
						if Category.objects.filter(poet_id=request.user.id, name=oldcat).count()==0:
							msg=u"The old category '%s' does not exist so unable to rename it as the new category '%s'" %(oldcat,newcat)
						else:
							if Category.objects.filter(poet_id=request.user.id, name=newcat).count() != 0:
								msg=u"The new category '%s' already exists so unable use it to rename the old category '%s'" %(newcat,oldcat)
							else:
								catRename=Category.objects.get(poet_id=request.user.id, name=oldcat)
								catRename.name=newcat
								catRename.save()
								renamedCategoriesCount +=1
						if msg!='': scriptMessages(request,msg)
				elif line.startswith(CATEGORIZED_TITLE_PREFIX):
					haveTitle=True
					newTitle0, subcat, majorcat = line[2:].split(CATEGORY_DELIM)
					newTitle0=newTitle0.strip()
					subcat=subcat.strip()
					sc = Category.objects.get(poet=request.user, name=subcat)
					subcat_id = sc.id
					majorcat=majorcat.strip()
					catTitle=True
				else:   # just title
					haveTitle = True
					newTitle0 = line.strip()
					catTitle = False

				if haveTitle:
					# normalise
					if normalseTitle == 0:
						newTitle = newTitle0
					elif normalseTitle == 1:
						newTitle = newTitle0.capitalize()
					else:
						newTitle = newTitle0.lower()
					# check for duplicate
					if Poem.objects.filter(title=newTitle).exists():
						duplicateTitleCount += 1
					else:
						# add new title
						np = Poem.objects.create(title=newTitle, form_id=thedefaultPoeticForm )
						np.tags.add(defaultUpdateTag)
						np.save()
						poemCount += 1
					# check if need to categorize the title
						if catTitle:
							Categorize.objects.create(poet=request.user, poem_id=np.id, category_id=subcat_id)
							titlesCategorizedCount+=1
	# finished processing the queryset

	# deletes queryset (to prevent duplicate processing)
	# this also deletes all text FILES but NOT any image files
	queryset.delete()
	# build processed message
	msg = u'Info: Processed %s upload%s \n' % (uploadCount, pluralize(uploadCount))
	if removedCategoriesCount!=0:
		msg += u' removed %s categor%s \n'  %  (removedCategoriesCount, y_ies(removedCategoriesCount))
	if addedCategoriesCount!=0:
		msg += u' added %s categor%s \n' % (addedCategoriesCount, y_ies(addedCategoriesCount))
	if renamedCategoriesCount!=0:
		msg += u' renamed %s categor%s \n' % (renamedCategoriesCount, y_ies(renamedCategoriesCount))
	if titlesDocCount != 0:
		msg += u' %s titles document%s \n' % (titlesDocCount, pluralize(titlesDocCount))
	if titlesCategorizedCount!=0:
		msg += u' of which %s have been categorized \n' % titlesCategorizedCount
	if logoImageCount != 0:
		msg += u' %s logo image%s \n' % (logoImageCount, pluralize(logoImageCount))
	if logoImageCount > 1:
		msg += u' ONLY THE LAST LOGO HAS BEEN RETAINED \n'
	if rejectedCount != 0:
		msg += u' - rejected %s. \n' % rejectedCount
	if poemCount == 0:
		msg += ' No new tiles !?\n'
	else:
		msg += u'%s new title%s. \n' % (poemCount, pluralize(poemCount))
	if duplicateTitleCount != 0:
		msg += u' %s duplicate title%s ignored \n' % (duplicateTitleCount, pluralize(duplicateTitleCount))
	scriptMessages(request, msg)
	return

processUploads.short_description = "Process upload"


def createCategoryDownloads(self, request, queryset):
	nowDT = datetime.now()
	dateTime=nowDT.strftime("%y%m%d%H%M%S")
	expandedDT=nowDT.strftime("%y-%b-%d  @ %H:%M:%S")
	catFilename='__hb_Categories_' + dateTime + '.cfg'
	prefix = 'poet_{}'.format(request.session['User_id'])
	catPath = os.path.join(settings.MEDIA_ROOT, prefix,'Downloads' ,catFilename)
	# create CP categories which will be in the form of a dictionary
	#  key             values-list
	# category-name:  (parent-name, poem-count)
	# files will be in the media-root / poet_id  sub-dir
	t_categories = {}
	t_parents={}
	categoriesCP = {"*": []}
	userName=request.session['User_name']
	theCats=queryset.order_by('level','name')
	try:
		for cat in theCats:
			theCatName = cat.name
			if cat.name==userName:
				theCatName="*"
				theCatParentName=''
			else:
				theCatParent_id=cat.parent_id
				theCatParent=Category.objects.get(id=theCatParent_id)
				theCatParentName=theCatParent.name
				if theCatParentName==userName: theCatParentName="*"
			# print(theCatName,theCatParentName, cat.count)
			# add the new dictionary entry
			t_categories[theCatName] = (theCatParentName, cat.count)
			# check for parent key in dictionary
			if theCatParentName!='':
				if theCatParentName not in t_parents:
					t_parents[theCatParentName]=list()
				t_parents[theCatParentName].append(theCatName)
		# sort & eliminate duplicates from t_categories
		s_categories = sorted(t_categories.items(), key=operator.itemgetter(0))
		categoriesCP = collections.OrderedDict(s_categories)
		# sort t_pareents into descending order
		categoriesPC = t_parents
		# write CP & PC as json dumps to the cfg file
		with open(catPath, 'w') as f:
			jsondump(categoriesCP, f)
			f.write('\n')
			jsondump(categoriesPC, f)
		# create the download record
		newCatDownload = Download.objects.create(poet_id=request.session['User_id'], type=5, os='All',
												 description=catFilename, file=catPath)
		newCatDownload.save()
		msg = 'Info: Sucessfully created the category file             PREPARATORY TO DOWNLOADING\n'
	except Exception as e:
		msg=u'Error: Failed to create the category download file with error: %s' % e
	scriptMessages(request,msg)
	return

createCategoryDownloads.short_description="Create category downloads"


def downloadDownloads(self, request, queryset):
	if len(queryset)>1:
		scriptMessages(request, 'Error: You can only download 1 file at a time')
		return
	else:
		theFilePath=queryset[0].file
		filepath, filename= os.path.split(theFilePath)
		path = open(theFilePath, 'r')
		# Set the mime type
		mime_type, _ = mimetypes.guess_type(theFilePath)
		# Set the return value of the HttpResponse
		response = HttpResponse(path, content_type=mime_type)
		# Set the HTTP header for sending to browser
		response['Content-Disposition'] = "attachment; filename=%s" % filename
		# Return the response value
		return response

downloadDownloads.short_description = "Download the downloads"

