#
# This file is part of pleiades_search_api
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2022 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#
"""
Basic web capabilities using the webiquette package
"""

from copy import deepcopy
import logging
from pleiades_search_api.text import normtext
from webiquette.webi import Webi, DEFAULT_HEADERS

DEFAULT_USER_AGENT = (
    "pleiades_search_api/0.0.1 (+https://github.com/isawnyu/pleiades_search_api)"
)
logger = logging.getLogger(__name__)


class Web:
    """Base mixin for providing web-aware functionality to API interface classes."""

    def __init__(
        self,
        netloc,
        webi: Webi = None,
        user_agent=DEFAULT_USER_AGENT,
        **kwargs,
    ):
        if webi is not None:
            if netloc == webi.netloc:
                self.web == webi
        else:
            headers = deepcopy(DEFAULT_HEADERS)
            ua = None
            try:
                ua = normtext(user_agent)
            except TypeError:
                pass
            if not ua:
                ua = DEFAULT_USER_AGENT
            if ua == DEFAULT_USER_AGENT:
                logger.warning(
                    f'Using default HTTP Request header for User-Agent = "{ua}". '
                    "We strongly prefer you define your own unique user-agent string."
                )
            headers["User-Agent"] = ua
            try:
                headers["accept"] = kwargs["accept"]
            except KeyError:
                pass
            web_kwargs = dict()
            if kwargs:
                for k, v in kwargs.items():
                    if k in {"respect_robots_txt", "cache_control", "expire_after"}:
                        web_kwargs[k] = v

            self.web = Webi(netloc=netloc, headers=headers, **web_kwargs)

    def get(self, uri: str):
        """HTTP get using caching, robots:crawl-delay, etc."""
        return self.web.get(uri)
