"""
Tests for primavera_viewer
"""
import unittest
from iris.tests.stock import realistic_3d
from primavera_viewer.nearest_location import *

class TestPointLocation(unittest.TestCase):

    def setUp(self):
        self.stock_cube = realistic_3d()
        self.stock_cube.coord('grid_latitude').guess_bounds()
        self.stock_cube.coord('grid_longitude').guess_bounds()

    def test_find_point_general_case(self):
        """
        Tests general case of single point within coordinate system
        """
        self.test_cube = PointLocation(lat=-1.51,lon=3.78,cube=self.stock_cube)
        self.lat_coord = self.test_cube.find_point().coord('latitude')
        self.lon_coord = self.test_cube.find_point().coord('longitude')
        self.assertEqual([self.lat_coord.points[0], self.lon_coord.points[0]],
                         [-2.0, 4.0])

    def test_find_point_on_boundary_case(self):
        """
        Tests case of single point on boundary between points within coordinate
        system
        """
        self.test_cube = PointLocation(lat=-2.5,lon=3.5,cube=self.stock_cube)
        self.lat_coord = self.test_cube.find_point().coord('latitude')
        self.lon_coord = self.test_cube.find_point().coord('longitude')
        self.assertEqual([self.lat_coord.points[0], self.lon_coord.points[0]],
                         [-2.0, 4.0])

class TestAreaLocation(unittest.TestCase):

    def setUp(self):
        self.stock_cube = realistic_3d()
        self.stock_cube.coord('grid_latitude').guess_bounds()
        self.stock_cube.coord('grid_longitude').guess_bounds()

    def test_find_area_general_case(self):
        """
        Tests general case of max/min definitions within coordinate system
        """
        self.test_cube = AreaLocation(lat_min=-2.92, lat_max = 1.63,
                                       lon_min=0.35, lon_max = 3.89,
                                       cube=self.stock_cube)
        self.lat_coord = self.test_cube.find_area().coord('latitude')
        self.lon_coord = self.test_cube.find_area().coord('longitude')
        print(self.lat_coord.points[0], self.lon_coord.points[0])
        self.assertEqual([self.lat_coord.points[0], self.lon_coord.points[0]],
                         [-0.5, 2.0])

    def test_find_area_on_boundary_case(self):
        """
        Tests case of max/min definitions on boundary between points within
        coordinate system.
        :return:
        """
        self.test_cube = AreaLocation(lat_min=-3.5, lat_max = 1.5,
                                       lon_min=0.5, lon_max = 4.5,
                                       cube=self.stock_cube)
        self.lat_coord = self.test_cube.find_area().coord('latitude')
        self.lon_coord = self.test_cube.find_area().coord('longitude')
        print(self.lat_coord.points[0], self.lon_coord.points[0])
        self.assertEqual([self.lat_coord.points[0], self.lon_coord.points[0]],
                         [-0.5, 3.0])

if __name__ == '__main__':
    unittest.main()