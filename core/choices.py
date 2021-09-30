# # global choices


HIGHLIGHT_POEM_CHOICES = (
    (0, 'none'),
    (1, 'current WIP poem'),
    (2, 'different from default MU'),
)

HIGHLIGHT_NOTE_CHOICES = (
    (0, 'none'),
    (1,  'current WIP poem'),
)

HIGHLIGHT_COMPETITION_CHOICES = (
    (0,  'none'),
    (1,  'current'),
    (2,  'historical'),
    (3,  'all'),
)

HIGHLIGHT_SUBMISSION_CHOICES = (
    (0,  'none'),
    (1,  'current'),
    (2,  'historical'),
    (3,  'all'),
)

HIGHLIGHT_PUBLISHER_CHOICES = (
    (0, 'none'),
    (1, 'all'),
)

UPLOAD_CHOICES = (
    (0, 'titles'),
    (1, 'logo')
)


UPLOAD_CHOICES = (
    (0, 'titles'),
    (1, 'logo')
)

LOGO_CHOICES = (
        (0,     'hummingbird'),
        (1,     'personal'),
        (2,     'none')
)

WAIT_DAY_CHOICES = (
        (0,     'none'),
        (1,     'next day'),
        (7,     '1 week'),
        (10,    '10 days'),
        (14,    '2 weeks'),
        (31,    '1 month'),
        (61,    '2 months'),
        (91,    '3 months'),
        (121,   '4 months'),
        (181,   '6 months'),
        (271,   '9 months'),
        (365,   '1 year'),
        (27375, 'out of UK copyright')
)

PLACE_CHOICES = (
    ('ukn', 'unknown'),
    ('unp', 'unplaced'),
    ('lng', 'Long listed'),
    ('sht', 'Short listed'),
    ('1st', 'First'),
    ('2nd', 'Secomd'),
    ('3rd', 'Third'),
    ('4th', 'Fourth'),
    ('5th', 'Fifth'),
    ('6th', 'Sixth'),
    ('7th', 'Seventh'),
    ('8th', 'Eighth'),
    ('9th', 'Ninth'),
    ('10t', 'Tenth'),
    ('wtdn', 'Withdrawn'),
    ('dltd', 'Deleted')
)


EDIT_TITLE = (
    (0,'As input'),
    (1,'Capitalise first letter'),
    (2,'All lower case'),
    (3,'Naturalise')
)


CANDIDATE_CHOICES=(
    ('δ', 'development'),
    ('𝛂', 'alpha testing'),
    ('β', 'user testing'),
    ('γ', 'release'),
    ('ζ', 'previous'),
    ('φ', 'patched'),
    ('⍵', 'emergency patch'),
)

BOOLEAN_CHOICES_MU=(
    (True, 	'Multiple'),
    (False, 'Single'),
)

BOOLEAN_CHOICES_OO=(
    (True, 	'On'),
    (False, 'Off'),
)

BOOLEAN_CHOICES_YN=(
    (True,	'Yes'),
    (False,	'No'),
)

BOOLEAN_CHOICES_SU=(
    (True, 	'Set'),
    (False, 'Unset'),
    (None, 'Unknown'),
)

BOOLEAN_CHOICES_TF=(
    (True, 	'True'),
    (False, 'False'),
)

PP_CHOICES=(
    ('Public', 	'Public'),
    ('Private', 'Private'),
)

URL_TYPE_CHOICES= (
    ('critq',   'Critique'),
    ('docmt',   'Document'),
    ('image',   'Image'),
    ('list',    'List'),
    ('rcdng',   'Recording'),
    ('refrn',   'Reference'),
    ('video',   'Video'),
)


NOTE_TYPE_CHOICES= (
    ('_wip_',   'WIP'),
    ('_vrn_',   'version'),
# additionally the implicit blank option here since this is under program control
# if note is added by user this will be blank ---
)

NOTE_SUBTYPE_CHOICES= (
    ('_fin_',   'finished'),
    ('critq',   'Critique'),
    ('draft',   'Draft'),
    ('image',   'Image'),
    ('jtngs',   'Jottings'),
    ('link',    'Link'),
    ('list',    'List'),
    ('rcdng',   'Recording'),
    ('sorce',   'Source'),
    ('refrn',   'Reference'),
    ('video',   'Video'),
)


PERIOD_CHOICES = (
    ('M','minutes'),
    ('H','hours'),
    ('D','days'),
    ('W','weeks'),
)

SUBMISSION_STATUS_CHOICES = (
    ('sbmttd', 'Submitted'),
    ('cnsdrd', 'Considered'),
    ('unknwn', 'Unknown'),
    ('rjctd',  'Rejected'),
    ('rtrnd',  'Returned'),
    ('wthdrn', 'Withdrawn'),
    ('ignrd',  'Ignored'),
    ('accptd', 'Accepted'),
    ('exprd',  'Expired'),
    ('deletd', 'Deleted'),
)

SC_SUFFIX=('to','by', 'about', 'by','by','from','by','by')

PUBLICATION_CHOICES = (
    (1, 'Anthology'),
    (2, 'Book'),
    (3, 'Chapbook'),
    (4, 'Pamphlet'),
    (5, 'Website'),
    (6, 'Project'),
)

EVENT_CHOICES = (
    (1, 'Reading'),
    (2, 'Critique'),
    (3, 'Open Mic.'),
    (4, 'Lit. Festival'),
    (5, 'Poetry Festival'),
    (6, 'Workshop'),
    (7, 'Course'),
    (8, 'Launch'),
    (9, 'Wedding'),
    (10, 'Wake'),
    (11, 'Slam'),
    (12, 'Celebration'),
    (13, 'Other'),
)

POEM_FIELDS = (
    "title",
    "dtlu",
    "form_id",
    "wip",
    'create',
    'mu',
    "nE2C",
    "nEE2C",
    "nS2M",
    "nES2M",
    "niP",
    "nR",
    "sd",
)

PREFIXES = (
    ('a', ', a'),
    ('an', ', an'),
    ('the', ', the'),
)

COUNTRIES = (
    # ('ALL', 'All'),
    ('ARG', 'Argentina'),
    ('AUS', 'Australia'),
    ('BEL', 'Belgium'),
    ('CAN', 'Canada'),
    ('DNK', 'Denmark'),
    ('FIN', 'Finland'),
    ('FRA', 'France'),
    ('DEU', 'Gernmany'),
    ('GGY', 'Gurnesey'),
    ('GRC', 'Greece'),
    ('HKG', 'Hong Kong'),
    ('HUN', 'Hungary'),
    ('ISL', 'Iceland'),
    ('IND', 'India'),
    ('IRL', 'Ireland'),
    ('ITA', 'Italy'),
    ('JPN', 'Japan'),
    ('JEY', 'Jersey'),
    ('NLD', 'Netherlands'),
    ('NZL', 'New Zealand'),
    ('NOR', 'Norway'),
    ('POL', 'Poland'),
    ('ESP', 'Spain'),
    ('ZAP', 'South Africa'),
    ('SWE', 'Sweden'),
    ('CHE', 'Switzerland'),
    ('GBR', 'UK'),
    ('USA', 'USA'),
)

RESOURCE_CHOICES = (
    (1,"Competitions"),
    (2,"Magazines"),
    (3,"Publishers"),
)

OS_CHOICES = (
    ("All","All"),
    ("Mac OS X","Mac OS X"),
    ("Windows","Windows"),
    ("Linux", "Linux"),
    ("Debian","Debian"),
)

DOWNLOAD_CHOICES =(
    (1,"Utility"),
    (2,"Bulletin"),
    (3,"ReadMe"),
    (4,"Release notes"),
    (5,'Category update')
)

POEM_LISTING_CHOICES =(
    (1,"Candidate & Used flags"),
    (2,"Entries, Submissions, Publishing & Readings numbers"),
    (3,"ES current & historical numbers P&R")
)

ERROR_CLASSIFICATION=(
    (0,"Critical"),
    (1,"Data"),
    (2,"Operational"),
    (3,"Coding"),
    (10,"Help fix"),
    (11,"Help required"),
    (20,"RFI urgent"),
    (21,"RFI non-urgent"),
    (30,"Cosmetic"),
    (97,"Duplicate"),
    (90,"No error"),
    (99,"Unclassified"),
)

ACTION_CHOICES=(
    (0, "TBA"),
    (1, "Assessing"),
    (2, "Fixing"),
    (3, "Resolved"),
    (4, "Awaiting release update"),
    (5, "No action"),
    (6, "No fix possible"),
    (7, "Re-classified"),
    (8, "Requires software/package update"),
    (9, "Dismissed"),
)

COMMENT_PREFIX              ='..'
REMOVE_CATEGORY_PREFIX      ='- '
ADD_CATEGORY_PREFIX         ='+ '
RENAME_CATEGORY_PREFIX      ='= '
CATEGORIZED_TITLE_PREFIX    ='>︎ '
CATEGORY_DELIM              =' | '

MAJOR_CATEGORIES=['Life', 'Humanities', 'Natural World', 'Sciences','The Inexplicable']

SUB_CATEGORIES=[
#     parent,           child
    ('Life',            'Personal'),
    ('Life',            'Relationships'),
    ('Relationships',   'Love'),
    ('Relationships',   'Mother'),
    ('Relationships',   'Father'),
    ('Love',            'Partner'),
    ('Love',            'Other'),
    ('Life',            'Current events'),
    ('Life',            'Connections'),
    ('Humanities',      'Art'),
    ('Humanities',      'Literature'),
    ('Humanities',      'Philosophy'),
    ('Humanities',      'Poetry'),
    ('Humanities',      'Religion'),
    ('Humanities',      'Perfoming arts'),
    ('Perfoming arts',  'Music'),
    ('Perfoming arts',  'Dance'),
    ('Humanities',      'Classics'),
    ('Natural World',   'Gardens'),
    ('Natural World',   'Trees'),
    ('Natural World',   'Rain'),
    ('Natural World',   'Landscapes'),
    ('Natural World',   'Places'),
    ('Natural World',   'Animals'),
    ('Animals',         'Elephants'),
    ("Animals",         'Rhinoceress'),
    ('Places',          'Crete'),
    ('Places',          'India'),
    ('Places',          'Siri Lanka'),
    ('Sciences',        'Astronomy'),
    ('Sciences',        'Mathematics'),
    ('Sciences',        'Physics'),
    ('The Inexplicable','Surreal'),
    ('The Inexplicable','Magic'),
    ('The Inexplicable','Synchronicity'),
]

POETIC_FORMS=(
    (10,' '),
    (20,'ABC'),
    (30,'abecedarian'),
    (40,'acrostic'),
    (50,'alexandrine'),
    (60,'allieration'),
    (70,'ballard'),
    (80,'ballade'),
    (90,'bhajan'),
    (100,'bio'),
    (110,'blank verse'),
    (120,'blitz'),
    (130,'burlesque'),
    (140,'canto'),
    (150,'canzone'),
    (160,'carpe-diem'),
    (170,'chant royal'),
    (180,'chastushka'),
    (190,'choka'),
    (200,'cinqku'),
    (210,'cinquain'),
    (220,'classicism'),
    (230,'clerihew'),
    (240,'concrete'),
    (250,'consonance'),
    (260,'couplet'),
    (270,'cowboy'),
    (280,'crown of sonnets'),
    (290,'crystalline'),
    (300,'curtal sonnet'),
    (310,'diamante'),
    (320,'didactic'),
    (330,'diminished hexaverse'),
    (340,'dirge'),
    (350,'dizain'),
    (360,'dodoitsu'),
    (370,'doggerel'),
    (380,'double dactyl'),
    (390,'dramatic monologue'),
    (400,'dramatic verse'),
    (410,'ekphrastic'),
    (420,'elergy'),
    (430,'englyn'),
    (440,'epic'),
    (450,'epigram'),
    (460,'epitaph'),
    (470,'epithalamium'),
(480,'epulaerya'),
(490,'epyllion'),
(500,'etheree'),
(510,'found'),
(520,'free verse'),
(530,'ghazal'),
(540,'grook'),
(550,'haibun'),
(560,'haiku'),
(570,'hamd'),
(580,'heroic couplet'),
(590,'horatian ode'),
(600,'hybronnet'),
(610,'iambic pentameter'),
(620,'idyll'),
(630,'imagism'),
(640,'irregular ode'),
(650,'juiju'),
(660,'kakuhb'),
(670,'lampoon'),
(680,'lanterne'),
(690,'lay'),
(700,'lento'),
(710,'light verse'),
(720,'limerick'),
(730,'list'),
(740,'lyric'),
(750,'madah'),
(760,'mandakranta'),
(770,'manqabat'),
(780,'marsiya'),
(790,'masnavi'),
(800,'mcwhirtle'),
(810,'monoku'),
(820,'mono-rhyme'),
(830,'musaddas'),
(840,'naat'),
(850,'name'),
(860,'narrative'),
(870,'ninette'),
(880,'nonette'),
(890,'ode'),
(900,'nursery rhyme'),
(910,'ottava rima'),
(920,'pantoum'),
(930,'parallelismus memrorum'),
(940,'pastoral'),
(950,'payar'),
(960,'personification'),
(970,'prayer'),
(980,'prose poem'),
(990,'petrarchan sonnet'),
(1000,'pindaric ode'),
(1010,'qasida'),
(1020,'qawwali'),
(1030,'quatrain'),
(1040,'questionku'),
(1050,'quintain'),
(1060,'quintella'),
(1070,'rengay'),
(1080,'refrain'),
(1090,'rhyme'),
(1100,'rhyme royal'),
(1110,'rictamete'),
(1120,'rispetto'),
(1130,'romanticism'),
(1140,'rondeau'),
(1150,'rubaiyat'),
(1160,'salaam'),
(1170,'sapphic stanza'),
(1180,'sedoka'),
(1190,'senrya'),
(1200,'sestina'),
(1210,'shape'),
(1220,'sijo'),
(1230,'sloka'),
(1240,'sonnet'),
(1250,'suzette prime'),
(1260,'tail-rhyme'),
(1270,'tanka'),
(1280,'tazkira'),
(1290,'terza rima'),
(1300,'terzanelle'),
(1310,'tetractys'),
(1320,'than-bauk'),
(1330,'triolet'),
(1340,'tyburn'),
(1350,'vaasokht'),
(1360,'verse'),
(1370,'villanelle'),
(1380,'vogon')
)


#===============================================

def lookupChoiceIndex(choiceName, choiceText):
    noOfChoices=len(choiceName)
    for i in range (noOfChoices):
        index,name=choiceName[i]
        if name==choiceText:
            return index,i
    raise ValueError


def lookupChoiceText(choiceName,choiceIndex):
    noOfChoices = len(choiceName)
    for i in range (noOfChoices):
        index, name = choiceName[i]
        if index==choiceIndex:
            return name,i
    raise ValueError