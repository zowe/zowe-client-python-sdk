import sys
from zeepy import Zeepy
from zeepy.console import Console
from zeepy.files import Files
from zeepy.jobs import Jobs
from zeepy.tso import Tso
from zeepy.zosmf import Zosmf

import unittest
sys.path.append("..")
test_object = Zeepy('', '', '')


class TestZeepy(unittest.TestCase):

    def test_zeepy_object_created_is_of_zeepy_instance(self):
        self.assertIsInstance(test_object, Zeepy)

    def test_zeepy_successfully_creates_instance_of_console_object(self):
        self.assertIsInstance(test_object.console, Console)

    def test_zeepy_successfully_creates_instance_of_files_object(self):
        self.assertIsInstance(test_object.files, Files)

    def test_zeepy_successfully_creates_instance_of_jobs_object(self):
        self.assertIsInstance(test_object.jobs, Jobs)

    def test_zeepy_successfully_creates_instance_of_tso_object(self):
        self.assertIsInstance(test_object.tso, Tso)

    def test_zeepy_successfully_creates_instance_of_zosmf_object(self):
        self.assertIsInstance(test_object.zosmf, Zosmf)
