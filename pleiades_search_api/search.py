#
# This file is part of pleiades_search_api
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2022 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#
"""
Defines the SearchInterface class: handle interactions with Pleiades
"""

import logging
from pleiades_search_api.web import Web, DEFAULT_USER_AGENT

logger = logging.getLogger(__name__)


class SearchInterface(Web):
    def __init__(self, user_agent=DEFAULT_USER_AGENT):
        Web.__init__(self, netloc="pleiades.stoa.org", user_agent=user_agent)
