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
from urllib.parse import urlencode, urlunparse
from pleiades_search_api.text import normtext
from pleiades_search_api.web import Web, DEFAULT_USER_AGENT
from pprint import pformat

logger = logging.getLogger(__name__)


class Query:
    def __init__(self):
        self.parameters = dict()
        self._supported_parameters = {
            "bbox": {"expected": (tuple), "behavior": self._preprocess_bbox},
            "description": {
                "expected": (str, list),
                "list_behavior": "join",
                "rename": "Description",
            },
            "feature_type": {
                "expected": (str, list),
                "list_behavior": "noseq",
                "list_additional": {"AND": {"get_usage:ignore_empty": "operator:and"}},
                "rename": "getFeatureType",
            },
            "tag": {
                "expected": (str, list),
                "list_behavior": "noseq",
                "list_additional": {
                    "AND": {"Subject_usage:ignore_empty": "operator:and"}
                },
                "rename": "Subject:list",
            },
            "text": {
                "expected": (str, list),
                "list_behavior": "join",
                "rename": "SearchableText",
            },
            "title": {"expected": str, "rename": "Title"},
        }
        self._default_web_parameters = {
            "portal_type:list": "Place",
            "review_state:list": "published",
        }

    @property
    def supported(self):
        """List supported parameters"""
        return list(self._supported_parameters.keys())

    def clear_parameters(self):
        """Reset all parameters for the query."""
        self.parameters = dict()

    @property
    def parameters_for_web(self):
        p = dict()
        for k, v in self._default_web_parameters.items():
            p[k] = v
        for k, v in self.parameters.items():
            these_web_params = self._convert_for_web(k, *v)
            for webk, webv in these_web_params.items():
                p[webk] = webv
        return p

    def set_parameter(self, name, value, operator=None):
        """Set a single parameter on the query."""
        try:
            rules = self._supported_parameters[name]
        except KeyError:
            raise ValueError(
                f"Unexpected parameter name '{name}'. Supported parameters: {sorted(self.supported)}."
            )
        if not isinstance(value, rules["expected"]):
            raise TypeError(
                f"Unexpected type {type(value)} for parameter '{name}'. Expected type(s): {rules['expected']}."
            )
        self.parameters[name] = (value, operator)

    def _convert_for_web(self, name, value, operator):
        """Convert our generic parameters to the specific ones Pleiades uses"""
        web_params = dict()
        rules = self._supported_parameters[name]

        # determine parameter name (key) to use in web query
        try:
            newname = rules["rename"]
        except KeyError:
            cooked_key = name
        else:
            cooked_key = newname

        # pre-process web parameters to meet Pleiades query interface expectations
        try:
            preprocess_func = rules["behavior"]
        except KeyError:
            if isinstance(value, list):
                try:
                    behavior = rules["list_behavior"]
                except KeyError:
                    cooked_value = " ".join(value)
                else:
                    if behavior == "list":
                        cooked_key = ":".join((cooked_key, "list"))
                        cooked_value = ",".join(value)
                    elif behavior == "join":
                        if operator:
                            cooked_value = f" {operator} ".join(value)
                        else:
                            cooked_value = " ".join(value)
                    elif behavior == "noseq":
                        logger.debug(f"noseq for {name}")
                        cooked_value = (
                            value  # assumes urlencode will be applied with noseq=True
                        )
                    else:
                        raise ValueError(behavior)
                try:
                    additional = rules["list_additional"][operator]
                except KeyError:
                    pass
                else:
                    for add_k, add_v in additional.items():
                        web_params[add_k] = add_v
            elif isinstance(value, str):
                cooked_value = value
            else:
                raise TypeError(type(value))
            web_params[cooked_key] = cooked_value
        else:
            these_params = preprocess_func(value)
            for this_k, this_v in these_params.items():
                web_params[this_k] = this_v
        return web_params

    def _preprocess_bbox(self, bounds: tuple):
        shaved_bounds = list()  # pleiades is weird
        for i in [0, 1]:
            shaved_bounds.append(bounds[i] + 0.0001)
        for i in [2, 3]:
            shaved_bounds.append(bounds[i] - 0.0001)
        return {
            "lowerLeft": f"{shaved_bounds[0]},{shaved_bounds[1]}",
            "upperRight": f"{shaved_bounds[2]},{shaved_bounds[3]}",
            "predicate": "intersection",
            "location_precision:list": "precise",
        }


class SearchInterface(Web):
    def __init__(self, user_agent=DEFAULT_USER_AGENT):
        Web.__init__(self, netloc="pleiades.stoa.org", user_agent=user_agent)
        self._terms = {"title": str}

    def search(self, query: Query):
        """Search Pleiades for the query."""
        params = self._prep_params(**query.parameters_for_web)
        return self._search_rss(params)

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

    def _prep_params(self, **kwargs):
        ready_kwargs = dict()
        for k, v in kwargs.items():
            if v is None:
                ready_kwargs[k] = ""
            elif isinstance(v, str):
                ready_kwargs[k] = v
            elif isinstance(v, list):
                if k in ["getFeatureType", "Subject:list"]:
                    ready_kwargs[k] = v
                else:
                    ready_kwargs[f"{k}:list"] = ",".join(v)
            else:
                raise TypeError(type(v))
        params = urlencode(ready_kwargs, doseq=True)
        return params
