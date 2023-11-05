from pandas import DataFrame
from typing import Union
import logging, os, shutil, sys
from colorama import Fore
import random
#from prettytable import PrettyTable
import pandas as pd
from datetime import datetime
import numpy as np

############################################################################
# logging config  #
############################################################################

severity_level = logging.DEBUG
logger = logging.getLogger(__name__)
FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
logging.basicConfig(format=FORMAT)
logger.setLevel(severity_level)

############################################################################
# Debug support #
############################################################################

#class VariableInspector(PrettyTable):
#
#    def __init__(self, *args:list[str,str], **kwargs) -> None:
#        """
#        Returns a VariableInspector instance. Insert variables as *args.
#        """
#        # Calling parent __init__
#        field_names = ["Name","Value"]
#        super().__init__(field_names, **kwargs)
#
#        # Adding variables
#        for row in args:
#            row[1] = str(row[1])
#            logger.debug(f"row being added: {row}")
#            self.add_row(row)

#    def caller(self):
#        curframe = inspect.currentframe()
#        calframe = inspect.getouterframes(curframe, 3)
#        print(F"\n{Fore.YELLOW} CALLER NAME: {calframe[1][3] + Fore.RESET}")

#    def table(self):
#        print(f"\n{Fore.YELLOW} VARIABLE REPORT TABLE {Fore.GREEN} \n\n {self.get_string() + Fore.RESET}")

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

    sys.path.append(rootdir_parent_path)
    logger.info(f"{Fore.YELLOW + rootdir_parent_path + Fore.RESET} has been added to {Fore.GREEN + 'sys' + Fore.RESET}.{Fore.CYAN + 'path' + Fore.RESET} list.")
    logger.debug(f"{Fore.YELLOW + rootdir_parent_path + Fore.RESET} is in sys.path = {Fore.BLUE + str(rootdir_parent_path in sys.path) + Fore.RESET}")

############################################################################
# Custom Exceptions  #
############################################################################

class FileSafetyException(Exception):
    """Raised when a risk of data loss or data exposure is detected."""
    pass

############################################################################
# Classes  #
############################################################################

class CaseCorrection():

    def __init__(self,
                 _object:Union[str,list,tuple,DataFrame]):
        """

        Arguments:
            - `_object`: str, list or pd.DataFrame to be corrected
        """

        logger.debug(f'Instantiating object')
        self._object = _object
        self.tuple_or_string_to_list()

    def __str__(self) -> str:
        return self.object_report()

    def correct(self, reference:Union[tuple,list,DataFrame]) -> Union[DataFrame,list]:
        """Applies case corrections according to reference parameter"""

        # checking if reference is a dataframe and converting to list if needed
        logger.debug(f'Old reference object {reference}')
        reference = correction_labels_to_list(reference)
        logger.debug(f'New reference object {reference}')

        # creating mapper dict for conversion
        logger.debug(f'Creating mapper based on reference')
        mapper = self.create_mapper(reference)
        logger.debug(f'Created mapper: {mapper}')

        # applying correction
        self.correction_handler()

        return self.corrected_object

    def correction_handler(self):
        """Calls the adequate correction method according to _object type."""

        if type(self._object) == list:
            self.list_case_correct()
        elif type(self._object) == DataFrame:
            self.dataframe_case_correct()
        else:
            self.corrected_object = None

    def object_report(self) -> str:
        """Provides insights on the objects attributes"""

        report_list = []

        type_report = f'type: {type(self._object)}'
        report_list.append(type_report)


        try: length_report = f"Length: {len(self._object)}"
        except: length_report = 'Does not apply'
        report_list.append(length_report)

        try:
            content_list = []
            for i in self._object:
                if type(self._object) == dict:
                    content_list.append(f'{i}({type(i)}):{self._object[i]}({type(self._object[i])})')
                else:
                    content_list.append(f'{i}({type(i)})')
                if len(content_list) > 5: break

            content_report = "Content: " + ', '.join(content_list)
        except: content_report = 'Content: Does not apply'

        report_list.append(content_report)

        report = '\n'.join(report_list)

        return report

    def tuple_or_string_to_list(self) -> None:
        """If _object is a tuple, turns it into a list. Else, creates a list with x as it's only object. """
        logger.debug(f'Checking object type')
        if type(self._object) == tuple:
            logger.debug(f'Object is a tuple. Converting tuple {self._object} into list')
            self._object = list(self._object)
            logger.debug(f'Tuple converted into list: {self._object}')
        elif type(self._object) == str:
            logger.debug(f'Object is a string. Converting single string {self._object} into list')
            self._object = [self._object]
            logger.debug(f'String converted into list {self._object}')
        logger.debug(f'Object is a {type(self._object)}. No conversion done. Object value is {self._object}')

    def unify_list(self, nested_list):
        """
        !DEPRECATED!

        Transforms a nested list into a a single list

        Arguments:
        nested_list: list in which objects may or may not be lists

        Returns: A non-nested list containing the all objects from nested_list and from the lists the were inside it
        """

        new_list = []
        for object in nested_list:
            try:
                for sub_object in object:
                    new_list.append(sub_object)
            except TypeError:
                new_list.append(object)

        return new_list

    def string_list_lower(self):
        """Converts all strings in string_list to lower case.

        Args:
            string_list (list): List of strings.

        Returns:
            string_list with all strings converted to only lower case.
        """

        logger.debug(f"checking and creating lower case strings list")
        logger.debug(f"Original string list: {self._object}")
        strings_lower = [string.lower() for string in self._object]
        logger.debug(f"lower case string list: {strings_lower}")

        return strings_lower

    def case_insensitive_string_check(self, str1:str, str2:str):
        """Checks if two strings are equal with a case insensitive method."""
        str1_l = str1.lower()
        str2_l = str2.lower()

        if str1_l == str2_l: return True
        return False

    def dataframe_check(self) -> list:
        """returns list with column labels if self._object is a DataFrame. Otherwise, returns self._object unaltered."""

        logger.debug(f'Checking if object is a DataFrame.')
        if type(self._object) == DataFrame:
            list_of_labels = list(self._object.columns)
            logger.debug(f'DataFrame detected. Returnling list of labels: {list_of_labels}')
            return list_of_labels

        logger.debug(f'Not a DataFrame. Returning object unaltered: {self._object}')
        return self._object

    def create_mapper(self, reference) -> dict:
        """Creates a mapper object for correction of strings list. Mapper keys are strings to be corrected in original list and mapper values are the corrected version of the string."""

        logger.debug(f'Creating mapper object')
        case_correction_mapper = {}

        _object = self.dataframe_check()

        for key in _object:
            for value in reference:
                logger.debug(f'Comparing list component {key} with reference list component {value}')
                if self.case_insensitive_string_check(key,value) and key != value:
                    logger.debug(f'Adding {key}:{value} to mapper')
                    case_correction_mapper[key] = value
        logger.debug(f'Mapper created: {case_correction_mapper}')

        self.mapper = case_correction_mapper

        return case_correction_mapper

    def list_case_correct(self) -> None:
        """
        Checks if any of the strings in original_list are equal to any of the strings in the reference list, except for lowercase/uppercase inconsistencies.
        Corrects any of those inconsistencies.

        Returns corrected original_list.
        """
        new_list = []

        mapper = self.mapper

        for string in self._object:
            if string in mapper:
                new_list.append(mapper[string])
            else:
                new_list.append(string)

        self.corrected_object = new_list

    def dataframe_case_correct(self) -> None:
        """
        Checks if any of the column labels are equal to any of the column names in the DataFrame, except for lowercase/uppercase inconsistencies.
        Corrects any of those inconsistencies.

        Arguments:
        df: DataFrame that will have it's columns checked.
        args: strings or nested lists|tuples of strings that will be used as reference to correct the DataFrame labels.

        Returns corrected DataFrame
        """
        df = self._object
        logger.debug(f'df being used: {df}')

        if type(df) != DataFrame:
            logger.error(f'Object is not of DataFrame type. Could not apply corrections')
            return None

        logger.debug(f'Renaming DataFrame columns')
        logger.debug(f'Old column names: {df.columns}')
        df.rename(columns = self.mapper, inplace = True)
        logger.debug(f'New column names: {df.columns}')

        self.corrected_object = df

class DataFormatting():

    def __init__(self, data) -> None:
        self.data = data

    def __str__(self) -> str:
        return self.data

    def rm_extension(self) -> None:
        """Data must be a string. Removes the extension from a string that represents a file name. If there is no extension, nothing is changed."""

        if type(self.data) != str:
            logger.error(f'data type is {type(self.data)}. Must be a string')
            return None

        new_name = self.data.partition(".")[0]

        self.data = new_name

    def value_string(df:DataFrame,index:int):
        """
        ! DEPRECATED !

        Transforms a row of the dataframe into a string compatible with the INSERT INTO SQL statement
        - df: DataFrame with the data to be turned into string
        - index: index of the column to be turned into string
        """

        # Extracting dataframe row into a list
        data_list = df.values.tolist()[index]

        # Converting values when necessary to fit the SQL syntax
        data_list_upd = []
        for value in data_list:
            if type(value) == bool:
                if value == True: data_list_upd.append('1')
                elif value == False: data_list_upd.append('0')
            elif type(value) == str:
                #if re.search('[a-zA-Z]',value) == None:
                #    data_list_upd.append(f'CONVERT(DATETIME,\'{value}\')')
                if len(value) == 36:
                    data_list_upd.append(f'CAST(\'{value}\' AS uniqueidentifier)')
                elif value == 'False':
                    data_list_upd.append('0')
                elif value == 'True':
                    data_list_upd.append('1')
            else:
                data_list_upd.append(str(value))

        sql_values = ', '.join(data_list_upd)
        return sql_values

    def cols_string(df:DataFrame):
        """
        ! DEPRECATED !

        Turns the df columns into a string compatible with the INSERT INTO SQL statement

        df: DataFrame to be used to create the string.
        """

        cols = ", ".join([str(i) for i in df.columns.tolist()])
        return cols

    def create_insert_into_statement(df:DataFrame):
        """! DEPRECATED !

        Creates a string with an INSERT INTO stament for evey row in the DataFrame
        """

        cols = DataFormatting.cols_string(df)

        sql = ''
        for index, row in df.iterrows():
            sql += f'INSERT INTO tbCenarioLimites ({cols}) VALUES ({DataFormatting.value_string(df,index)}); '

        return sql

    def create_data_list(self) -> list:
        """
        Data must be DataFrame type

        Creates a list of tuples from the the df. Tuples represent rows; objects in a tuple represent a cell.

        Returns:
        list: Every tuple represents a row in the input DataFrame.
        """
        logger.debug(f"Creating data list from {self.data}")

        if type(self.data) != DataFrame:
            raise TypeError(f"self.data is {type(self.data)}. Must be a DataFrame.")

        df = self.data

        for col in df.columns:

            if col in ("insertOrder", "insertorder"):
                df.drop(columns = col, inplace = True)

            elif col == "dtCenario":
                current_datetime = datetime.now().isoformat()
                current_datetime = current_datetime.replace("T", " ")
                current_datetime = current_datetime.split('.')[0]
                df[col] = current_datetime

            elif df[col].dtype == "object":
                continue

            else:
                df[col] = df[col].map(df_to_sql)

        data_list = []
        for row in df.itertuples(index = False, name = None):
            data_list.append(row)

        logger.debug(f"Created data list: {data_list}")

        return data_list

class DemoFileGenerator():
    """
    Manages creation and deletion of files for test purposes. `path` argument must be a directory path and must contain
    a file named `testmarker`, otherwise the `safety_lock()` method will engage and stop any class method that gets
    executed before it's able to change any files.

    Main class methods:
    - `create()`: Creates a `.csv` file in the directory specified by `self.path`.
    - `show_test_file()`: Displays test file saved in `self.path`

    """

    def __init__(self,
                 path:str = "",
                 file_name:str = "demofile",
                 ext:str = "csv",
                 multiple_files:bool = False,
                 header = "file header\n",
                 lines = "file line ",
                 line_number = 1
) -> None:

        self.set_path(path)

        self.file_name = file_name
        self.header = header
        self.lines = lines
        self.ext = ext
        self.line_number = line_number
        self.multiple_files = multiple_files
        self.file_counter = 0

        logger.info("setup finished.")

    def create(self, show = False) -> None:
        """Creates a test file in the directory specified by ``self.path``. returns True if operation was successful and False otherwise."""

        try:
            self.creation_block()
        except FileNotFoundError:
            logger.warning(f"Directory {self.path} does not exist. Defaulting to current working directory.")

            # setting path to cwd
            self.set_path("")

            # creating/overriding file
            self.creation_block()

        # creating line list of one doesn't exist already
        if not hasattr(self,"line_list"):
            logger.debug(f"{Fore.BLUE}self.line_list{Fore.RESET} does not exist. Calling {Fore.BLUE}self{Fore.RESET}.{Fore.YELLOW}standard_line_list(){Fore.RESET}.")
            self.standard_line_list()
        else:
            logger.debug(f"{Fore.BLUE}self.line_list{Fore.RESET} exists. Skipping {Fore.BLUE}self{Fore.RESET}.{Fore.YELLOW}standard_line_list(){Fore.RESET}.")

        # inserting lines
        self.input_lines()

        if show:
            self.show_test_file()

    def file_opener(self, mode:str):
        """Calls ``open()`` function and passes the `mode` argument."""
        if self.multiple_files:
            full_path = f"{self.file_name}{self.file_counter}.{self.ext}"
        else:
            full_path = f"{self.file_name}.{self.ext}"

        logger.debug(f"self.multiple_files is {self.multiple_files}. Full file path is {full_path}.")
        logger.debug(f"Accessing file {full_path} in {mode} mode.")
        return open(full_path, mode)

    def creation_block(self):
        """Basic bulding block for creating or overriding the file."""

        if self.multiple_files:
            self.file_counter += 1
            logger.debug(f"Increasing {Fore.BLUE}file_counter{Fore.RESET}. New value: {self.file_counter}")

        try:
            with self.file_opener("x") as f:
                f.write(self.header)
        except FileExistsError:
            logger.debug(f"File already exists. Overriding.")
            with self.file_opener("w") as f:
                f.truncate(0)
                f.write(self.header)

    def show_test_file(self):
        """Reads and prints the test file on ``self.path``."""

        with self.file_opener("r") as f:
            print(f"\nReading file on path {Fore.YELLOW + self.path + Fore.RESET}:\n")
            print(f.read())

    def standard_line_list(self):
        """Creates a list of file lines according to standard parameters."""

        counter = 0
        line_list = []
        while counter <= self.line_number:
            line_list.append(self.lines + str(counter))
            counter += 1

        self.line_list = line_list

    def input_lines(self):
        """Insertes strings in self.line_list into file."""

        logger.debug("Inserting lines in files")
        with self.file_opener("a") as f:
            for line in self.line_list:
                logger.debug(f"Inserting line {line}")
                f.write("\n" + line)

    def set_path(self, newpath:str) -> None:
        """Checks if chosen path contains the ``testmarker`` file. Sets ``self.path = newpath`` if
        and only if this check is successful."""

        # making list of files in newpath
        if newpath.endswith("/"):
            newpath = newpath[:-1]

        if newpath == "":
            logger.warning(f"{Fore.BLUE}newpath{Fore.RESET} string empty. defaulting to current working directory.")
            newpath = os.getcwd()

        if os.path.isdir(newpath):
            dir_list = os.listdir(newpath)
            logger.debug(f"files in directory: {dir_list}")
        else:
            raise NotADirectoryError(f"path {Fore.GREEN + newpath + Fore.RESET} points to a file, but should point to a directory instead.")

        logger.debug(f"Files in {newpath}: {dir_list}")
        try:
            self.newpath_check(newpath)
        except FileNotFoundError:
            logger.warning(f"path {Fore.YELLOW + newpath + Fore.RESET} not found. Defaulting to current working directory.")
            newpath = os.getcwd()
            self.newpath_check(newpath)

    def newpath_check(self, newpath:str) -> None:
        """Verifies if newpath is valid directory that is marked as a test area. If the Check passes, saves
        it as self.newpath and returns warningmessages otherwise."""

        if not newpath.endswith("/"):
            newpath += "/"

        logger.debug(f"Setting test file path to {Fore.GREEN + newpath + Fore.RESET}")

        proj_root = os.getcwd()

        dir_list = os.listdir(proj_root + "/" + newpath)
        if "testmarker" not in dir_list:
            raise FileSafetyException(f"""

        {Fore.GREEN + newpath + Fore.RESET} directory is {Fore.RED}NOT{Fore.RESET} marked as a testing area. Cancelling operation for safety reasons.

        To mark this directory as a testing area, create a file named {Fore.BLUE}testmarker{Fore.RESET} in it.
""")
        logger.info(f"{Fore.YELLOW + newpath + Fore.RESET} verified as test area. Proceeding with setup.")

        self.path = newpath

    def clear_folder(self) -> None:
            """Deletes all files in the specified directory."""

            # Checking if directory is marked as a test area.

            logger.info(f"{Fore.RED}Wiping all files in {self.path + Fore.RESET}")

            dir_list = os.listdir(self.path)

            for file_name in dir_list:
                file_path = os.path.join(self.path, file_name)
                try:
                    if file_name == "testmarker":
                        continue
                    elif os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print('Failed to delete %s. Reason: %s' % (file_path, e))

            logger.info(f"{Fore.RED}Directory {self.path} has been wiped clean.{Fore.RESET}")

class CsvDemoFileGenerator(DemoFileGenerator):

    def __init__(self,
                 path:str = "",
                 file_name:str = "",
                 multiple_files:bool = False,
                 column_number = 5,
                 line_number = 5
    ) -> None:
        DemoFileGenerator.__init__( self,
                                    path = path,
                                    file_name = file_name,
                                    ext = "csv",
                                    multiple_files = multiple_files,
                                    line_number = line_number
)
        self.column_number = column_number

    def create_csv(self, path:str):
        """Create test csv file according to attributes. Saves it at `path`"""

        df_dict = {}
        while len(df_dict) < self.column_number:

            line = []
            while len(line) < self.line_number:
                line.append(random.randint(1,10))

            col_name = f"col{len(df_dict)}"
            df_dict[col_name] = line

        df = pd.DataFrame(df_dict)

        df.to_csv(path,index=False)

    def csv_line_list(self):
        """Creates files header according to desired number of columns."""

        line_list = []
        line_counter = 0
        while line_counter <= self.line_number:
            line = ''
            column_counter = 0
            while column_counter <= self.column_number:
                rand_number = str(random.randint(1,20))
                logger.debug(f"Adding random number to line: {rand_number}")
                line += rand_number
                line += ","
                column_counter += 1
            line = line[:-1]
            line_list.append(line)
            logger.debug(f"New line list: {line_list}")
            line_counter += 1

        logger.debug(f"Line list created: {line_list}")
        self.line_list = line_list

    def csv_header(self):
        """Creates a header line for a ``.csv`` file"""

        header = ""
        counter = 0
        while counter <= self.column_number:
            header += f"col{counter}"
            header += ","
            counter += 1
        header = header[:-1]

        self.header = header
        return

############################################################################
# Functions  #
############################################################################

def contains_column(df:DataFrame, col:str):
    """Checks if DataFrame `df` contains any of the labels in list `cols`."""

    df_col_list = list(df.columns)

    if col in df_col_list:
        return True

    return False

def create_marker(path:str):

    confirmation = input(f"\n{Fore.RED + ' !! WARNING !!' + Fore.RESET}\nYou are about to mark a directory as a testing area, which will put all files in it at risk of being deleted or modified.\nPlease 'AGREE' to confirm that you wish to proceed:\n\n ")

    if confirmation != "AGREE":
        raise FileSafetyException("Confirmation invalid. Cancelling operation.")

    try:
        with open(f"{path}/testmarker", "x") as file:
            file.write("")

    except FileExistsError:
        logger.warning(f"testmarker file already exists at {Fore.YELLOW + path + Fore.RESET}.")

def remove_marker(path:str):

    if path.endswith("/"):
        path = path[:-1]

    try:
        os.remove(f"{path}/testmarker")
    except FileNotFoundError:
        pass

def check_for_marker(path:str) -> bool:

    try:
        with open(f"{path}testmarker", "r") as file:
            file.read()
        return True
    except FileNotFoundError:
        return False

def obj_report(_obj):
    """logs a report with information from _obj parameter"""
    obj_type = str(type(_obj))

    if type(_obj) in (str,int,float):
        obj_value = str(_obj)
    elif type(_obj) in (tuple, list, DataFrame, dict):
        obj_value = str(len(_obj))
    else:
        obj_value = "-Could not be determined-"


    report_str = f"""object report:\n
                     Type\t{obj_type}\n
                     Value\t{obj_value}


                     """

    logger.debug(report_str)

    return report_str

def list_of_keys(_dict:dict) -> list:
    """Creates a list with the keys from _dict"""
    _list = []
    for key in _dict:
        _list.append(key)
    return _list

def float_check(x) -> bool:
    """Returns True if data is a float with only zeros in the decimal place. Returns False otherwise."""

    if type(x) != float:
        logger.debug("Data is not a float")
        return False
    if int(x) == x:
        logger.debug("Data is a float with only zerosin the decimal place")
        return True

    return False

def df_to_sql(x:Union[str,int,float]) -> str :
    """
    Turns x into a string that can be inserted in a SQL query.
    To be used in a list comprehension in the create_data_list() function.

    x: object to be modified and/or converted into a string type.
    """

    try:

#        if x in ('[NULL]', 'None'):
#            return None
        if type(x) == bool:
            if x == True: return '1'
            elif x == False: return '0'
        if float_check(x):
            return int(x)
        if type(x) == np.nan:
            return None

    except ValueError:
        return str(x)

    return str(x)

def correction_labels_to_list(reference):
    """Converts reference parameter to list in case it is a DataFrame.

    Arguments:
        - reference (tuple | list | DataFrame): parameter to be converted.
        - - If tuple, function will a list with the same elements.
        - - If List, function returns it unchanged.
        - - If DataFrame, returns list of DataFrame labels.

    Returns a List as per reference argument discription.
    """

    if type(reference) == DataFrame:
        logger.debug(f'Correction object is a DataFrame. Extracting list of labels')
        df = reference
        reference = list(df.columns)
    elif type(reference) == tuple:
        reference = list(reference)
    else:
        logger.debug(f'reference object is not a DataFrame. No changes made')

    return reference

def dplcheck(collection) -> bool:
    """Checks of `collection` object contains any duplicated value. Returns ``True`` if so, and `False` otherwise."""

    _set = set(collection)

    if len(_set) == len(collection):
        return True

    return False

def dict_dplcheck(_dict:dict) -> bool:
    """Checks if `_dict` contains any duplicated values. Returns `True` if any duplicated value is found and
    `False otherwise.`"""

    keys = _dict.keys()

    # retornar valor de cada chave e criar uma lista
    values = [_dict[key] for key in keys]

    result = dplcheck(values)

#    inspector = VariableInspector(["keys",keys],
#                                  ["values",values],
#                                  ["result",result]
#)
#    logger.debug(inspector.caller())
#    logger.debug(inspector.table())

    return result

if __name__ == "__main__":
    df1 = pd.DataFrame({1:[1,2,3],
                        2:[1,None,3]
})
    formatter = DataFormatting(df1)

    result = formatter.create_data_list()

    print(df1)
