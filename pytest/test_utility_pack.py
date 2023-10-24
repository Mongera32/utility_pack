import logging, os
from utility_pack import ManageTestFiles, CaseCorrection
import pandas as pd

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
