import logging, os, sys
import pandas as pd
from colorama import Fore

severity_level = logging.DEBUG
logger = logging.getLogger(__name__)
FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
logging.basicConfig(format=FORMAT)
logger.setLevel(severity_level)

def append_syspath(rootdir:str) -> None:
    """
    Finds directory that contains root directory `rootdir` and adds it to `sys.path` list.
    """
    # Creating string with absolute path to current working directory.
    current_path = os.path.dirname(os.path.abspath(__file__))
    # Splitting path string and creating a list with split elements.
    current_path_list = current_path.split("/")
    # Finding index of rootdir in the list
    rootdir_index = current_path_list.index(rootdir)
    # creating a list without rootdir and It's subdirectories.
    rootdir_path_list = [x for x in current_path_list if current_path_list.index(x) < rootdir_index]
    # joining list elements in a new string
    rootdir_parent_path = "/".join(rootdir_path_list)

    logger.debug(f"appending {rootdir_parent_path} to {Fore.GREEN + 'sys' + Fore.RESET}.{Fore.CYAN + 'path' + Fore.RESET}")
    logger.debug(f"{Fore.GREEN + 'sys' + Fore.RESET}.{Fore.CYAN + 'path' + Fore.RESET} list: {str(sys.path)}")

    sys.path.append(rootdir_parent_path)
    logger.info(f"{Fore.YELLOW + rootdir_parent_path + Fore.RESET} has been added to {Fore.GREEN + 'sys' + Fore.RESET}.{Fore.CYAN + 'path' + Fore.RESET} list.")
    logger.debug(f"{Fore.YELLOW + rootdir_parent_path + Fore.RESET} is in sys.path = {Fore.BLUE + str(rootdir_parent_path in sys.path) + Fore.RESET}")
append_syspath("utility_pack")
from utility_pack import CaseCorrection, DemoFileGenerator, FileSafetyException

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
        logger.warning(f"testmarker file already exists at {Fore.BLUE + path + Fore.RESET}.")

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

class TestBaseFileGenerator():

    def test_create_in_unmarked_directory(self):

        path = "test_folder/"

        remove_marker(path)

        try:
            manager = DemoFileGenerator(path)
            manager.create()
        except FileSafetyException:
            pass

    def test_create_in_non_directory(self):

        path = "test_folder"

        create_marker(path)

        try:
            manager = DemoFileGenerator(path)
            manager.create()
        except NotADirectoryError:
            pass

    def test_clear_unmarked_directory(self):

        path = "test_folder/"

        remove_marker(path)

        try:
            manager = DemoFileGenerator(path)
            manager.clear_folder()
        except FileSafetyException:
            pass

    def test_clear_marked_directory(self):

        path = "test_folder/"

        create_marker(path)

        manager = DemoFileGenerator(path)
        manager.clear_folder()

    def test_testmarker_remais_after_clear(self):

        pass

if __name__ == "__main__":
    pass
