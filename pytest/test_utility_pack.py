import logging, os, sys
import pandas as pd

severity_level = logging.DEBUG
logger = logging.getLogger(__name__)
FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
logging.basicConfig(format=FORMAT)
logger.setLevel(severity_level)

def relative_import(rootdir:str) -> None:
    """
    Finds directory that contains root directory `rootdir` and adds it to ``PYTHONPATH``.
    """

    current_path = os.path.dirname(os.path.abspath(__file__))

    current_path_list = current_path.split("/")

    rootdir_index = current_path_list.index(rootdir)

    rootdir_path_list = [x for x in current_path_list if current_path_list.index(x) < rootdir_index]

    rootdir_path = "/".join(rootdir_path_list)


    logger.debug(f"cwd\t{current_path}")
    logger.debug(f"path string into list\t{current_path_list}")
    logger.debug(f"rootdir index in list\t{rootdir_index}")
    logger.debug(f"rootdir path list\t{rootdir_index}")
    logger.debug(f"rootdir path\t{rootdir_path}")

    sys.path.append(rootdir_path)
    logger.debug(f"{rootdir_path} is in sys.path = {rootdir_path in sys.path}")
relative_import("utility_pack")
from utility_pack.main import CaseCorrection, ManageTestFiles

def adjust_to_directory(path:str):
    if not path.endswith("/"):
        path += "/"
    return path

def create_marker(path:str):

    path = adjust_to_directory(path)

    try:
        with open(f"{path}testmarker", "x") as file:
            file.write("")
    except FileExistsError:
        pass

def remove_marker(path:str):

    path = adjust_to_directory(path)

    try:
        os.remove(f"{path}testmarker")
    except FileNotFoundError:
        pass

def check_for_marker(path:str) -> bool:

    path = adjust_to_directory(path)

    try:
        with open(f"{path}testmarker", "r") as file:
            file.read()
        return True
    except FileNotFoundError:
        return False

class TestCaseCorrection():

    def test_list_case_correction_with_list(self):

        test_object = ["tEste", "abilidebob"]
        reference_object = ["Teste", "abilidebob"]

        test = CaseCorrection(test_object)
        corrected_object = test.correct(reference_object)

        assert corrected_object == ["Teste", "abilidebob"]

    def test_list_case_correction_with_tuple(self):

        test_object = ["tEste", "abilidebob"]
        reference_object = ("TestE", "abiliDEbob")

        test = CaseCorrection(test_object)
        corrected_object = test.correct(reference_object)

        assert corrected_object == ["TestE", "abiliDEbob"]

    def test_DataFrame_case_correction_with_tuple(self):

        test_object = pd.DataFrame({"tEste":[1,2,3], "abilidebob":[4,5,6]})
        reference_object = ("TestE", "AbiliDEbob")

        test = CaseCorrection(test_object)
        corrected_object = test.correct(reference_object)

        assert corrected_object.equals(pd.DataFrame({"TestE":[1,2,3], "AbiliDEbob":[4,5,6]}))

    def test_DataFrame_case_correction_with_list(self):

        test_object = pd.DataFrame({"tEste":[1,2,3,6,2], "abilidebob":[4,5,6,6,11]})
        reference_object = ["TestE", "nfnfuewinfw", "wedwqe"]

        test = CaseCorrection(test_object)
        corrected_object = test.correct(reference_object)

        assert corrected_object.equals(pd.DataFrame({"TestE":[1,2,3,6,2], "abilidebob":[4,5,6,6,11]}))

    def test_DataFrame_case_correction_with_DataFrame(self):

        test_object = pd.DataFrame({"tEste":[1,2,3,6,2], "abilidebob":[4,5,6,6,11]})
        reference_object = pd.DataFrame({"tEstando":[1,2,3,6,2],"tESTe":[1,2,3,6,2], "abiLIDebob":[4,5,6,6,11]})

        test = CaseCorrection(test_object)
        corrected_object = test.correct(reference_object)

        assert corrected_object.equals(pd.DataFrame({"tESTe":[1,2,3,6,2], "abiLIDebob":[4,5,6,6,11]}))

class TestBaseManager():

    def test_create_in_unmarked_directory(self):

        path = "test_folder/"

        remove_marker(path)

        manager = ManageTestFiles(path)

        assert manager.create() == False

    def test_create_in_non_directory(self):

        path = "test_folder"

        create_marker(path)

        manager = ManageTestFiles(path)

        assert manager.create() == False

    def test_create_in_marked_directory(self):

        path = "test_folder/"

        create_marker(path)

        manager = ManageTestFiles(path)

        assert manager.create() == True

    def test_clear_unmarked_folder(self):

        path = "test_folder/"

        remove_marker(path)

        manager = ManageTestFiles(path)

        assert manager.clear_folder() == False

    def test_clear_marked_folder(self):

        path = "test_folder/"

        create_marker(path)

        manager = ManageTestFiles(path)

        assert manager.clear_folder() == True

    def test_testmarker_remais_after_clear(self):

        path = "test_folder/"

        create_marker(path)

        manager = ManageTestFiles(path)
        manager.clear_folder()

        assert check_for_marker(path) == True

if __name__ == "__main__":
    pass
