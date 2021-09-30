#################################################################
# Culls titles for                                              #
# hummingbird3  application                                     #
# from the users poem document files                            #
# In addition can be used  to categorize poems                  #
#                                                               #
# GUI dependes exclusively  on PySimpleGUI                      #
#                                                               #
# Version 0.3.1                                                 #
# last updated 30-Jul-21                                        #
# Version 0.3.2                                                 #
# last updated 01-Aug-21  added settings file load/save         #
# version 0.3.3                                                 #
# last updated 04-aug-2021 highlighted next to be used buttom   #
# version 0.4.0                                                 #
# last updated 08-aug-2021 renamed getPoemTitles                #
# included extra step for categorization                        #
# version 0.5.0                                                 #
# last updated 16-aug-2021                                      #
# included show category tree - add category                    #
# version 0.6.0                                                 #
# last updated 24-aug-2021                                      #
# pass categorry updates into upload file                       #
# version 0.6.1                                                 #
# last updated 14-sep-2021                                      #
# category rename facility & CP/PC files in Downloads           #
# version 0.6.2                                                 #
# last updated 20-sep-2021                                      #
# seperate category update included                             #
#################################################################
# IMPORTANT                                                     #
# This utility makes use of 2 files in a sub-directory named    #
# hummingbird located in the useres Downloads directory         #
# if the files are not pressent they are created with defaults  #
#################################################################

import collections
import fnmatch
import operator
import os
import re
import sys
from datetime import datetime
from json import (loads as jsonload, dump as jsondump)
from os import path, listdir
from os.path import isfile, join
from pathlib import Path
from stat import S_IREAD

import PySimpleGUI as sg
import textract
from dateutil.parser import parse
from filehash import FileHash

# =========== Constants ========================================

HB_HUMMINGBIRD = [
    "... ╔╗─────────────────╔══╗─────╔╗",
    "... ║║─────────────────║╔╗║─────║║",
    "... ║╚═╦╗╔╦╗╔╦╗╔╦╦══╦══╣╚╝╚╦╦═╦═╝║",
    "... ║╔╗║║║║╚╝║╚╝╠╣╔╗╣╔╗║╔═╗╠╣╔╣╔╗║",
    "... ║║║║╚╝║║║║║║║║║║║╚╝║╚═╝║║║║╚╝║",
    "... ╚╝╚╩══╩╩╩╩╩╩╩╩╝╚╩═╗╠═══╩╩╝╚══╝",
    "... -───────────────╔═╝║",
    "... ────────────────╚══╝"]
HB_TITLES = [
    "... ──────────────╔╗─╔╗╔╗",
    "... ─────────────╔╝╚╦╝╚╣║",
    "... ╔══╦══╦══╦╗╔╗╚╗╔╬╗╔╣║╔══╦══╗",
    "... ║╔╗║╔╗║║═╣╚╝║─║║╠╣║║║║║═╣══╣",
    "... ║╚╝║╚╝║║═╣║║║─║╚╣║╚╣╚╣║═╬══║",
    "... ║╔═╩══╩══╩╩╩╝─╚═╩╩═╩═╩══╩══╝",
    "... ║║",
    "... ╚╝"]

HB_AND = [
    "... ────────╔╗",
    "... ────────║║",
    "... ╔══╦═╗╔═╝║",
    "... ║╔╗║╔╗╣╔╗║",
    "... ║╔╗║║║║╚╝║",
    "... ╚╝╚╩╝╚╩══╝"]
HB_CATEGORY_UPDATES = [
    "... ──────╔╗──────────────────────────╔╗──╔╗",
    "... ─────╔╝╚╗─────────────────────────║║─╔╝╚╗",
    "... ╔══╦═╩╗╔╬══╦══╦══╦═╦╗─╔╗──╔╗╔╦══╦═╝╠═╩╗╔╬══╦══╗",
    "... ║╔═╣╔╗║║║║═╣╔╗║╔╗║╔╣║─║║──║║║║╔╗║╔╗║╔╗║║║║═╣══╣",
    "... ║╚═╣╔╗║╚╣║═╣╚╝║╚╝║║║╚═╝║──║╚╝║╚╝║╚╝║╔╗║╚╣║═╬══║",
    "... ╚══╩╝╚╩═╩══╩═╗╠══╩╝╚═╗╔╝──╚══╣╔═╩══╩╝╚╩═╩══╩══╝",
    "... ───────────╔═╝║────╔═╝║──────║║",
    "... ───────────╚══╝────╚══╝──────╚╝"]

delims = ['__', '_', ' ', '--', '-']
ICON_FILE = '/Users/jr/adv/hb3/hummingbird3/_utilities_/getPoemDocuments.ico'
# DISPLAY_FILENAME =  r'/Users/jr/adv/hb3/hummingbird3/_utilities_/getDocuments_2.png'
# if you want to use a file instead of data, then use this in Image Element
DISPLAY_TIME_MILLISECONDS = 4000
VERSION = 'version: v0.6.2 20-Sep-21'
HB_UTILITY_TITLE = 'hummingbird utility'
HB_UTILITY_subTITLE = 'get poem titles'
HB_UPLOADFILE_NAME_PREFIX = '__hb_gpt_upload_'
sDIR = defaultPATH = os.getcwd()
EXTNS = ['.txt', '.rtf', '.rtfd', '.pdf', '.docx', '.doc', '.odt', '.pages']
nvEXTNS = ['.rtfd', '.pages']
getTextFromEXTNS = ['.txt', '.rtf', '.pdf', '.docx', '.doc', '.odt']
searchWORDS = ['~', 'backup', 'copy', 'revised', 'revision', 'duplicate', 'comment']
DELIMS = ['__', '_', ' ', '--', '-']
NUMBERS1 = [0, 10, 25, 50, 100, 250, 500, 1000]
NUMBERS2 = [n for n in range(1, 21)]
DAYSoftheMONTH = [d for d in range(1, 32)]
MONTHSoftheYEAR = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
currentDAY = datetime.now().day
currentMONTH = datetime.now().month
currentYEAR = datetime.now().year
latestYearStart = currentYEAR - 51
LAST50YEARS = [y for y in range(currentYEAR, latestYearStart, -1)]
FONT_BIG = 'Optima'
FONT_REGULAR = 'Calibri'
FONT_SMALL = 'Georgia'
FONT_REGULAR_SIZE = 14
FONT_BIG_SIZE = FONT_REGULAR_SIZE + 6
FONT_SMALL_SIZE = FONT_REGULAR_SIZE - 3
DOWNLOADS_PATH = path.join(str(Path.home()), "Downloads", "hummingbird")
SETTINGS_FILE = path.join(DOWNLOADS_PATH, r'__hb_settings.cfg')
DEFAULT_SETTINGS = {'sDIR': os.getcwd(),
                    'getFilesFromDir': True,
                    'getFiles': False,
                    'selectFilesAuto': True,
                    'selectFilesMan': False,
                    'limitFilesRetrived': 100,
                    'ignoreTheFirst': 0,
                    'startDay': 1,
                    'startMonth': 1,
                    'startYear': latestYearStart,
                    'endDay': currentDAY,
                    'endMonth': currentMONTH,
                    'endYear': currentYEAR,
                    'extn0': True,
                    'extn1': True,
                    'extn2': True,
                    'extn3': True,
                    'extn4': True,
                    'extn5': True,
                    'extn6': True,
                    'extn7': True,
                    'preference1': True,
                    'preference2': False,
                    'preference3': False,
                    'verboseComments': True,
                    'checkTitles': True,
                    'theme': 'DarkBlue12',
                    'defaultSettings1': True}
# "Map" from the settings dictionary keys to the window's element keys
SETTINGS_KEYS_TO_ELEMENT_KEYS = {'sDIR': '-FOLDER-',
                                 'selectFilesAuto': '-SELECT1-',
                                 'selectFilesMan': '-SELECT2-',
                                 'limitFilesRetrived': '-NUMBER1-',
                                 'ignoreTheFirst': '-NUMBER3-',
                                 'startDay': '-STARTING_DAY-',
                                 'startMonth': '-STARTING_MONTH-',
                                 'startYear': '-STARTING_YEAR-',
                                 'endDay': '-ENDING._DAY-',
                                 'endMonth': '-ENDING._MONTH-',
                                 'endYear': '-ENDING._YEAR-',
                                 'extn0': '-EXTN0-',
                                 'extn1': '-EXTN1-',
                                 'extn2': '-EXTN2-',
                                 'extn3': '-EXTN3-',
                                 'extn4': '-EXTN4-',
                                 'extn5': '-EXTN5-',
                                 'extn6': '-EXTN6-',
                                 'extn7': '-EXTN7-',
                                 'preference1': '-PREFERENCE1-',
                                 'preference2': '-PREFERENCE2-',
                                 'preference3': '-PREFERENCE3-',
                                 'verboseComments': '-VERBOSE0-',
                                 'checkTitles': '-CHECKTITLES0-',
                                 'theme': '-THEME-'}
PM = {('error', 'background'): 'red',
      ('error', 'text'): 'white',
      ('warning', 'background'): 'yellow',
      ('warning', 'text'): 'black',
      ('info', 'background'): 'lightblue',
      ('info', 'text'): 'black',
      ('help', 'background'): 'darkgrey',
      ('help', 'text'): 'black',
      ('special', 'background'): 'purple',
      ('special', 'text'): 'white',
      ('faq', 'background'): 'lightgrey',
      ('faq', 'text'): 'black',
      }
CATEGORIES_FILE_YMDHMS = path.join(DOWNLOADS_PATH, r'__hb_categories_YMDHMS.cfg')
DEFAULT_CATEGORIES = {'*':                  ['Life', 'Humanities', 'Natural World', 'Sciences', 'The Inexplicable'],
                      'Life':               ['Personal', 'Relationships', 'Current events', 'Connections'],
                      'Relationships':      ['Love', 'Mother', 'Father', 'Daughter', 'Son'],
                      'Love':               ['Partner', 'Other'],
                      'Humanities':         ['Art', 'Performing arts', 'Literature', 'Philosophy', 'Poetry', 'Religion',
                                             'Classics'],
                      'Performing arts':    ['Music', 'Dance', 'Drama'],
                      'Natural World':      ['Gardens', 'Trees', 'Rain', 'Landscapes', 'Places', 'Animals', 'Insects'],
                      'Animals':            ['Elephants', 'Rhinoceress'],
                      'Places':             ['Crete', 'India', 'Siri Lanka'],
                      'Sciences':           ['Astronomy', 'Physics', 'Mathematics'],
                      'The Inexplicable':   ['Surreal', 'Magic', 'Synchronicity'],
                      }
CAT_PREFIX  = '>︎ '
CAT_DELIM   = ' | '
CAT_REMOVE  = '- '
CAT_ADD     = '+ '
CAT_RENAME  = '= '


##################### Load/Save Settings & categories Files #####################

def getLatestCatFile():
    # get the latest cat files
    fileList = fnmatch.filter(os.listdir(DOWNLOADS_PATH), u'__hb_Categories_*.cfg')
    if len(fileList) == 0:
        # none found
        return '', False
    else:
        fileList.sort()
        return path.join(DOWNLOADS_PATH, fileList[-1]), True


def load_categories():
    # look for latest cat files in Downloads
    CATEGORIES_FILE, found = getLatestCatFile()
    if found:
        with open(CATEGORIES_FILE, 'r') as f:
            data = []
            for line in f:
                data.append(jsonload(line))
        categoriesCP = data[0]
        categoriesPC = data[1]
        pathH, pathT = os.path.split(CATEGORIES_FILE)
        filename, extension = os.path.splitext(pathT)
        bits = filename.split("_")
        dt = bits[-1]
        dtExpanded = u'%s-%s-%s @ %s:%s:%s' % (dt[0:2], dt[2:4], dt[4:6], dt[6:8], dt[8:10], dt[10:12])
    else:
        popupMessage('info', u'No category file found...\n'
                             u'It will be created in your Downloads sub-dir')
        t_categories = {}
        for majorCat in DEFAULT_CATEGORIES:
            for subCat in DEFAULT_CATEGORIES[majorCat]:
                t_categories[subCat] = (majorCat, 0)
        # sort subcats
        s_categories = sorted(t_categories.items(), key=operator.itemgetter(0))
        categoriesCP = collections.OrderedDict(s_categories)
        categoriesPC = DEFAULT_CATEGORIES
        dtExpanded = save_categories(categoriesCP, categoriesPC, True)
    return categoriesCP, categoriesPC, dtExpanded


def save_categories(categoriesCP, categoriesPC, newCategories):
    # save category files with current date-time suffix
    if not newCategories: return
    nowDT = datetime.now()
    dtSuffix = nowDT.strftime("%y%m%d%H%M%S")
    dtExpanded = nowDT.strftime("%y-%s-%d %H:%M:%S")
    CATEGORIES_FILE = CATEGORIES_FILE_YMDHMS.replace('YMDHMS', dtSuffix)
    with open(CATEGORIES_FILE, 'w') as f:
        jsondump(categoriesCP, f)
        f.write('\n')
        jsondump(categoriesPC, f)
    popupMessage('info',
                 u"The categories have been saved in: \n%s\nin files with the suffix '%s'" % (DOWNLOADS_PATH, dtSuffix))
    return dtExpanded


def higlightedCategory(hc):
    # check for valid highlighted category
    if hc == "":
        popupMessage('info', 'No category has been highlighted on the tree ?!')
        return False
    elif hc == "*":
        popupMessage('error', 'You cannot alter with the * (root) category !')
        return False
    else:
        return True


def updateTreeData(catPC, catCP):
    # update the tree data
    treedata = sg.TreeData()
    treedata.insert('', '*', '*', values=[])
    theParents = []
    for majorCat in catPC:
        theParents.append(majorCat)
        for subCat in catPC[majorCat]:
            mCat, count = catCP[subCat]
            if count > 0:
                treedata.insert(majorCat, subCat, subCat, values=[count])
            else:
                treedata.insert(majorCat, subCat, subCat, values=[])
    theParents.sort()
    return treedata, theParents

# ----------------------------------------------------------------------------------------------------------------------
# 5.1 Edit the categories tree
# ----------------------------------------------------------------------------------------------------------------------
def showCatTree(catPC, catCP, subCats, catUpdates, catLastUpdated):
    treeDataChanged = False
    treedata, theParents = updateTreeData(catPC, catCP)
    treeLayout = [[TextLabel('The categories tree of relationships & assignment counts', FONT_REGULAR_SIZE)],
                  [TextLabel(u'last updated: %s' % catLastUpdated, FONT_REGULAR_SIZE)],
                  [sg.Tree(data=treedata,
                           font=(FONT_REGULAR, FONT_REGULAR_SIZE),
                           auto_size_columns=True,
                           headings=['Count'],
                           num_rows=20,
                           col0_width=40,
                           key='-TREE-',
                           show_expanded=True,
                           enable_events=True),
                   ],
                  [bL()], [bL()],
                  [
                      [TextLabel('Highlight a category on the tree to:', FONT_REGULAR_SIZE)],
                      [Btn('Remove', '-REMOVE-')],
                      [TextLabel('and to:', FONT_REGULAR_SIZE), Btn('Rename', '-RENAME-'),
                       TextLabel(' or ', FONT_REGULAR_SIZE), Btn('Add', '-ADD-')],
                      [TextLabel('enter the new category:', FONT_REGULAR_SIZE),
                       sg.Input(size=(25, 1), font=(FONT_REGULAR, FONT_REGULAR_SIZE), key=("-CAT-"))]
                  ],
                  [bL()],
                  [bL()],
                  [Btn('Help', '-CAT_HELP-'), Btn('Close & save changes', '-CLOSE-')],
                  [bL()]
                  ]
    treeWindow = sg.Window(HB_UTILITY_TITLE, treeLayout)
    theHC = ''
    while True:
        event, values = treeWindow.read()
        if event in (sg.WIN_CLOSED, '-CLOSE-'):
            break
        elif event == '-CAT_HELP-':
            popupMessage('help', 'Catgegories will be (re-)initialised automatically\n'
                                 'with a file downloaded from the application.\n\n'
                                 'IMPORTANT\n'
                                 "It is your responsibility to keep this utility's\n"
                                 "and the application's categories in synch.\n\n"
                                 "The application's categories are the master\n"
                                 "reference.\n\n"
                                 'In the absence of a file a default tree will\n'
                                 'created and used. This tree will be indentical\n'
                                 'to the default category tree used by the\n'
                                 'application.\n\n'
                                 'INSTRUCTIONS\n'
                                 'First highlight a category on the tree to:\n'
                                 'RENAME, REMOVE or ADD a category.\n\n'
                                 'A category can only be removed if:\n'
                                 'it has no sub-categories\n'
                                 'and\n'
                                 'it has no titles assigned\n'
                                 'i.e. it has no associated count.\n\n'
                                 'A new category can only be ADDed as a\n'
                                 'sub-category to an existing category.\n\n'
                                 'A category can only be RENAMED to a none-\n'
                                 'extisting category.\n\n'
                                 'Category names must be unique.\n'
                                 'If you wish to add/rename a category with\n'
                                 'a name that already exists append a numerical\n'
                                 'suffix e.g. Rain_1 to make it unique.\n\n'
                                 'Changes will be automatically propogated to\n'
                                 'the application via the upload file.')
        elif event == '-TREE-':
            theHC = values['-TREE-'][0]
        elif event == '-REMOVE-' or event == '-ADD-' or event == '-RENAME-':
            nbg = remove = add = rename = False
            if event == '-REMOVE-':
                remove = True
                rca = 'remove'
            elif event == '-ADD-':
                add = True
                rca = 'add'
            else:  # renaming
                rename = True
                rca = 'rename'
            if add or rename:
                theNewSubCat = values["-CAT-"].capitalize()
                # check that there is a  new sub cat
                if theNewSubCat == None or theNewSubCat == '':
                    popupMessage('warning', u'A new category is required for %s.' % rca)
                    nbg = True
                if not nbg:
                    # does the new sub cat already exist?
                    for subCat in subCats:
                        if theNewSubCat in subCat:
                            popupMessage('info', u"The category '%s'\n you want to %s already exists!\n"
                                                 u"Suggest you add a suffix like _Number and resubmit" % (
                                         theNewSubCat, rca))
                            nbg = True
                            break
            # check there is a highlighted category
            if (add or remove) and not nbg and higlightedCategory(theHC):
                # look for highlighted cat in list of parents
                if not add:
                    if theHC in theParents:
                        popupMessage('warning', u'You cannot %s the category:\n\n'
                                                "'%s'\n\n"
                                                ' - it has one or more subCategories !' % (rca, theHC))
                        nbg = True
                if not nbg:
                    for majorCat in catPC:
                        if theHC in catPC[majorCat]:
                            majorCat, count = catCP[theHC]
                            # see if it has titles assigned
                            if count > 0:
                                popupMessage('warning', 'Uanble to %s the category\n\n'
                                                        "'%s'\n\n"
                                                        "because it has %s title%s assigned ?!" % (
                                             rca, theHC, count, pluralize(count)))
                                nbg = True
                            else:
                                if askTheQuestion(u"Confirm you want to %s the category:\n\n'%s'" % (rca, theHC)):
                                    if remove:
                                        catPC[majorCat].remove(theHC)
                                        del catCP[theHC]
                                        for subCat in subCats:
                                            if theHC in subCat:
                                                subCats.remove(subCat)
                                                catUpdates.append(u'%s%s' % (CAT_REMOVE, subCat))
                                    if add:
                                        catPC[theHC] = catPC.get(theHC, []) + [theNewSubCat]
                                        catCP[theNewSubCat] = (theHC, 0)
                                        subCats.append(theNewSubCat + ' | ' + theHC)
                                        catUpdates.append(u'%s%s' % (CAT_ADD, subCats[-1]))
                                    break
            else:  # rename
                if not nbg:
                    # is the cat to be renamed a parent?
                    if theHC in theParents:
                        theCs = catPC[theHC]
                        del catPC[theHC]
                        catPC[theNewSubCat] = theCs
                    # look for HC in Cs
                    for p in catPC:
                        if theHC in catPC[p]:
                            listofc = catPC[p]
                            listofc.remove(theHC)
                            listofc.append(theNewSubCat)
                            catPC[p] = listofc
                    pc = catCP[theHC]
                    del catCP[theHC]
                    catCP[theNewSubCat] = pc
                    for c in catCP:
                        if theHC in catCP[c]:
                            oldP, count = catCP[c]
                            catCP[c] = (theNewSubCat, count)
                    subCats = [CAT_DELIM]
                    for subCat in catCP:
                        subCats.append(u'%s | %s' % (subCat, catCP[subCat][0]))
                    catUpdates.append(u'%s%s%s%s' % (CAT_RENAME, theHC, CAT_DELIM, theNewSubCat))
            if not nbg:
                # revise the tree data & update
                revised_treedata, theParents = updateTreeData(catPC, catCP)
                treeWindow['-TREE-'].update(values=revised_treedata)
                subCats.sort()
                treeDataChanged = True
    treeWindow.close()
    if treeDataChanged:
        catLastUpdated = save_categories(catCP, catPC, True)
    return catPC, catCP, subCats, catUpdates, catLastUpdated


def load_settings(settings_file, default_settings):
    # load settings from file  - use default if unable to open file
    try:
        data = []
        with open(settings_file, 'r') as f:
            for line in f:
                data.append(jsonload(line))
        settings = data[0]
    except Exception as e:
        popupMessage('info', u'No settings file found...one will be created as:\n\n%s' % settings_file)
        settings = DEFAULT_SETTINGS
        save_settings(settings_file, settings, None)
    return settings


def save_settings(settings_file, settings, values):
    if values:  # if there are stuff specified by another window, fill in those values
        for key in SETTINGS_KEYS_TO_ELEMENT_KEYS:  # update window with the values read from settings file
            try:
                theValue = SETTINGS_KEYS_TO_ELEMENT_KEYS[key]
                if theValue == '-STARTING_MONTH-' or theValue == '-ENDING._MONTH-':
                    settings[key] = MONTHSoftheYEAR.index(values[theValue]) + 1
                elif theValue == '-STARTING_DAY-' or theValue == '-ENDING._DAY-' or \
                     theValue == '-STARTING_YEAR-' or theValue == '-ENDING._YEAR-':
                    settings[key] = int(values[theValue])
                else:
                    settings[key] = values[theValue]
            except Exception as e:
                popupMessage('warning', f'Problem updating settings from values\n with key = {key}')

    with open(settings_file, 'w') as f:
        jsondump(settings, f)

    popupMessage('info', 'The settings have been saved.')


# =========== Routines ==================================================

def pluralize(n):
    if n == 1:
        return ''
    else:
        return 's'


def is_are(n):
    if n == 1:
        return 'is'
    else:
        return 'are'


def its_their(n):
    if n == 1:
        return "it's"
    else:
        return 'their'


def itIs_theyAre(n):
    if n == 1:
        return "it is"
    else:
        return 'they are'


def has_have(n):
    if n == 1:
        return 'has'
    else:
        return 'have'


def was_were(n):
    if n == 1:
        return 'was'
    else:
        return 'were'


def checkForFiles(nf, vC):
    testForNoneFound('files', nf)
    if vC:
        popupMessage('info', u'Retrieved %s poem file%s' % (nf, pluralize(nf)))
    return


def reverseColour(hexValue):
    h = hexValue.lstrip('#')
    rgb = tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    rgbInverse = 255 - rgb[0], 255 - rgb[1], 255 - rgb[2]
    return '#{:02x}{:02x}{:02x}'.format(rgbInverse[0], rgbInverse[1], rgbInverse[2])


def datePicker(text, defaultDay=None, defaultMonth=None, defaultYear=None):  # nb calendar does NOT work on MAC
    key = text.upper()
    dayKey = u'-%s_DAY-' % key
    monthKey = u'-%s_MONTH-' % key
    yearKey = u'-%s_YEAR-' % key
    if defaultDay == None: defaultDay = currentDAY
    if defaultMonth == None: defaultMonth = currentMONTH
    defaultMonth -= 1
    if defaultYear == None: defaultYear = currentYEAR
    return [TextColourLabel(text),
            sg.InputCombo(values=DAYSoftheMONTH, font=(FONT_REGULAR, FONT_REGULAR_SIZE), size=(5, 10), key=dayKey,
                          default_value=defaultDay),
            sg.InputCombo(values=MONTHSoftheYEAR, font=(FONT_REGULAR, FONT_REGULAR_SIZE), size=(5, 10), key=monthKey,
                          default_value=MONTHSoftheYEAR[defaultMonth]),
            sg.InputCombo(values=LAST50YEARS, font=(FONT_REGULAR, FONT_REGULAR_SIZE), size=(5, 10), key=yearKey,
                          default_value=defaultYear)]


def isValidDate(day, month, year):
    try:
        newDate = datetime(year, month, day)
        if newDate <= datetime.now():
            return True
    except ValueError:
        pass
    return False


def popupMessage(type, msg):
    sg.popup(msg, title=u'%s - %s' % (HB_UTILITY_TITLE, type), keep_on_top=True, line_width=80,
             background_color=PM[(type, 'background')], text_color=PM[(type, 'text')],
             font=(FONT_REGULAR, FONT_REGULAR_SIZE))


def askTheQuestion(question):
    layout = [
        [bL()],
        [sg.T(question)],
        [bL()],
        [sg.B('Yes', button_color=(boldColourFg(), boldColourBg())), sg.B('No')]
    ]
    event, values = sg.Window('Please respond to the question ...', layout, size=(450, 180), keep_on_top=True,
                              font=(FONT_REGULAR, FONT_REGULAR_SIZE)).read(close=True)
    if event == "Yes" or event == sg.WIN_CLOSED:
        return True
    else:
        return False


def Quitting(event, msg=''):
    if event == '-QUITTING-' or event == sg.WIN_CLOSED:
        msgq = u'%s\n\nAre you sure you want to quit ?' % msg
        return askTheQuestion(msgq)
    else:
        return False


def TextLabel(text, size=None, theKey=None):
    if size == None:
        theSize = FONT_REGULAR_SIZE
    else:
        theSize = size
    if theKey == None:
        return sg.Text(text, font=(FONT_REGULAR, theSize))
    else:
        return sg.Text(text, size=(10 + len(text), 1), font=(FONT_REGULAR, theSize), key=(u'%s' % theKey.upper()))


def theTextTitle(text):
    u = ''
    lu = '_' * 80
    lt = len(text)
    if lt < 85:
        u = lu[:80 - lt]
    return sg.Text(u'%s %s' % (text, u), font=(FONT_BIG, FONT_BIG_SIZE), key='-TITLE-')


def boldColourBg():
    return reverseColour(sg.theme_background_color())


def boldColourFg():
    return reverseColour(sg.theme_text_color())


def boldColours():
    return boldColourFg(), boldColourBg()


def TextColourLabel(text, theKey=None):
    if theKey == None:
        return sg.Text(text, font=(FONT_REGULAR, FONT_REGULAR_SIZE), text_color=(boldColourBg()))
    else:
        return sg.Text(text, key=(u'-%s-' % theKey.upper()), font=(FONT_REGULAR, FONT_REGULAR_SIZE),
                       text_color=(boldColourBg()))


def Cb(text, key, number, theDefault=False):
    return sg.Checkbox(text, key=(u'-%s%s-' % (key, number)), font=(FONT_REGULAR, FONT_REGULAR_SIZE),
                       default=theDefault, enable_events=True, text_color=(boldColourBg()))


def Rb(text, groupKey, number, theDefault): return sg.Radio(text, groupKey, default=theDefault,
                                                            font=(FONT_REGULAR, FONT_REGULAR_SIZE),
                                                            key=(u'-%s%s-' % (groupKey.upper(), number)))


def bL(): return sg.Text(' ')


def Btn(text, theKey=None, isVisible=True, highlight=False):
    if theKey == None:
        k = u'-%s-' % text.upper()
    else:
        k = u'%s' % theKey.upper()
    if highlight:
        return sg.Button(text, key=k, visible=isVisible, font=(FONT_REGULAR, FONT_REGULAR_SIZE),
                         button_color=(boldColours()))
    else:
        return sg.Button(text, key=k, visible=isVisible, font=(FONT_REGULAR, FONT_REGULAR_SIZE))


def endswithNumber(string):
    m = re.search(r'\d+$', string)
    if m is not None:
        return True
    else:
        return False


def endswithText(string, theTexts):
    for text in theTexts:
        if string.endswith(text):
            return True
    return False


def startswithText(string, theTexts):
    for text in theTexts:
        if string.startswith(text):
            return True
    return False


def is_date(string, fuzzy=False):
    try:
        parse(string, fuzzy=fuzzy)
        return True
    except ValueError:
        return False


def generateUniqueUploadFileNameWithDesktopPath():
    # generate upload filename with yearMonthDayHourMinSec suffix to ensure uniqueness
    nowDT = datetime.now()
    hbUploadFilename = HB_UPLOADFILE_NAME_PREFIX + nowDT.strftime("%y%m%d%H%M%S") + '.txt'
    uploadFile = os.path.join(os.path.normpath(os.path.expanduser("~" + os.path.sep + "Desktop")),
                              hbUploadFilename)
    return uploadFile


def getHbGptUploadTitles():
    # build a dictionary of titles from the current upload files on the desktop
    desktopPath = os.path.normpath(os.path.expanduser("~" + os.path.sep + "Desktop"))
    allFiles = [f for f in listdir(desktopPath) if isfile(join(desktopPath, f))]
    gptUploadFiles = []
    for f in allFiles:
        if HB_UPLOADFILE_NAME_PREFIX in f:
            gptUploadFiles.append(f)
    if len(gptUploadFiles) == 0: return None
    prefoundTitles = []
    for f in gptUploadFiles:
        with open(os.path.join(desktopPath, f)) as ff:
            lines = ff.readlines()
            for line in lines:
                if '...' != line[0:3]:
                    prefoundTitles.append(line[:-1])  # drop the \n  suffix
    return dict.fromkeys(prefoundTitles, 'title')


def testForNoneFound(type1, NoOf1, type2=None, NoOf2=None):
    if type2 == None:
        if NoOf1 == 0:
            popupMessage('warning', 'Terminating the utility !\n\nNo %s have been found ?!' % type1)
            sys.exit()
    else:
        msg = ''
        if NoOf1 == 0: msg += u'No %s have been found ?!\n' % type1
        if NoOf2 == 0: msg += u'No %s have been updated ?!\n' % type2
        if msg != '':
            popupMessage('info', msg)
            if NoOf1 == 0 and NoOf2 == 0:
                popupMessage('warning', 'Terminating the utility !')
                sys.exit()
    return


def writeTamperProofUploadFile(theLines, theFile):
    # writes tamper proof upload file to the desktop
    # file is protected by having a filehash suffix
    # computed AFTER having appended the filename
    # and then re-written with the hash in place
    # of the filename.
    # Returns True if all OK else False
    #
    # This is the complement to the routine:
    # validateAndReadTamperProofUploadFile
    # in core.generalSupportRoutines

    try:
        # get desktop file path
        uploadFilePath = os.path.join(os.path.normpath(os.path.expanduser("~" + os.path.sep + "Desktop")), theFile)
        # append filename to lines
        theLines.append(theFile)
        # write lines to file
        with open(uploadFilePath, "w") as uf:
            uf.write('\n'.join(theLines))
        # compute sha256 file hash
        sha256hasher = FileHash('sha256')
        fileHash = sha256hasher.hash_file(uploadFilePath)
        # remove the filename from the lines
        del theLines[-1]
        # append hash
        theLines.append(fileHash)
        # 're-write file by overwriting
        with open(uploadFilePath, "w") as uf:
            uf.write('\n'.join(theLines))
        # make the file read-only
        os.chmod(uploadFilePath, S_IREAD)
        return True
    except:
        return False

########################################################################################################################
########################################################################################################################

def main():
    # -------- set whats done flags -------#
    settingsChanged = False
    filesRetrieved = False
    titlesExtracted = False
    titlesReviewed = False
    newCategories = False
    filterMsg = ''
    catUpdates = []
    theTitles = []

    # -------- process flags -------#
    processingTitles = False
    processingCategories = False

    # -------- set titles found -------#
    theFinalNoOfTitles = 0

    # --------get platform info  -------#

    is_Linux = sg.running_linux()
    is_Mac = sg.running_mac()
    is_Windows = sg.running_windows()

    # --------initialise window theme -------#

    window = None
    sg.DEFAULT_FONT = (FONT_REGULAR, FONT_REGULAR_SIZE)

    # ------ get control settings from default or file into variables -------#

    settings = load_settings(SETTINGS_FILE, DEFAULT_SETTINGS)

    sDIR = settings['sDIR']
    selectFilesAuto = settings['selectFilesAuto']
    selectFilesMan = settings['selectFilesMan']
    limitFilesRetrived = settings['limitFilesRetrived']
    ignoreTheFirst = settings['ignoreTheFirst']
    startingDay = settings['startDay']
    startingMonth = settings['startMonth']
    startingYear = settings['startYear']
    startingDate = datetime(startingYear, startingMonth, startingDay).date()
    endingDay = settings['endDay']
    endingMonth = settings['endMonth']
    endingYear = settings['endYear']
    endingDate = datetime(endingYear, endingMonth, endingDay).date()
    extnsList = []
    listExtns = ''
    for e in range(8):
        extnKey = u'extn%s' % e
        if settings[extnKey]:
            extnsList.append(EXTNS[e])
            listExtns += u' *%s' % EXTNS[e]
    if settings['preference1']: preference = 1
    if settings['preference2']: preference = 2
    if settings['preference3']: preference = 3
    verboseComments = settings['verboseComments']
    checkTitles = settings['checkTitles']
    theTheme = settings['theme']
    sg.theme(theTheme)
    defaultSettings = settings['defaultSettings1']
    # -----------------------------------------------------------------------------------------------------------------------
    # Splash screen
    # -----------------------------------------------------------------------------------------------------------------------
    #     if is_Windows: sg.Window(HB_UTILITY_TITLE, [[sg.Image(filename=DISPLAY_FILENAME)]], transparent_color=sg.theme_background_color(),
    #                    no_titlebar=True,keep_on_top=True).read(timeout=DISPLAY_TIME_MILLISECONDS, close=True)
    # -----------------------------------------------------------------------------------------------------------------------
    # Welcome window
    # -----------------------------------------------------------------------------------------------------------------------

    layout = [
        [theTextTitle('Welcome')],
        [bL()],
        [TextLabel('This utility recovers poem titles ')],
        [TextLabel('into an application upload file.')],
        [bL()],
        [TextLabel('There are 6 steps to follow in order:')],
        [bL()],
        [TextLabel('1. Review, revise and update the default settings')],
        [TextLabel('2. Get the files')],
        [TextLabel('3. Filter the files and extract the titles')],
        [TextLabel('4. Review the titles, removing any that are unwanted')],
        [TextLabel('5. Categorize titles   (& optionally ▶︎)')],
        [TextLabel('6. Create the upload file')],
        [bL()],
        [TextLabel('▶ The utility can be used just to update and')],
        [TextLabel('  synch the category tree with the application.')],
        [bL()],
        [Btn("Next", '-NEXT-', True, True), Btn("▶ Category tree", '-CAT-TREE-'), Btn("About", '-ABOUT-'),
         Btn("FAQs", "-FAQ-"), Btn("Quit", '-QUITTING-')]
    ]
    window = sg.Window(HB_UTILITY_TITLE, layout, size=(450, 540), keep_on_top=True)

    while True:
        event, values = window.read()
        if Quitting(event):
            return
        if event == '-ABOUT-':
            popupMessage('info', u'This hummingbird utility is %s' % VERSION)
        if event == '-NEXT-':
            processingTitles = True
            break
        if event == '-CAT-TREE-':
            processingCategories = True
            break
        if event == "-FAQ-":
            popupMessage('FAQ', '\nQ: Why should I use this utility? '
                                '\nA: It will save you the labour of entering your poem titles by hand'
                                '\n   and it can check that the poem title is the same as the filename;'
                                '\n   in addition you can optionally categorise your poems.\n'
                                '\nQ: Do HAVE to use this utility?'
                                '\nA: No, you can enter all your poem titles manually into the'
                                '\n   application and do thier categorizations there as well.\n'
                                "\nQ: If I don't know what to do - how do I get help?"
                                '\nA: Click on the HELP button.\n'
                                "\nQ: If I made a mistake and want to abandon the utility - what do I do?"
                                "\nA: Click on the QUIT button - you'll have to confirm your decision.\n"
                                '\nQ: Does the utility require lots of input/decsions? '
                                '\nA: No - it will harvest the poem titles automatically'
                                '\n   once you tell it which sub-dir to use.\n'
                                '\nQ: Can I use pre-selection crieria on my files?'
                                '\nA: Yes - there are 7 selection criteria you can employ'
                                '\n   or you can rely on the default settings.\n'
                                '\nQ  Does it only find poem titles?'
                                '\nA: No - you can optionally use it to maintain your categories'
                                '\n   in synch with the application.\n'
                                '\nQ: How do my poem titles & category updates get into the application?'
                                '\nA: The utility creates an file of titles and category'
                                '\n   changes which is uploaded & read by the application.\n'
                                "\nQ: I don't like the utility's theme colours - what can I do?"
                                "\nA: At the bottom of the selections there's a drop-down menu"
                                '\n   with a choice of 100+ themes\n'
                                "\nQ: I can't seem to be able to do X and/or I don't understand"
                                '\n   Y this is happening -  what do I do?'
                                "\nA: Use the application's CONTACT facility and email us"
                                "\n   your question. We'll get back to you promptly with a reply."
                         )

    window.close()

    # -------begin processing categories--------------------
    if processingCategories:
        catUpdates = []
        categoriesCP, categoriesPC, catLastUpdated = load_categories()
        subCats = [CAT_DELIM]
        nCategorized = 0
        for subCat in categoriesCP:
            subCats.append(u'%s | %s' % (subCat, categoriesCP[subCat][0]))
        categoriesPC, categoriesCP, subCats, catUpdates, catLastUpdated = showCatTree(categoriesPC, categoriesCP,
                                                                                      subCats,
                                                                                      catUpdates, catLastUpdated)
    if processingTitles:
        # -------begin processing titles--------------------

        # -----------------------------------------------------------------------------------------------------------------------
        # 1. REVISE SETTINGS
        # -----------------------------------------------------------------------------------------------------------------------

        settingsChanged = False
        sg.theme(theTheme)
        nextButton = Btn('Next', '-NEXT-', defaultSettings, defaultSettings)
        updateButton = Btn("Update & save", '-UPDATE-', not defaultSettings, defaultSettings)
        now = datetime.now()

        layout = [[theTextTitle('1. Review, revise and update the default settings')],
                  [bL()],
                  [TextColourLabel('Choose a folder for the poem title files selection')],
                  [sg.Input(sDIR, key="-FOLDER-", size=(60, 1), font=(FONT_REGULAR, FONT_REGULAR_SIZE)),
                   sg.FolderBrowse()],
                  [bL()],
                  [Cb('Use the default settings without review & revision', 'DEFAULTSETTINGS', 1, defaultSettings)],
                  [bL()],
                  [updateButton, nextButton, Btn('Help', '-HELP_REVISE_SETTINGS-'), Btn("Quit", '-QUITTING-')],
                  [bL()],
                  [sg.Frame(layout=[
                      [bL()],
                      [TextColourLabel('Have the files selected by:'),
                       Rb('automatically retrieving▲︎︎︎', 'select', 1, selectFilesAuto),
                       Rb('manually browsing', 'select', 2, selectFilesMan)],
                      [bL()],
                      [TextColourLabel('Limit the number of files to a maximum of: '),
                       sg.InputCombo(values=NUMBERS1, font=(FONT_REGULAR, FONT_REGULAR_SIZE), size=(5, 10),
                                     key=("-NUMBER1-"),
                                     default_value=limitFilesRetrived),
                       TextColourLabel('ignoring the first: '),
                       sg.InputCombo(values=NUMBERS1, font=(FONT_REGULAR, FONT_REGULAR_SIZE), size=(5, 10),
                                     key=("-NUMBER3-"),
                                     default_value=ignoreTheFirst)
                       ],
                      [bL()],
                      [TextColourLabel('within the period: ')],
                      datePicker('starting', startingDay, startingMonth, startingYear),
                      datePicker('ending.', endingDay, endingMonth, endingYear),
                      [bL()],
                      [TextColourLabel('with extensions:')],
                      [Cb('*.txt',      "EXTN", 0, settings['extn0']),
                       Cb('*.rtf',      "EXTN", 1, settings['extn1']),
                       Cb('*.rtfd▼︎',    "EXTN", 2, settings['extn2']),
                       Cb('*.pdf',      "EXTN", 3, settings['extn3']),
                       Cb('*.docx',     "EXTN", 4, settings['extn4']),
                       Cb('*.doc',      "EXTN", 5, settings['extn5']),
                       Cb('*.odt',      "EXTN", 6, settings['extn6']),
                       Cb('*.pages▼︎︎',  "EXTN", 7, settings['extn7'])],
                      [bL()],
                      [TextColourLabel('Taking the title from the:'),
                       Rb('Filename', 'preference', 1, settings['preference1']),
                       Rb('Document', 'preference', 2, settings['preference2']),
                       Rb('or Resolve if they are different', 'preference', 3, settings['preference3'])],
                      [bL()],
                      [Cb('check titles with waiting uploads', "CHECKTITLES", 0, checkTitles)],
                      [Cb('provide verbose information.', "VERBOSE", 0, verboseComments)],
                      [bL()],
                      [sg.Text('▲︎︎︎︎︎ will include the files in sub-dirs recursively',
                               font=(FONT_SMALL, FONT_SMALL_SIZE))],
                      [sg.Text('▼︎ these document types are not readable - titles default to filenames',
                               font=(FONT_SMALL, FONT_SMALL_SIZE))],
                      [bL()],
                      [TextLabel('Theme'),
                       sg.InputCombo(values=sg.theme_list(), size=(20, 20), key='-THEME-', default_value=theTheme,
                                     font=(FONT_REGULAR, FONT_REGULAR_SIZE))],
                      [bL()],
                  ],
                      title='Settings', title_color=boldColourBg(), font=(FONT_REGULAR, FONT_REGULAR_SIZE),
                      visible=not defaultSettings,
                      key='-FRAME-', relief=sg.RELIEF_SUNKEN)],
                  # [bL()],
                  # [bL()],
                  # [updateButton, nextButton, Btn('Help', '-HELP_REVISE_SETTINGS-'), Btn("Quit", '-QUITTING-')]
                  ]
        if defaultSettings:
            thelength = 280
        else:
            thelength = 900
        window = sg.Window(HB_UTILITY_TITLE, layout, size=(670, thelength), finalize=True, resizable=True)

        while True:

            event, values = window.read()

            if Quitting(event, "If not UPDATED you will loose any changed settings."):
                return

            elif event == '-HELP_REVISE_SETTINGS-':
                popupMessage('help', '\n\nThese settings control the selection of the poem files and titles.\n\n'
                                     'On initial execution a saved settings file will be automatically created\n'
                                     'using the default values. Any subsequent change requires an update and save.\n\n '
                                     'Changing any of the settings is optional.\n'
                                     'You can make use of any or all of the defaults if they are appropriate.\n\n'
                                     'By default the current working folder will be used to source the poem files.\n'
                                     'This can be changed by using the BROWSE button. You will be taken to your\n'
                                     'file directories from there you can navigate to your chosen folder.\n\n'
                                     'There is a choice of having the files selected automatically or manually.\n'
                                     "If the default, automatic, option is chosen the folder and it's sub-directories,\n"
                                     "and their sub-directories and so on recursively, will be used to source files.\n\n"
                                     "If the manual option is chosen you must select individual or groups of files\n"
                                     "from within the chosen folder.\n\n"
                                     "You can limit the number of files selected to between 10 & 1000.\n"
                                     "You can nominate to have the first of a specific number of files ignored;\n"
                                     "useful if you are retrieving files automatically in batches.\n\n"
                                     "You can specify a bounded time period for filtering using an inclusive\n"
                                     "starting(defaults to 50 years ago) and ending (defaults to today) dates.\n"
                                     "for the files' DLM (date last modified). E.g. with starting date 1-Jan-2019\n"
                                     "and an ending date of 31-Jul-2019 means that to be included in the selection\n"
                                     "a file's DLM must have been during the first 7 months of 2019.\n\n"
                                     "Files can be filtered by any or all of the extension types. N.B. not all types\n"
                                     "can be opened and inspected for their titles. For these types the filename is used\n"
                                     "as the subsitute for the poem title.\n\n"
                                     "Poem titles can be optiionally recovered from either: (1) their filenames,\n"
                                     "(2) the file document, the first line is assumed to be the title,\n"
                                     "or if these two are in conflict, you can elect to (3) arbitrate.\n"
                                     "With this latter preference, in exception, if neither filename nor title\n"
                                     "is acceptable you may provide an alternative.\n\n"
                                     "By default titles will be checked against those in waiting upload files;\n"
                                     "if present they will be excluded from the review and current upload."
                                     "By default you will recieve verbose information as the process proceeds.\n"
                                     "If this checkbox is unticked only brief information is proviided.\n\n"
                                     "The user interface colour scheme can be changed using the drop dowm menu.\n\n"
                                     "Settings must be confirmed with the UPDATE button to be effective,\n"
                                     "*** even if no changes have been made. ***\n\n"
                                     "You may make multiple changes and UPDATEs before using\n\n"
                                     "NEXT (which will only become visible after the UPDATE button is used for\n"
                                     "first time) which will take you on to the next step 2. in the process.\n\n"
                                     "QUIT will terminate the utility.\n\n"
                             )
            elif event == '-DEFAULTSETTINGS1-':
                defaultSettings = values['-DEFAULTSETTINGS1-']
                settings['defaultSettings1'] = defaultSettings
                settingsChanged = True
                if defaultSettings:
                    thelength = 280
                else:
                    thelength = 900
                    window['-UPDATE-'].update(visible=True, button_color=boldColours())
                    window['-NEXT-'].update(button_color=boldColours())
                window['-FRAME-'].update(visible=not defaultSettings)
                window.size = (670, thelength)
            elif event == '-UPDATE-':
                msg = ''
                filterMsg = 'Filtered from:\n'
                # collect changed settings & update variables
                canUpdateSettings = True
                # double check dir because could've typed it in
                new_sDIR = values["-FOLDER-"]
                if new_sDIR == None:
                    sDIR = os.getcwd()
                elif not os.path.isdir(new_sDIR):
                    popupMessage('warning',
                                 u'[ %s ] (sub)directory does not exist ?! %s' % (new_sDIR, SETTINGS_NOT_UPDATED))
                    canUpdateSettings = False
                else:
                    if sDIR != new_sDIR:
                        sDIR = new_sDIR
                        settingsChanged = True
                filterMsg += u'%s\n' % sDIR
                if values['-SELECT1-']:
                    selectFilesAuto = True
                    selectFilesMan = False
                filterMsg += 'with the files selected automatically\n'
                if values['-SELECT2-']:
                    selectFilesAuto = False
                    selectFilesMan = True
                    filterMsg += 'with the files selected manually\n'
                    settingsChanged = True
                if limitFilesRetrived != values['-NUMBER1-']:
                    limitFilesRetrived = values['-NUMBER1-']
                    filterMsg += u'limited to %s files' % limitFilesRetrived
                    settingsChanged = True
                if ignoreTheFirst != values['-NUMBER3-']:
                    ignoreTheFirst = values['-NUMBER3-']
                    filterMsg += u' & ignoring the first %s\n' % ignoreTheFirst
                if ignoreTheFirst > limitFilesRetrived:
                    popupMessage('warning', "Can't ignore more (%s) files than the limit (%s)" % (
                    ignoreTheFirst, limitFilesRetrived))
                    canUpdateSettings = False

                sd = int(values['-STARTING_DAY-'])
                sm = MONTHSoftheYEAR.index(values['-STARTING_MONTH-']) + 1
                sy = int(values['-STARTING_YEAR-'])
                if isValidDate(sd, sm, sy):
                    startingDate = datetime(sy, sm, sd).date()
                else:
                    popupMessage('warning', u'%s-%s-%s is not a valid starting date !' % (sd, sm, sy))
                    canUpdateSettings = False

                ed = int(values['-ENDING._DAY-'])
                em = MONTHSoftheYEAR.index(values['-ENDING._MONTH-']) + 1
                ey = int(values['-ENDING._YEAR-'])
                if isValidDate(ed, em, ey):
                    endingDate = datetime(ey, em, ed).date()
                else:
                    popupMessage('warning', u'%s-%s-%s is not a valid ending date !' % (ed, em, ey))
                    canUpdateSettings = False

                if startingDate > endingDate:
                    popupMessage('warning', u'starting date is after ending  date ?!')
                    canUpdateSettings = False

                filterMsg += u'\nwithin the period of: %s - %s\n' % (startingDate, endingDate)
                settingsChanged = True

                extnsList = []
                listExtns = ''
                for e in range(8):
                    extnKey = u'-EXTN%s-' % e
                    if values[extnKey]:
                        extnsList.append(EXTNS[e])
                        listExtns += u' %s' % EXTNS[e]
                if listExtns == '':
                    canUpdateSettings = False
                    popupMessage('warning',
                                 u'Poem files MUST be filtered by at least one extension type. %s' % SETTINGS_NOT_UPDATED)
                filterMsg += u'restricting to the extension%s: \n %s\ntaking the titles from the\n' % (
                pluralize(len(extnsList)), listExtns)
                if not values['-PREFERENCE1-']:
                    settingsChanged = True
                if values['-PREFERENCE1-']:
                    preference = 1
                    filterMsg += 'filenames'
                if values['-PREFERENCE2-']:
                    preference = 2
                    vt = 'Document titles will not be used'
                    settingsChanged = True
                    filterMsg += 'first line of the documents'
                if values['-PREFERENCE3-']:
                    preference = 3
                    vt = 'Filenames and document titles will not be compared'
                    settingsChanged = True
                    filterMsg += 'resolving differences between filename & document titles'
                # check options
                if preference >= 2:
                    nvEs = []
                    for nvE in nvEXTNS:
                        if nvE in extnsList:
                            nvEs.append(nvE)
                    if len(nvEs) != 0:
                        popupMessage('warning',
                                     u'%s for files with extensions: %s.\n\nFilenames will be used for titles.' % (
                                     vt, nvEs))
                if verboseComments != values['-VERBOSE0-']:
                    verboseComments = values['-VERBOSE0-']
                    settingsChanged = True
                if values['-THEME-'] is not None:
                    if theTheme != values['-THEME-']:
                        settings['theme'] = values['-THEME-']
                        theTheme = values['-THEME-']
                if settingsChanged:
                    if canUpdateSettings == False: msg += '\nNo settings will be updated until errors are corrected! '
                else:
                    msg = 'No update - no settings changed or saved ?!'
                if (verboseComments or not canUpdateSettings) and msg != '':   popupMessage('info', msg)
                if canUpdateSettings: save_settings(SETTINGS_FILE, settings, values)
                # updateButton.update(visible=False) = allow muliple updates
                nextButton.update(visible=True, button_color=(boldColours()))
                updateButton(
                    button_color=(reverseColour(sg.theme_background_color()), reverseColour(sg.theme_text_color())))

            elif event == '-NEXT-':
                break

        window.close()

# ----------------------------------------------------------------------------------------------------------------------
# 2. Get the files either by Retriving or Browsing
# ----------------------------------------------------------------------------------------------------------------------

        sg.theme(theTheme)
        nextButton = Btn('Next', '-NEXT-', False)

        if selectFilesAuto:
            retrieveMsg1 = "Poem files will be automatically retrieved from the directory:"
            retrieveMsg2 = "including those from sub-directories - recursivly."
            rbButton = Btn("Retrieve", '-RETRIEVE-', True, True)
            helpMsg = '\n\nFiles will be automatically RETRIEVEd from the source folder.\n'
            action = 'RETRIEVE'

        if selectFilesMan:
            retrieveMsg1 = "Browse and select poem files from the directory:"
            retrieveMsg2 = u"\nYou can select:\n\n" \
                           "o individual files by clicking on them,\n\n" \
                           "o groups of consecutive files by highlighting,\n\n" \
                           "  the first & then [SHIFT]+clicking on the last\n\n" \
                           "o any combination and/or repetition of the above."
            helpMsg = "\n\nYou must BROWSE and select files from the folder.\n\n" \
                      "Don't be concerened about inadvertently selecting\n" \
                      "inappropriate/none-text files - they will be automatically\n" \
                      "excluded at the next step as will versioned filenames.\n" \
                      "E.g.  names like: 'this is a poem_v7' or 'daffodils no.4'\n" \
                      "As will filenames with: 'backup','copy','revised','revision'\n" \
                      "'duplicate' or 'comment'.\n"
            action = 'BROWSE'
            rbButton = (sg.Input(key='-BROWSE-', visible=False, enable_events=True),
                        sg.FilesBrowse(target='-BROWSE-', font=(FONT_REGULAR, FONT_REGULAR_SIZE), initial_folder=sDIR,
                                       key='-BROWSER-', button_color=(boldColours())))

        layout = [[theTextTitle('2. Get the files')],
                  [bL()],
                  [TextLabel(retrieveMsg1, FONT_REGULAR_SIZE, '-TEXT_LABEL_1-')],
                  [TextColourLabel(sDIR)],
                  [TextLabel(retrieveMsg2, FONT_REGULAR_SIZE, '-TEXT_LABEL_2-')],
                  [bL()],
                  [bL()],
                  [rbButton, nextButton, Btn('Help', '-HELP_RETRIEVE_SETTINGS-'), Btn("Quit", '-QUITTING-')]
                  ]
        window = sg.Window(HB_UTILITY_TITLE, layout, size=(500, 250))
        retrievedFiles = False
        filteredFiles = False
        while True:

            event, values = window.read()

            if Quitting(event):
                return

            elif event == '-HELP_RETRIEVE_SETTINGS-':
                helpMsg += u"%s must be performed before moving onto the next step.\n\n" \
                           u"The NEXT button (which will become visible once the\n" \
                           u"%s has been done) will take you on to the next step 3.\n" \
                           u"in the process.\n\n" \
                           u"QUIT will terminate the utility.\n\n" % (action, action)
                popupMessage('help', helpMsg)

            elif event == '-RETRIEVE-':
                if retrievedFiles:
                    popupMessage('warning', 'Already retrieved the files !?')
                    continue
                theFiles1 = []
                nf = 0
                # r=root, d=directories, f = files
                for r, d, f in os.walk(sDIR):
                    for afile in f:
                        if nf == limitFilesRetrived: break
                        fname, extn = os.path.splitext(afile)  # get filename
                        if extn in extnsList:
                            nf += 1
                            if nf > ignoreTheFirst: theFiles1.append((r, fname, extn))
                filesRetrieved = True
                checkForFiles(nf, verboseComments)
                rbButton.update(visible=False)
                nextButton(visible=True, button_color=(boldColours()))
                window['-TITLE-'].update(u'2. Got %s file%s from:' % (nf, pluralize(nf)))
                window['-TEXT_LABEL_1-'].update(visible=False)
                window['-TEXT_LABEL_2-'].update(visible=False)

            elif event == '-BROWSE-':
                theFiles = values['-BROWSE-'].split(';')
                if len(theFiles) > 0:
                    theFiles1 = []
                    nf = 0
                    for f in theFiles:
                        if nf == limitFilesRetrived: break
                        fWithExtn = os.path.basename(f)
                        fName, fExtn = os.path.splitext(fWithExtn)
                        if fExtn in extnsList:
                            nf += 1
                            if nf > ignoreTheFirst: theFiles1.append((os.path.dirname(f), fName, fExtn))
                    filesRetrieved = True
                    checkForFiles()
                window['-BROWSER-'].update(visible=False)
                window['-NEXT-'].update(visible=True, button_color=(boldColours()))
                window['-TITLE-'].update(u'2. Got %s file%s from:' % (nf, pluralize(nf)))
                window['-TEXT_LABEL_1-'].update(visible=False)
                window['-TEXT_LABEL_2-'].update(visible=False)
            elif event == '-NEXT-':
                break

        window.close()

# -----------------------------------------------------------------------------------------------------------------------
# 3. FILTER
# -----------------------------------------------------------------------------------------------------------------------
        testForNoneFound('files', len(theFiles1))
        filterButton = Btn('Filter & extract', '-FILTER-', True, True)
        nextButton = Btn('Next', '-NEXT-', False)
        numberofTitles = 0
        layout0 = [
            [theTextTitle('3. Filter the %s file%s and extract their title%s' % (nf, pluralize(nf), pluralize(nf)))],
            [bL()],
            [bL()],
            [bL()],
            [bL()],
            [filterButton, nextButton, Btn('Help', '-HELP_FILTER-'), Btn("Quit", '-QUITTING-')]
            ]

        window0 = sg.Window(HB_UTILITY_TITLE, layout0, size=(500, 220))
        FilteredFiles = False
        while True:

            event, values = window0.read()

            if Quitting(event, "You will loose any files retrieved."):
                return

            elif event == '-HELP_FILTER-':
                popupMessage('help', '\n\nFltering & title extraction must be performed before the next step.\n\n'
                                     'Files will be filtered using the settings.\n'
                                     "Any duplicate titles, left from either suffixes from filenames e.g.'_v7',\n"
                                     "'no.4' or recovered from examining document titles, will be ignored.\n\n"
                                     " If a filename has any of the pre/suf-fixes: 'backup', copy','revised',\n"
                                     " 'revision', 'duplicate', 'comment' it will be ignored.\n\n"
                                     "The target of filtering & extraction is to produce a unique set of titles.\n"
                                     "Note however that similar titles are likely to be included.\n\n"
                                     "The NEXT button (which will become visible once filtering has\n"
                                     "been done) will take you on to the next step 4. in the process.\n\n"
                                     "QUIT will terminate the utility.\n\n")
            elif event == '-FILTER-':
                # initial filter on extn, and DLM period window
                theTitles = []
                default2Filename = ''
                numberofdefault2Filename = 0
                noOfFilesToFilter = len(theFiles1)
                nf2f = 0
                for f in theFiles1:
                    nf2f += 1
                    msg = ''
                    fname = f[1].lower()
                    extn = f[2]
                    # double check for valid extension
                    if f[2] not in extnsList: continue
                    # check if within period window
                    # Get file's Last modification time stamp in terms of seconds since epoch
                    f012 = os.path.join(f[0], fname) + extn
                    try:
                        modTimesinceEpoc = os.path.getmtime(f012)
                    except:
                        popupMessage('error', u'Abandoning file: %s\nunable to get DLM ?!' % (f012))
                        continue
                    # get file's DLM &  check within period wiindow
                    theFileDLM = datetime.fromtimestamp(modTimesinceEpoc).date()
                    if theFileDLM < startingDate or theFileDLM > endingDate: continue
                    # get title from filename NB will alyas need this even for preference 2 for default
                    firstChar = fname[:1]
                    if startswithText(fname,
                                      searchWORDS) or firstChar.isdigit() or firstChar == '.' or firstChar == "'" or firstChar == "_": continue
                    for dlim in delims:
                        if dlim in fname:
                            bits = fname.split(dlim)
                            lastBit = bits[-1]
                            if lastBit == '':
                                del bits[-1]
                            elif dlim == '_' and lastBit[0] == 'v':
                                del bits[-1]
                            elif endswithNumber(lastBit) or endswithText(lastBit, searchWORDS):
                                del bits[-1]
                            elif is_date(lastBit):
                                del bits[-1]
                            fname = dlim.join(bits)
                        else:
                            if fname[-2:].isnumeric():
                                fname = fname[:-2]
                            if fname[-1:].isnumeric():
                                fname = fname[:-1]
                            if fname[-1:] == 'v' or fname[-1:] == '_' or fname[-1:] == '-':
                                fname = fname[:-1]
                    newTitleFromFilename = fname.strip().capitalize()
                    # proceed depending on preference
                    if preference == 1:
                        newTitle = newTitleFromFilename
                    # get title from the document 2 & 3 preferences
                    else:
                        defaultToFileName = False
                        msg = ''
                        if extn in getTextFromEXTNS:
                            the1stLine = ''
                            # check file is readable
                            try:
                                f = open(f012, 'r')
                            except Exception as e:
                                defaultToFileName = True
                            if not f.readable():
                                defaultToFileName = True
                            f.close()
                            # get the text
                            if not defaultToFileName:
                                try:
                                    text = textract.process(f012, encoding='ascii')
                                    theText = text.decode("utf-8")
                                except:
                                    defaultToFileName = True
                            # extract title from text
                            if not defaultToFileName:
                                lines = theText.split('\n')
                                the1stLine = ''
                                for line in lines:
                                    the1stLine = line.strip()
                                    if the1stLine != '':
                                        theTitle = the1stLine
                                        break
                                if the1stLine == '':
                                    defaultToFileName = True
                        else:
                            defaultToFileName = True
                        if not defaultToFileName:
                            if preference == 2:
                                newTitle = theTitle
                            else:  # preference 3
                                # compare fileane with doc title using casefold which negates whatever case each is
                                if theTitle.casefold() != newTitleFromFilename.casefold():
                                    layout1 = [
                                        [theTextTitle('Resolve the title conflict')],
                                        [bL()],
                                        [TextLabel(u'for file %s of %s:' % (nf2f, noOfFilesToFilter))],
                                        [TextColourLabel(f012)],
                                        [bL()],
                                        [TextLabel('by choosing either:')],
                                        [bL()],
                                        [Rb('the filename title:', 'resolve', 1, True)],
                                        [TextColourLabel(newTitleFromFilename)],
                                        [bL()],
                                        [Rb("the poem's document title:", 'resolve', 2, False)],
                                        [TextColourLabel(theTitle)],
                                        [bL()],
                                        [Rb('to provide an alternative:', 'resolve', 3, False)],
                                        [sg.Input(size=(45, 1), key='-IN-', font=(FONT_REGULAR, FONT_REGULAR_SIZE))],
                                        [bL()],
                                        [Rb(u"or abandon adding this poem file's title.", 'resolve', 4, False)],
                                        [bL()], [bL()],
                                        [Btn('Resolved'), Btn("Help", '-HELP_RESOLVE-'), Btn("Quit", '-QUITTING-')]
                                    ]
                                    window1 = sg.Window(HB_UTILITY_subTITLE, layout1, size=(500, 520), keep_on_top=True,
                                                        modal=True)
                                    while True:
                                        event, values = window1.read()
                                        if Quitting(event, "You will loose any files filtered and titles extracted."):
                                            return
                                        elif event == '-HELP_RESOLVE-':
                                            popupMessage('help',
                                                         '\n\nYou must chose one of the four options\n'
                                                         'to resolve the title conflict.\n\n'
                                                         'Choose either:\n'
                                                         "1) the filename or 2) the document's title\n"
                                                         "or 3) supply an alternative or 4) abandon the file.\n\n"
                                                         "Then click RESOLVED to confirm the choice.\n\n"
                                                         "QUIT will terminate the utility.\n\n")

                                        elif event == "-RESOLVED-":
                                            if values['-RESOLVE1-']:
                                                window.close()
                                                newTitle = newTitleFromFilename
                                                break
                                            if values['-RESOLVE2-']:
                                                window.close()
                                                newTitle = theTitle
                                                break
                                            if values['-RESOLVE3-']:
                                                if values['-IN-'] != '':
                                                    window.close()
                                                    newTitle = values['-IN-']
                                                    break
                                                else:
                                                    popupMessage('warning',
                                                                 'The alternative resolution requires a new title !?')
                                            if values['-RESOLVE4-']:
                                                newTitle = ''
                                                break
                                        elif event == sg.WIN_CLOSED:
                                            newTitle = ''
                                            break
                                    window1.close()
                                else:
                                    newTitle = theTitle
                        else:
                            # add to default to filenames list
                            if newTitleFromFilename not in default2Filename and newTitle != '':
                                default2Filename += u'\n%s' % newTitleFromFilename
                                numberofdefault2Filename += 1
                            newTitle = newTitleFromFilename
                    # add the new title to the list of titles provided it's not already in it
                    theNewTitle = newTitle.strip().capitalize()
                    if theNewTitle not in theTitles and newTitle != '':
                        theTitles.append(theNewTitle)

                numberofTitles = len(theTitles)
                if verboseComments:
                    popupMessage('info', u'From the filtered files:\n\n'
                                         u'%s title%s were extracted\n\n'
                                         u"%s %s defaulted to %s filename%s:\n"
                                         u'%s\n' % (numberofTitles, pluralize(numberofTitles),
                                                    numberofdefault2Filename, was_were(numberofdefault2Filename),
                                                    its_their(numberofdefault2Filename),
                                                    pluralize(numberofdefault2Filename),
                                                    default2Filename))
                    filterMsg += u'\nhaving extracted %s titles\n' \
                                 u'with %s being defaulted to their filenames\n' % (
                                 numberofTitles, numberofdefault2Filename)
                window0['-FILTER-'].update(visible=False)
                window0['-NEXT-'].update(visible=True, button_color=(boldColours()))
                window0['-TITLE-'].update(u'3. Filtered the files and extracted their %s title%s' % (
                numberofTitles, pluralize(numberofTitles)))
                titlesExtracted = True

            elif event == '-NEXT-':
                break

        window0.close()

# ----------------------------------------------------------------------------------------------------------------------
# 4. REVIEW
# ----------------------------------------------------------------------------------------------------------------------

        titlesReviewed = False
        noOfTitlesRemoved = 0
        checkUploadTitlesCount = 0
        revisedTitles = []
        if checkTitles:
            uploadTitles = getHbGptUploadTitles()
            if (uploadTitles == None or len(uploadTitles) == 0) and verboseComments:
                popupMessage('special', 'There are no waiting upload files to check the titles against.')
                revisedTitles = theTitles
            else:
                for t in theTitles:
                    try:
                        alreadyGot = uploadTitles[t]
                        checkUploadTitlesCount += 1
                    except:
                        revisedTitles.append(t)
                if checkUploadTitlesCount != 0 and verboseComments:
                    popupMessage('special', u'Have removed %s title%s from current list\n'
                                            '%s already in the waiting upload files' % (checkUploadTitlesCount,
                                                                                        pluralize(
                                                                                            checkUploadTitlesCount),
                                                                                        itIs_theyAre(
                                                                                            checkUploadTitlesCount))

                                 )
        testForNoneFound('titles', len(revisedTitles))
        # turn titles into dictionary for constuct remove list
        td = dict(zip(revisedTitles, revisedTitles))
        finishReviewButton = Btn('Finish review', '-FINISH-', True, True, )
        categorizeButton = Btn('Categorize', '-CATEGORIZE-', False)
        nextButton = Btn('Next', '-NEXT-', False)
        layout = [[theTextTitle('4. Review and removed unwanted titles')],
                  [bL()],
                  [sg.Listbox(values=list(td.keys()), key='-SELECTED-', size=(50, 20),
                              font=(FONT_REGULAR, FONT_REGULAR_SIZE),
                              enable_events=True, select_mode=sg.LISTBOX_SELECT_MODE_EXTENDED)],
                  [bL()],
                  [sg.Input(key='_HIDDEN_', visible=False, enable_events=True, font=(FONT_REGULAR, FONT_REGULAR_SIZE)),
                   Btn('Remove')],
                  [bL()],
                  [TextLabel(u'%s titles have been removed.' % noOfTitlesRemoved, FONT_REGULAR_SIZE,
                             '-NTITLESREMOVED-')],
                  [bL()],
                  [bL()],
                  [sg.pin(finishReviewButton), sg.pin(categorizeButton), sg.pin(nextButton),
                   Btn('Help', '-HELP_REVIEW-'), Btn("Quit", '-QUITTING-')]
                  ]
        window = sg.Window(HB_UTILITY_TITLE, layout, size=(670, 650))
        removeTitles = []
        while True:

            event, values = window.read()

            if Quitting(event, "You will loose any titles reviewed"):
                return

            elif event == '-HELP_REVIEW-':
                popupMessage('help', "\n\nReviewing and removing titles is an optional step.\n\n"
                                     "if you made use of the 'check titles' option and there\n"
                                     "are one or more waiting upload files then prior to the\n"
                                     "review all pre-existing upload titles will be removed\n"
                                     "from the review list.\n\n"
                                     "in exceptional circumstances this can empty the review\n"
                                     "list - usually caused by a re-run without changing the\n"
                                     "settingss\n\n"
                                     "You are advised to make use of the review in order to\n"
                                     "remove any erronious/mistaken/similar titles.\n\n"
                                     "To remove a title highlight it by clicking on it, then\n"
                                     "click the REMOVE buttpn. Consecutive titles, called a\n"
                                     "group, can be identified by highlighting the first and\n"
                                     "then [SHIFT]+clicking on the last of the group.\n"
                                     "A group is removed by clicking on the REMOVE button.\n\n"
                                     "You must use the FINISH REVIEW button to confirm completion\n"
                                     "*** even if there has been no removals. ***\n\n"
                                     "The NEXT button (which will become visible once the review\n"
                                     "is finished) will take you on to step 5. in the process.\n\n"
                                     "QUIT will terminate the utility.\n\n")
            elif event == '-SELECTED-':
                removeTitles = values['-SELECTED-']

            elif event == '-REMOVE-':
                noOfTitles2BRemoved = len(removeTitles)
                if noOfTitles2BRemoved == 0:
                    if verboseComments: popupMessage('warning', 'No titles highlighted to remove ?!')
                else:
                    for rT in removeTitles:
                        del td[rT]
                    removeTitles[:] = []
                    noOfTitlesRemoved += noOfTitles2BRemoved
                    numberofTitles -= noOfTitles2BRemoved

                    window['-TITLE-'].update(u'4. Review the remaining %s title%s' % (numberofTitles,
                                                                                      pluralize(numberofTitles)))
                    window['-NTITLESREMOVED-'].update(u'%s title%s %s been removed.' % (noOfTitlesRemoved,
                                                                                        pluralize(noOfTitlesRemoved),
                                                                                        has_have(noOfTitlesRemoved)))
                    window['-SELECTED-'].update(td)

            elif event == '-FINISH-':
                theTitles = []
                for t in td:
                    theTitles.append(td[t])
                theTitles.sort()
                theFinalNoOfTitles = len(theTitles)
                if verboseComments:
                    popupMessage('info', u'There %s %s title%s after the review' % (is_are(theFinalNoOfTitles),
                                                                                    theFinalNoOfTitles,
                                                                                    pluralize(theFinalNoOfTitles)))
                titlesReviewed = True
                finishReviewButton.update(visible=False)
                categorizeButton.update(visible=True, button_color=(boldColours()))
                nextButton.update(visible=True, button_color=(boldColours()))
                filterMsg += '& %s removed' % noOfTitlesRemoved
            elif event == '-NEXT-' or event == '-CATEGORIZE-':
                lastEvent = event
                break

        window.close()

# ----------------------------------------------------------------------------------------------------------------------
# 5. CATEGORIZE TITLES
# ----------------------------------------------------------------------------------------------------------------------
        catUpdates = []
        if lastEvent == '-CATEGORIZE-':
            theFinalNoOfTitles = len(theTitles)
            categoriesCP, categoriesPC, catLastUpdated = load_categories()
            subCats = [CAT_DELIM]
            nCategorized = 0
            for subCat in categoriesCP:
                subCats.append(u'%s | %s' % (subCat, categoriesCP[subCat][0]))
            layout = [[theTextTitle('5. Categorize titles')],
                      [bL()],
                      [bL()],
                      [TextLabel(
                          u'There %s %s title%s to be categorized' % (is_are(theFinalNoOfTitles), theFinalNoOfTitles,
                                                                      pluralize(theFinalNoOfTitles)), FONT_REGULAR_SIZE,
                          '-NTITLES2BCATEGORIZED-')],
                      [bL()],
                      [sg.Listbox(values=theTitles, key='-SELECTED-', size=(50, 20),
                                  font=(FONT_REGULAR, FONT_REGULAR_SIZE),
                                  enable_events=True, select_mode=sg.LISTBOX_SELECT_MODE_EXTENDED),
                       sg.Input(key='_HIDDEN_', visible=False, enable_events=True,
                                font=(FONT_REGULAR, FONT_REGULAR_SIZE))],
                      [bL()],
                      [Btn('Categorize', '-CATEGORIZE TITLES-'),
                       TextLabel('with'),
                       sg.InputCombo(values=subCats, font=(FONT_REGULAR, FONT_REGULAR_SIZE), size=(35, 10),
                                     key=("-SUBandMAJORCATS-"))
                       ],
                      [bL()],
                      [TextLabel(u'There %s %s title%s categorized' % (is_are(nCategorized), nCategorized,
                                                                       pluralize(nCategorized)),
                                 FONT_REGULAR_SIZE, '-NTITLESCATEGORIZED-')],
                      [bL()],
                      [Btn('Tree', '-TREE-'), Btn('Finish', '-FINISH CATEGORIZING-', True, True),
                       Btn('Help', '-HELP_CATEGORIZE-'),
                       Btn("Quit", '-QUITTING-')]
                      ]
            window = sg.Window(HB_UTILITY_TITLE, layout, size=(550, 720))
            catTitles = []

            while True:

                event, values = window.read()

                if Quitting(event, "You will loose the titles"):
                    return

                elif event == '-HELP_CATEGORIZE-':
                    popupMessage('help', 'Categorization is optional:\n'
                                         'none, one, more or all titles can be categorized.\n\n'
                                         '1. highlight the title(s) to be categorized\n'
                                         '2. select the sub | major category from the drop down menu\n'
                                         '3. click the CATEGORIZRE button\n\n'
                                         'Multiple titles can be selected and categorized together\n'
                                         'using [SHIFT]-click for a range or [CTRL]+[SHIFT]+click\n'
                                         'for individual titles.\n\n'
                                         'IMPORTANT once categorized\n'
                                         'titles will be prefixed with ▶︎ , suffixed with the\n'
                                         'categorization and placed at the END of the titles list.\n\n'
                                         'To de-categorize a previously categorized title highlight\n'
                                         'it and re-categorize using the empty | category at the top\n'
                                         'of the drop down menu.\n\n'
                                         "'The categories tree' button is self explanatory as is the\n"
                                         "'Finish categorization' button\n"
                                         "Quit will terminate the utility.\n\n"
                                 )

                elif event == '-TREE-':

                    categoriesPC, categoriesCP, subCats, catUpdates, catLastUpdated = showCatTree(categoriesPC,
                                                                                                  categoriesCP, subCats,
                                                                                                  catUpdates,
                                                                                                  catLastUpdated)
                    window["-SUBandMAJORCATS-"].update(values=subCats)

                elif event == '-SELECTED-':
                    catTitles = values['-SELECTED-']

                elif event == '-CATEGORIZE TITLES-':
                    noOfTitles2BCat = len(catTitles)
                    nCategorized += noOfTitles2BCat
                    if noOfTitles2BCat == 0:
                        if verboseComments: popupMessage('warning', 'No titles highlighted to categorize ?!')
                    else:
                        subAndMajorCat = values['-SUBandMAJORCATS-']
                        for ct in catTitles:
                            theTitles.remove(ct)
                            if subAndMajorCat == CAT_DELIM:
                                newCt = (ct.split(CAT_DELIM)[0]).strip()
                                if CAT_PREFIX in newCt:
                                    newCt = newCt[3:]
                            else:
                                if '|' not in ct:
                                    newCt = u'%s%s%s%s' % (CAT_PREFIX, ct.strip(), CAT_DELIM, subAndMajorCat)
                            theTitles.append(newCt)
                            subCat, majorCat = subAndMajorCat.split(' | ')
                            majorCat, count = categoriesCP[subCat]
                            count += 1
                            categoriesCP[subCat] = (majorCat, count)
                        catTitles = []
                        theTitles.sort()
                        window['-SELECTED-'].update(theTitles)
                        n2BC = theFinalNoOfTitles - nCategorized
                        window['-NTITLES2BCATEGORIZED-'].update(
                            u'There %s %s title%s to be categorized' % (is_are(n2BC),
                                                                        n2BC, pluralize(n2BC)))
                        window['-NTITLESCATEGORIZED-'].update(
                            u'There %s %s title%s categorized' % (is_are(nCategorized),
                                                                  nCategorized, pluralize(nCategorized)))
                elif event == '-FINISH CATEGORIZING-':
                    break

        window.close()

    # -------end processing titles--------------------

    if processingTitles or processingCategories:

# ----------------------------------------------------------------------------------------------------------------------
# 6.CREATE UPLOAD FILE
# ----------------------------------------------------------------------------------------------------------------------

        noOfCategoryUpdates = len(catUpdates)
        testForNoneFound('titles', theFinalNoOfTitles, 'categories', noOfCategoryUpdates)
        # generate upload filename with yearMonthDayHourMinSec suffix to ensure uniqueness
        nowDT = datetime.now()
        hbUploadFilename = '__hb_gpt_upload_' + nowDT.strftime("%y%m%d%H%M%S") + '.txt'
        layout = [[theTextTitle('5. Create the upload file and finish')],
                  [bL()],
                  [bL()],
                  [TextLabel(u'There %s %s title%s and %s category update%s for the upload file:' % (
                  is_are(theFinalNoOfTitles), theFinalNoOfTitles
                  , pluralize(theFinalNoOfTitles), noOfCategoryUpdates, pluralize(noOfCategoryUpdates)))],
                  [bL()],
                  [TextColourLabel(hbUploadFilename)],
                  [bL()],
                  [bL()],
                  [Btn('Create upload', '-CREATE-', True, True), Btn('Help', '-HELP_CREATE-'),
                   Btn("Quit", '-QUITTING-')]
                  ]
        window = sg.Window(HB_UTILITY_TITLE, layout, size=(670, 300))

        while True:

            event, values = window.read()

            if Quitting(event, "You will loose the upload file about to be created."):
                return

            elif event == '-HELP_CREATE-':
                popupMessage('help', "\n\nYou must use the CREATE UPLOAD button to finish the process.\n\n"
                                     "As the name implies this will create an upload file for the\n"
                                     "application. The file, which will be placed on your desktop,\n"
                                     "will be given a unique datetime-stamp journal identifying filename.\n\n"
                                     "IMPORTANT\n"
                                     "You MUST NOT make any changes to the file's name or it's contents.\n"
                                     "To do so will render the file useless and unacceptable to the application.\n\n"
                                     "Once the upload file has beeen created the utility will terminate.\n\n"
                                     "BTW if the 'check titles' setting is used subsquently it is the\n"
                                     "titles in this file which will be used.")
            elif event == '-CREATE-':
                window.close()
                if verboseComments and filterMsg != '':  popupMessage('info', filterMsg)
                lines = HB_HUMMINGBIRD
                if theFinalNoOfTitles != 0: line += HB_TITLES
                if theFinalNoOfTitles != 0 and noOfCategoryUpdates != 0: lines += HB_AND
                if noOfCategoryUpdates != 0: lines += HB_CATEGORY_UPDATES
                lines += ['...',
                          u'... on ' + nowDT.strftime("%y-%m-%d at %H:%M:%S")]
                if theFinalNoOfTitles != 0:
                    lines += [
                        u'... %s unique title%s were found' % (theFinalNoOfTitles, pluralize(theFinalNoOfTitles)),
                        u'... in the initial set of %s file%s' % (nf, pluralize(nf)),
                        u'... retrieved from the directory:',
                        u'... %s' % sDIR]
                if noOfCategoryUpdates != 0:
                    lines += [u'... This file includes %s category update%s.'
                              % (noOfCategoryUpdates, pluralize(noOfCategoryUpdates))]
                lines += ['...',
                          '... WARNING: DO NOT MODIFY THE NAME OR CONTENTS OF THIS',
                          '... WARNING: FILE. ANY  CHANGES WILL  RENDER IT USELESS',
                          '... WARNING: AND   UNACCEPTABLE   TO   THE  APPLICATION.',
                          '...']
                if len(catUpdates) != 0: lines += catUpdates
                if len(theTitles) != 0: lines += theTitles

                if writeTamperProofUploadFile(lines, hbUploadFilename):
                    if verboseComments:
                        popupMessage('info', u'The upload file:\n\n%s\n\nhas been created on the desktop!\n\n\n'
                                             u'The utility will now terminate.' % hbUploadFilename)

                else:
                    popupMessage('error', u'Unable to create the upload file:\n\n%s\n\non the desktop ?!\n\n\n'
                                          u'This utility will now terminate.' % hbUploadFilename)
                sys.exit()


# ----------------------------------------------------------------------------------------------------------------------
# Start
# ----------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    main()