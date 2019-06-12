# The contents of this file are subject to the Mozilla Public License
# Version 2.0 (the "License"); you may not use this file except in
# compliance with the License. You may obtain a copy of the License at
#    http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS IS"basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
# for the specific language governing rights and limitations under the
# License.
#
# OS2Webscanner was developed by Magenta in collaboration with OS2 the
# Danish community of open source municipalities (http://www.os2web.dk/).
#
# The code is currently governed by OS2 the Danish community of open
# source municipalities ( http://www.os2web.dk/ )
"""Settings file for the Exchange export module"""
import os
BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
PROJECT_DIR = os.path.dirname(BASE_DIR)
VAR_DIR = os.path.join(PROJECT_DIR, 'var')
LOGS_DIR = os.path.join(VAR_DIR, 'logs')

EXCHANGE_LOGGER_DIR = LOGS_DIR + '/exchange'
if not os.path.exists(EXCHANGE_LOGGER_DIR):
    os.mkdir(EXCHANGE_LOGGER_DIR)

# Path to exchange export dir
EXCHANGE_EXPORT_DIR_PREFIX = '/tmp/os2webscanner/exchangescan/'

DAYS_BETWEEN_DOWNLOAD = 1

# Number of email downloader threads that should be running.
NUMBER_OF_EMAIL_THREADS = 4

MAX_WAIT_TIME = 1000
