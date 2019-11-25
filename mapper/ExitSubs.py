# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import re

exitRegexpString =\
r"(?P<isNone>none)|[-=~]?[\[(#{/\\]?(?P<dir>north|east|south|west|up|down)[\])#{/\\]?[-=~]?"

exitRegexp = re.compile("^" + exitRegexpString + "$")
autoexitRegexp = re.compile(r"Exits: (?P<exits>(" + exitRegexpString + r"(, )?)+)\.")
exitCommandRegexp = re.compile(
	r"(?P<exits>( *" + exitRegexpString + " +- [^\r]+(\r\n)?)+)"
)
