#
# This file is part of pleiades_search_api
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2022 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#
"""
Defines the SearchInterface class: handle interactions with Pleiades
"""

import feedparser
import logging
from urllib.parse import urlunparse
from pleiades_search_api.web import Web, DEFAULT_USER_AGENT

logger = logging.getLogger(__name__)


class SearchInterface(Web):
    def __init__(self, user_agent=DEFAULT_USER_AGENT):
        Web.__init__(self, netloc="pleiades.stoa.org", user_agent=user_agent)

    def _search_rss(self, params):
        """Use Pleiades RSS search interface since it gives us back structured data."""
        uri = urlunparse(("https", "pleiades.stoa.org", "/search_rss", "", params, ""))
        logger.debug(uri)
        r = self.get(uri)
        hits = list()
        data = feedparser.parse(r.text)
        for entry in data.entries:
            hits.append(
                {
                    "id": entry.link.split("/")[-1],
                    "uri": entry.link,
                    "title": entry.title,
                    "summary": entry.description,
                }
            )
        return {"query": uri, "hits": hits}
