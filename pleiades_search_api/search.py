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

logger = logging.getLogger(__name__)


class Query:
    def __init__(self):
        self.parameters = dict()
        self._supported_parameters = {
            "description": (str, list),
            "text": (str, list),
            "title": str,
        }
        self._default_parameters = {
            "portal_type": ["Place"],
            "review_state": ["published"],
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
        for k, v in self._default_parameters.items():
            p[k] = v
        for k, v in self.parameters.items():
            these_web_params = self._convert_for_web(k, v)
            for webk, webv in these_web_params.items():
                p[webk] = webv
        return p

    def set_parameter(self, name, value, operator=None):
        """Set a single parameter on the query."""
        try:
            expected_classes = self._supported_parameters[name]
        except KeyError:
            raise ValueError(
                f"Unexpected parameter name '{name}'. Supported parameters: {sorted(self.supported)}."
            )
        if not isinstance(value, expected_classes):
            raise TypeError(
                f"Unexpected type {type(value)} for parameter '{name}'. Expected type(s): {expected_classes}."
            )
        self.parameters[name] = getattr(
            self, f"_set_parameter_{value.__class__.__name__.lower()}"
        )(value, operator)

    def _convert_for_web(self, name, value):
        return getattr(self, f"_convert_{name}_for_web")(value)

    def _convert_description_for_web(self, value):
        return {"Description": value}

    def _convert_text_for_web(self, value):
        return {"SearchableText": value}

    def _convert_title_for_web(self, value):
        return {"Title": value}

    def _set_parameter_list(self, value: list, operator=None):
        """Process a string value for parameterization"""
        values = [
            getattr(self, f"_set_parameter_{v.__class__.__name__.lower()}")(v)
            for v in value
        ]
        if operator:
            separator = f" {operator} "
        else:
            separator = ","
        return separator.join(values)

    def _set_parameter_str(self, value: str, *args, **kwargs):
        """Process a string value for parameterization"""
        return normtext(value)


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
            if isinstance(v, str):
                ready_kwargs[k] = v
            elif isinstance(v, list):
                ready_kwargs[f"{k}:list"] = ",".join(v)
            else:
                raise TypeError(type(v))
        params = urlencode(ready_kwargs)
        return params
