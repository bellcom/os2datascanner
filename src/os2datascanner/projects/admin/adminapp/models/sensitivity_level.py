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

from django.utils.translation import ugettext_lazy as _


class Sensitivity:

    """Name space for sensitivity values."""

    def __init__(self):
        pass

    CRITICAL = 3
    HIGH = 2
    LOW = 1
    OK = 0

    choices = (
        (CRITICAL, _('Critical')),
        (HIGH, _('Problem')),
        (LOW, _('Warning')),
        (OK, _('Notification')),
    )
