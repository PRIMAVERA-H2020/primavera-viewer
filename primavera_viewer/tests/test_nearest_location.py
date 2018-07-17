"""
Tests for primavera_viewer
"""

import iris
import unittest
from iris.tests.stock import realistic_3d
from primavera_viewer.nearest_location import *

from primavera_viewer.nearest_location import *

class TestPointLocation(unittest.TestCase):

    def setup(self):
        self.example_cube = realistic_3d()
        self.example_cube.coord('gird_latitude').guess_bounds()
        self.example_cube.coord('gird_latitude').guess_bounds()
        self.latitude = 1.13
        self.longitude = 1.45

    def test_find_point(self):
        test_point = PointLocation()