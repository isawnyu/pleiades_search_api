#
# This file is part of pleiades_search_api
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2022 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#
"""
Test the pleiades_search_api/text module.
"""
import logging
from pleiades_search_api.text import normtext

logger = logging.getLogger(__name__)


class TestText:
    def test_normtext_unity(self):
        s = "Banana"
        assert s == normtext(s)

    def test_normtext_single_space(self):
        s = "Banana split"
        assert s == normtext(s)

    def test_normtext_strip(self):
        s = "    Banana split "
        assert s.strip() == normtext(s)

    def test_normtext_lines(self):
        s = "\nBanana\nsplit\n"
        assert "Banana split" == normtext(s)

    def text_normtext_mixed_white_space(self):
        s = "\n    \tBanana       \tsplit\t\t\t\t \t"
        assert "Banana split" == normtext(s)

    # TBD: unicode normalization, but we know that textnorm does this
