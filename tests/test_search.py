#
# This file is part of pleiades_search_api
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2022 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Test the pleiades_search_api.search module
"""
import logging
from pathlib import Path
from pleiades_search_api.search import SearchInterface

fn = Path(__file__).name
logger = logging.getLogger(fn)


class TestSearch:
    def test_init_searchinterface(self):
        si = SearchInterface()
        assert getattr(si, "web")
        assert getattr(si.web, "get")
        assert si.web.netloc == "pleiades.stoa.org"
        assert si.web.respect_robots_txt

    def test_init_custom_user_agent(self):
        ua = "CosmicBurritoBot/7.3 (+http://nowhere.com/cosmicburritobot)"
        si = SearchInterface(user_agent=ua)
        assert si.web.user_agent == ua
