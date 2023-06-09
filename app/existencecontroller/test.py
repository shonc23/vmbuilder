"""
Test file for controller.
To launch these tests, add first
$export PYTHONPATH="${PYTHONPATH}:/path-to-app/
"""
import constants
import os
import random
import string
import unittest
from argparse import Namespace
from existencecontroller.controller import VagrantController, PackerController
from existencecontroller.errors import (
    FileExtesionError,
    ExistenceProjectError
)


def generate_new_name_in(folder_path: str):
    """Generate and return a string which mock the name
    of a file or folder that does not exist in the given
    folder
    """
    name_in_folder = False
    while not name_in_folder:
        random_file_name = f"""{''.join(
            random.choices(string.ascii_lowercase, k=5)
        )}"""
        if random_file_name not in os.listdir(folder_path):
            name_in_folder = True
    return random_file_name


class VagrantControllerTest(unittest.TestCase):

    def test_check_json_existence(self):
        """Test that if selected JSON does not exist, then a new JSON
        file with the given name and a warning is printed in terminal
        """
        namespace = Namespace()
        json_file_name = f'{generate_new_name_in(constants.VAGRANT_PROVS_CONFS_PATH)}.json'
        namespace.json = json_file_name
        controller = VagrantController(namespace=namespace)
        try:
            with self.assertLogs(level='WARNING'):
                controller.check_json_existence()
        except SystemExit:
            pass

        self.assertIn(
            json_file_name,
            os.listdir(constants.VAGRANT_PROVS_CONFS_PATH)
        )
        os.remove(f'{constants.VAGRANT_PROVS_CONFS_PATH}/{json_file_name}')

    def test_json_extension(self):
        """Test that an error is raised when a JSON file has not the proper
        json extension
        """
        namespace = Namespace()
        json_file_name = generate_new_name_in(constants.VAGRANT_PROVS_CONFS_PATH)
        namespace.json = f'{json_file_name}.js'
        controller = VagrantController(namespace=namespace)
        with self.assertRaises(FileExtesionError):
            controller.check_json_existence()

    def test_check_new_project_folder_existence(self):
        """Test that if you create a project with a used name, then an error
        is raised"""
        new_project_name = generate_new_name_in(constants.VAGRANT_MACHINES_PATH)
        os.mkdir(f'{constants.VAGRANT_MACHINES_PATH}/{new_project_name}')
        namespace = Namespace()
        namespace.name = new_project_name
        controller = VagrantController(namespace=namespace)
        with self.assertRaises(ExistenceProjectError):
            controller.check_new_project_folder_existence()
        os.rmdir(f'{constants.VAGRANT_MACHINES_PATH}/{new_project_name}')


class PackerControllerTest(unittest.TestCase):

    def test_check_json_existence(self):
        """Test that if selected JSON does not exist, then a new JSON
        file with the given name and a warning is printed in terminal
        """
        namespace = Namespace()
        json_file_name = f'{generate_new_name_in(constants.PACKER_PROVS_CONFS_PATH)}.json'
        namespace.json = json_file_name
        controller = PackerController(namespace=namespace)
        try:
            with self.assertLogs(level='WARNING'):
                controller.check_json_existence()
        except SystemExit:
            pass

        self.assertIn(
            json_file_name,
            os.listdir(constants.PACKER_PROVS_CONFS_PATH)
        )
        os.remove(f'{constants.PACKER_PROVS_CONFS_PATH}/{json_file_name}')

    def test_json_extension(self):
        """Test that an error is raised when a JSON file has not the proper
        json extension
        """
        namespace = Namespace()
        json_file_name = generate_new_name_in(constants.PACKER_PROVS_CONFS_PATH)
        namespace.json = f'{json_file_name}.js'
        controller = PackerController(namespace=namespace)
        with self.assertRaises(FileExtesionError):
            controller.check_json_existence()

    def test_check_new_project_folder_existence(self):
        """Test that if you create a project with a used name, then an error
        is raised"""
        new_project_name = generate_new_name_in(constants.PACKER_MACHINES_PATH)
        os.mkdir(f'{constants.PACKER_MACHINES_PATH}/{new_project_name}')
        namespace = Namespace()
        namespace.name = new_project_name
        controller = PackerController(namespace=namespace)
        with self.assertRaises(ExistenceProjectError):
            controller.check_new_project_folder_existence()
        os.rmdir(f'{constants.PACKER_MACHINES_PATH}/{new_project_name}')


if __name__ == '__main__':
    unittest.main()
