#__BEGIN_LICENSE__
# Copyright (c) 2015, United States Government, as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All rights reserved.
#
# The xGDS platform is licensed under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0.
#
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
#__END_LICENSE__

# siteSettings.py -- site default settings
#
# This contains the default settings for the site-level django app.  This will
# override any application-default settings and define the default set of
# installed applications. This should be a full settings.py file which needs
# minimal overrides by the settings.py file for the application to actually
# function.
#
# As a bare minimum, please edit INSTALLED_APPS!
#
# This file *should* be checked into git.
import importlib
import os
import sys

from django.conf import global_settings
from django.core.urlresolvers import reverse

from django.db import models

from geocamUtil.SettingsUtil import getOrCreateDict, getOrCreateArray, HOSTNAME

XGDS_SITE_APP = "xgds_braille_app"

SITE_TITLE = 'BRAILLE'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '***REMOVED***'

#XGDS_BROWSERIFY = getOrCreateArray('XGDS_BROWSERIFY')
FAVICON_PATH = "xgds_core/icons/favicon.ico"

# from apps.basaltApp.instrumentDataImporters import *
# apps should be listed from "most specific" to "most general".  that
# way, templates in more specific apps override ones from more general
# apps.
INSTALLED_APPS = ['django_npm_apps',
                  XGDS_SITE_APP,

                  # TODO uncomment the submodules that you are including
                  'xgds_sample',
                  'xgds_instrument',
                  'xgds_image',
                  'xgds_notes2',
                  'xgds_planner2',
                  'xgds_map_server',
                  # 'xgds_video',
                  'xgds_plot',
                  # 'xgds_status_board',

                  'deepzoom',
                  'geocamTrack',
                  'xgds_timeseries',
                  'xgds_core',
                  'geocamPycroraptor2',
                  'geocamUtil',
                  'pipeline',
                  'taggit',
                  'resumable',
                  'django_markwhat',
                  'jsonify',

                  'dal',
                  'dal_select2',
                  'rest_framework.authtoken',
                  'rest_framework',
                  'corsheaders',
                  'django.contrib.admin',
                  'django.contrib.auth',
                  'django.contrib.contenttypes',
                  'django.contrib.sessions',
                  'django.contrib.sites',
                  'django.contrib.messages',
                  'django.contrib.staticfiles',
                  ]

for app in reversed(INSTALLED_APPS):
    try:
        appSettings = importlib.import_module(app + ".defaultSettings")
        for key, val in vars(appSettings).iteritems():
            if not key.startswith('_'):
                globals()[key] = val
    except:
        pass

USING_DJANGO_DEV_SERVER = ('runserver' in sys.argv)
USE_STATIC_SERVE = USING_DJANGO_DEV_SERVER

SCRIPT_NAME = os.environ['DJANGO_SCRIPT_NAME']  # set in sourceme.sh
if USING_DJANGO_DEV_SERVER:
    # django dev server deployment won't work with other SCRIPT_NAME settings
    SCRIPT_NAME = '/'


DEBUG = True
# TEMPLATE_DEBUG = DEBUG

    
PROJ_ROOT = os.path.abspath(os.path.dirname(__file__))
if not PROJ_ROOT.endswith('/'):
    PROJ_ROOT += '/'

# Python path is agnostic to what the site-level dir is. It also prefers the
# checked-out version of an app over the standard python install locations.
sys.path.append(PROJ_ROOT)

ADMINS = (
    # ('NASA Intelligent Robotics Group', 'your_email@domain.com'),
)
MANAGERS = ADMINS

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Los_Angeles'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-US'

SITE_ID = 1  # This is for Django's site framework - NOT to specify the location of a field site.

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds static.
# Example: "/home/static/static.lawrence.com/"
STATIC_ROOT = os.path.join(PROJ_ROOT, "build", "static")

# URL that handles the static served from STATIC_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://static.lawrence.com", "http://example.com/static/"
STATIC_URL = SCRIPT_NAME + 'static/'
EXTERNAL_URL = STATIC_URL

# Absolute path to the directory that holds data. This is different than static
# in that it's uploaded/processed data that's not needed for the operation of
# the site, but may need to be network-accessible, or be linked to from the
# database. Examples: images, generate kml files, etc.
# Example: "/data"
DATA_ROOT = os.path.join(PROJ_ROOT, 'data', '')

# URL that handles the data served from DATA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://data.lawrence.com", "http://example.com/data/"
DATA_URL = SCRIPT_NAME + 'data/'

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = DATA_ROOT

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = DATA_URL

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(PROJ_ROOT, 'apps', XGDS_SITE_APP, 'templates'),
            os.path.join(PROJ_ROOT, 'apps', XGDS_SITE_APP, 'templates', XGDS_SITE_APP),
            os.path.join(PROJ_ROOT, 'apps/xgds_core/templates/registration'),
            STATIC_ROOT,

            # Templates for utility scripts
            os.path.join(PROJ_ROOT, 'bin/templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'debug': True,
            'context_processors': ['django.template.context_processors.request',
                                   'django.contrib.auth.context_processors.auth',
                                   'django.template.context_processors.debug',
                                   'django.template.context_processors.i18n',
                                   'django.template.context_processors.media',
                                   'django.template.context_processors.static',
                                   'django.template.context_processors.tz',
                                   'django.contrib.messages.context_processors.messages',
                                   'geocamUtil.context_processors.settings',
                                   'geocamUtil.context_processors.AuthUrlsContextProcessor.AuthUrlsContextProcessor',
                                   'geocamUtil.context_processors.SettingsContextProcessor.SettingsContextProcessor'
                                   ],
                    },
        },
    ]


# Session Serializer: we use Pickle for backward compatibility and to allow more flexible session storage, but
# be sure to keep the SECRET_KEY secret for security (see:
# https://docs.djangoproject.com/en/1.7/topics/http/sessions/#session-serialization)
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'


# List of callables that know how to import templates from various sources.
# TEMPLATE_LOADERS = ('django.template.loaders.filesystem.Loader',
#                     'django.template.loaders.app_directories.Loader',
#                     #     'django.template.loaders.eggs.load_template_source',
#                     )

MIDDLEWARE_CLASSES = (
    'geocamUtil.middleware.LogErrorsMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.RemoteUserMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.RemoteUserBackend',
    'django.contrib.auth.backends.ModelBackend'
]

ROOT_URLCONF = 'urls'

#TODO probably can delete the below 2 lines
LOGIN_URL = SCRIPT_NAME + 'accounts/login/'
LOGIN_REDIRECT_URL = '/'

# email settings
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = '/tmp/xgds_messages'
EMAIL_SUBJECT_PREFIX = '[xGDS] '
SERVER_EMAIL = 'noreply@xgds.org'

STATICFILES_STORAGE = 'pipeline.storage.PipelineCachedStorage'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'pipeline.finders.FileSystemFinder',
    'pipeline.finders.AppDirectoriesFinder',
    'pipeline.finders.PipelineFinder',
    'pipeline.finders.CachedFileFinder',
    'djangobower.finders.BowerFinder',
    'django_npm_apps.finders.NpmAppFinder',
)

# SET UP PIPELINE
PIPELINE = getOrCreateDict('PIPELINE')
PIPELINE['PIPELINE_ENABLED'] = True
PIPELINE['JS_COMPRESSOR'] = 'pipeline.compressors.yuglify.YuglifyCompressor'
PIPELINE['CSS_COMPRESSOR'] = 'pipeline.compressors.yuglify.YuglifyCompressor'
PIPELINE['YUGLIFY_JS_ARGUMENTS'] = 'mangle:false --terminal'
PIPELINE['DISABLE_WRAPPER'] = True


COMPRESS_ENABLED = False
#COMPRESS_CSSTIDY_BINARY = '/usr/bin/csstidy'

# PIPELINE_COMPILERS = ()

DEBUG_TOOLBAR = False
if DEBUG_TOOLBAR:
    INSTALLED_APPS += ('debug_toolbar',)
    MIDDLEWARE_CLASSES_LIST = list(MIDDLEWARE_CLASSES)
    MIDDLEWARE_CLASSES_LIST.insert(2, 'debug_toolbar.middleware.DebugToolbarMiddleware')
    MIDDLEWARE_CLASSES = tuple(MIDDLEWARE_CLASSES_LIST)
    INTERNAL_IPS = ('127.0.0.1', 
                    '10.0.3.1',
                    '::1')  # TODO add your virtual machine's IP here from your host; 
    #ie do an ifconfig and see if virtualbox or vmware has created something.
    # Alternately you can create a view that returns request.META['REMOTE_ADDR']
    DEBUG_TOOLBAR_PANELS = ['debug_toolbar.panels.versions.VersionsPanel',
                            'debug_toolbar.panels.timer.TimerPanel',
                            'debug_toolbar.panels.settings.SettingsPanel',
                            'debug_toolbar.panels.headers.HeadersPanel',
                            'debug_toolbar.panels.request.RequestPanel',
                            'debug_toolbar.panels.sql.SQLPanel',
                            'debug_toolbar.panels.staticfiles.StaticFilesPanel',
                            'debug_toolbar.panels.templates.TemplatesPanel',
                            'debug_toolbar.panels.cache.CachePanel',
                            'debug_toolbar.panels.signals.SignalsPanel',
                            'debug_toolbar.panels.logging.LoggingPanel',
                            'debug_toolbar.panels.redirects.RedirectsPanel',
                            #'debug_toolbar.panels.profiling.ProfilingPanel',
                            ]
    DEBUG_TOOLBAR_CONFIG = {'INTERCEPT_REDIRECTS': False,
                            'RENDER_PANELS': True,
                            'JQUERY_URL': '',
                           }

VAR_ROOT = PROJ_ROOT + 'var/'

XGDS_PLANNER_SCHEMAS["KRex2"] = {
    "schemaSource": "apps/xgds_braille_app/planner/kRex2PlanSchema.json",
    "librarySource": "apps/xgds_braille_app/planner/kRex2PlanLibrary.json",
    "simulatorUrl": "xgds_planner2/js/planner/genericVehicleSimulator.js",
    "simulator": "genericVehicle.Simulator",  # the namespace within the simulator js
}

XGDS_PLANNER_DEFAULT_SITE = ('LAB', 'Lava Beds')

XGDS_PLANNER_CRS_UNITS_DEFAULT = True

XGDS_PLANNER_PLAN_EXPORTERS = (
    # ('xpjson', '.json', 'xgds_planner2.planExporter.XpjsonPlanExporter'),
    # ('bearing_distance', '.bdj', 'xgds_planner2.planExporter.BearingDistanceJsonPlanExporter'),
    ('bearing_distance', '.cbdj', 'xgds_planner2.planExporter.BearingDistanceCRSJsonPlanExporter', 'bdJson'),
    ('kml', '.kml', 'xgds_planner2.kmlPlanExporter.KmlPlanExporter'),
    # ('stats', '-stats.json', 'xgds_planner2.statsPlanExporter.StatsPlanExporter'),
    ('crsjson', '.crsjson', 'xgds_planner2.planExporter.CrsJsonPlanExporter', 'Json'),
)


GEOCAM_TRACK_POSITION_MODEL = 'geocamTrack.ResourcePoseDepth'
GEOCAM_TRACK_PAST_POSITION_MODEL = 'geocamTrack.PastResourcePoseDepth'
GEOCAM_TRACK_OPS_TIME_ZONE = TIME_ZONE
GEOCAM_TRACK_CLOSEST_POSITION_MAX_DIFFERENCE_SECONDS = 360  # our data does not come in very frequently so set this to 6 minutes.


# XGDS_INSTRUMENT_IMPORT_MODULE_PATH = 'xgds_baseline_app.instrumentDataImporters'

# GEOCAM_TRACK_RECENT_TIME_FUNCTION = 'xgds_baseline_app.views.getCurrentTimeWithDelayCorrection'


PYRAPTORD_SERVICE = True

XGDS_CURRENT_SITEFRAME_ID = 2
XGDS_CORE_LIVE_INDEX_URL = '/' + XGDS_SITE_APP + '/live'
XGDS_CORE_FLIGHT_MONIKER = "Traverse"


TEST_RUNNER = 'django.test.runner.DiscoverRunner'



def make_key(key, key_prefix, version):
    return key

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        'TIMEOUT': 604800,
        'KEY_FUNCTION' : make_key
    }
}

# FILE_UPLOAD_TEMP_DIR = os.path.join(DATA_ROOT, XGDS_MAP_SERVER_GEOTIFF_SUBDIR, 'temp')
#ZEROMQ_PORTS = PROJ_ROOT + 'apps/xgds_baseline_app/ports.json'


USE_TZ = True

# turn this on when we are live field broadcasting
GEOCAM_UTIL_LIVE_MODE = False
GEOCAM_UTIL_DATATABLES_EDITOR = False
GEOCAM_TRACK_URL_PORT = 8181


XGDS_CORE_TEMPLATE_DEBUG = True

COUCHDB_FILESTORE_NAME = "braille-file-store"


ALLOWED_HOSTS = ['*']


# Setup support for proxy headers
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
         'rest_framework.permissions.IsAuthenticated',
    ]
}

SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 43200 # 12 hours

XGDS_MAP_SERVER_JS_MAP = getOrCreateDict('XGDS_MAP_SERVER_JS_MAP')

XGDS_MAP_SERVER_JS_MAP['Spectrometer'] = {'ol': 'xgds_instrument/js/olSpectrometerDataProduct.js',
                                          'model': 'xgds_braille_app.NirvssSpectrometerDataProduct',
                                          'columns': ['checkbox', 'acquisition_time', 'acquisition_timezone', 'collector_name', 'name', 'description', 'pk', 'view_url', 'app_label', 'model_type', 'type', 'lat', 'lon', 'alt', 'flight_name', 'instrument_name','manufacturer_data_file_url','portable_data_file_url','jsonDataUrl','csvDataUrl', 'DT_RowId'],
                                          'hiddenColumns': ['pk', 'view_url', 'app_label', 'model_type','type', 'lat','lon','alt','flight_name','instrument_name','manufacturer_data_file_url','portable_data_file_url','jsonDataUrl','csvDataUrl', 'DT_RowId'],
                                          'columnTitles': ['Time', 'TZ', 'Collector', 'Name', 'Description'],
                                          'viewHandlebars': 'xgds_instrument/templates/xgds_instrument/handlebars/instrument-view.handlebars',
                                          'viewJS': [EXTERNAL_URL + 'flot/jquery.flot.js',
                                                     EXTERNAL_URL + 'flot-axislabels/jquery.flot.axislabels.js',
                                                     STATIC_URL + 'xgds_instrument/js/instrumentView.js' ],
                                          'viewInitMethods': ['xgds_instrument.getData'],
                                          'event_time_field': 'acquisition_time',
                                          'event_timezone_field': 'acquisition_timezone',
                                          'plotLabels': ['Wavelength(nm)','Reflectance'],
                                          'search_form_class': 'xgds_braille_app.forms.SearchNirvssSpectrometerDataForm'
                                          }

GEOCAM_TRACK_PAST_POSITION_MODEL = 'geocamTrack.PastResourcePoseDepth'

