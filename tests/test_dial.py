#!/usr/bin/env python
# -*- coding: utf-8 -*-

import modi
import mock
import unittest

from modi.module.dial import Dial


class TestDial(unittest.TestCase):
    """Tests for 'Dial' class."""

    def setUp(self):
        """Set up test fixtures, if any."""
        mock_args = (-1, -1, None, None)
        self.dial = Dial(*mock_args)
        self.dial._get_property = mock.MagicMock()

    def tearDown(self):
        """Tear down test fixtures, if any."""
        del self.dial

    def test_get_degree(self):
        """Test get_degree method."""
        self.dial.get_degree()
        self.dial._get_property.assert_called_once_with(self.dial.PropertyType.DEGREE)

    def test_get_turnspeed(self):
        """Test get_turnspeed method."""
        self.dial.get_turnspeed()
        self.dial._get_property.assert_called_once_with(
            self.dial.PropertyType.TURNSPEED
        )


if __name__ == "__main__":
    unittest.main()