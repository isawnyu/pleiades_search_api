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
from pleiades_search_api.search import Query, SearchInterface

fn = Path(__file__).name
logger = logging.getLogger(fn)


class TestQuery:
    def test_description(self):
        q = Query()
        q.set_parameter("description", "Punic")
        assert q.parameters["description"] == "Punic"
        assert q.parameters_for_web["Description"] == "Punic"

    def test_description_or(self):
        q = Query()
        q.set_parameter("description", ["contested", "trace"], "OR")
        assert q.parameters["description"] == "contested OR trace"
        assert q.parameters_for_web["Description"] == "contested OR trace"

    def test_description_and(self):
        q = Query()
        q.set_parameter("description", ["contested", "trace"], "AND")
        assert q.parameters["description"] == "contested AND trace"
        assert q.parameters_for_web["Description"] == "contested AND trace"

    def test_title(self):
        q = Query()
        q.set_parameter("title", "Zucchabar")
        assert q.parameters["title"] == "Zucchabar"
        assert q.parameters_for_web["Title"] == "Zucchabar"

    def test_text_simple(self):
        q = Query()
        q.set_parameter("text", "Miliana")
        assert q.parameters["text"] == "Miliana"
        assert q.parameters_for_web["SearchableText"] == "Miliana"

    def test_text_or(self):
        q = Query()
        q.set_parameter("text", ["Zucchabar", "Luxmanda"], "OR")
        assert q.parameters["text"] == "Zucchabar OR Luxmanda"
        assert q.parameters_for_web["SearchableText"] == "Zucchabar OR Luxmanda"

    def test_text_and(self):
        q = Query()
        q.set_parameter("text", ["Zucchabar", "Miliana"], "AND")
        assert q.parameters["text"] == "Zucchabar AND Miliana"
        assert q.parameters_for_web["SearchableText"] == "Zucchabar AND Miliana"


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

    def test_search_rss(self):
        si = SearchInterface()
        params = (
            "Title=Zucchabar&portal_type%3Alist=Place&review_state%3Alist=published"
        )
        results = si._search_rss(params)
        assert results["query"] == "https://pleiades.stoa.org/search_rss?" + params
        assert len(results["hits"]) == 1
        hit = results["hits"][0]
        assert hit["id"] == "295374"
        assert hit["title"] == "Zucchabar"
        assert hit["uri"] == "https://pleiades.stoa.org/places/295374"
        assert hit["summary"].startswith(
            "Zucchabar was an ancient city of Mauretania Caesariensis with Punic origins."
        )

    def test_prep_params_str(self):
        si = SearchInterface()
        kwargs = {"foo": "bar"}
        params = si._prep_params(**kwargs)
        assert params == "foo=bar"
        kwargs = {"foo": "bar", "raw": "cooked"}
        params = si._prep_params(**kwargs)
        assert params == "foo=bar&raw=cooked"
        kwargs["where"] = "Burrito Bunker"
        params = si._prep_params(**kwargs)
        assert params == "foo=bar&raw=cooked&where=Burrito+Bunker"
        kwargs["when"] = "A long, long time ago"
        params = si._prep_params(**kwargs)
        assert (
            params
            == "foo=bar&raw=cooked&where=Burrito+Bunker&when=A+long%2C+long+time+ago"
        )

    def test_search_description(self):
        si = SearchInterface()
        q = Query()
        q.set_parameter("description", "Punic")
        results = si.search(q)
        assert len(results["hits"]) >= 74

    def test_search_description_or(self):
        si = SearchInterface()
        q = Query()
        q.set_parameter("description", ["contested", "conflict"], "OR")
        results = si.search(q)
        assert len(results["hits"]) >= 10

    def test_description_and(self):
        si = SearchInterface()
        q = Query()
        q.set_parameter("description", ["contested", "conflict"], "AND")
        results = si.search(q)
        assert len(results["hits"]) == 1

    def test_search_title(self):
        si = SearchInterface()
        q = Query()
        q.set_parameter("title", "Zucchabar")
        results = si.search(q)
        assert len(results["hits"]) == 1
        hit = results["hits"][0]
        assert hit["id"] == "295374"
        assert hit["title"] == "Zucchabar"
        assert hit["uri"] == "https://pleiades.stoa.org/places/295374"
        assert hit["summary"].startswith(
            "Zucchabar was an ancient city of Mauretania Caesariensis with Punic origins."
        )

    def test_search_text_simple(self):
        si = SearchInterface()
        q = Query()
        q.set_parameter("text", "Miliana")
        results = si.search(q)
        assert len(results["hits"]) == 4
        for hit in results["hits"]:
            assert hit["id"] in ["315048", "295374", "295304", "315104"]

    def test_search_text_or(self):
        si = SearchInterface()
        q = Query()
        q.set_parameter("text", ["Zucchabar", "Luxmanda"], "OR")
        results = si.search(q)
        assert len(results["hits"]) == 2
        for hit in results["hits"]:
            assert hit["id"] in ["295374", "896643025"]

    def test_search_text_and(self):
        si = SearchInterface()
        q = Query()
        q.set_parameter("text", ["Zucchabar", "Miliana"], "AND")
        results = si.search(q)
        assert len(results["hits"]) == 1
        assert results["hits"][0]["id"] == "295374"
