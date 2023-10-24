from pandas import DataFrame
from typing import Union
import logging, os, shutil
from utility_pack import ManageTestFiles


severity_level = logging.WARNING
logger = logging.getLogger(__name__)
FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
logging.basicConfig(format=FORMAT)
logger.setLevel(severity_level)

def create_marker(path:str):

    if not path.endswith("/"):
        path += "/"

    try:
        with open(f"{path}testmarker", "x") as file:
            file.write("")
    except FileExistsError:
        pass

def remove_marker(path:str):

    if not path.endswith("/"):
        path += "/"

    try:
        os.remove(f"{path}testmarker")
    except FileNotFoundError:
        pass

def check_for_marker(path:str) -> bool:

    if not path.endswith("/"):
        path += "/"

    try:
        with open(f"{path}testmarker", "r") as file:
            file.read()
        return True
    except FileNotFoundError:
        return False

#####################################

def test_create_in_unmarked_directory():

    path = "test_folder/"

    remove_marker(path)

    manager = ManageTestFiles(path)

    assert manager.create() == False

def test_create_in_non_directory():

    path = "test_folder"

    create_marker(path)

    manager = ManageTestFiles(path)

    assert manager.create() == False

def test_create_in_marked_directory():

    path = "test_folder/"

    create_marker(path)

    manager = ManageTestFiles(path)

    assert manager.create() == True

def test_clear_unmarked_folder():

    path = "test_folder/"

    remove_marker(path)

    manager = ManageTestFiles(path)

    assert manager.clear_folder() == False

def test_clear_marked_folder():

    path = "test_folder/"

    create_marker(path)

    manager = ManageTestFiles(path)

    assert manager.clear_folder() == True

def test_testmarker_remais_after_clear():

    path = "test_folder/"

    create_marker(path)

    manager = ManageTestFiles(path)
    manager.clear_folder()

    assert check_for_marker(path) == True

if __name__ == "__main__":
    pass
