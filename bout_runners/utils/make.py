"""
Contains the make class
"""

import inspect
import logging
from pathlib import Path
from bout_runners.utils.subprocesses_functions import run_subprocess
logger = logging.getLogger(__name__)


# FIXME: We might need the exec_name elsewhere, as the executable is
#        needed for a run


class MakeError(Exception):
    """
    Error class indicating that this is a Make error
    """
    pass


class MakeProject(object):
    """
    The make class is responsible for making the project

    Methods
    -------

    Examples
    --------

    """

    def __init__(self,
                 make_file_root_path=None,
                 exec_name=None,
                 force=False):
        """
        Calls the make file of the make_file_root_path

        Parameters
        ----------
        make_file_root_path : None or Path or str
            Root path of make file
            If None, the path of the root caller of MakeProject will
            be called
        exec_name : None or str
            Name of the resulting executable.
            This is used to check if the program has been made
            If None the class will search for *.o file, and infer the
            name from the first *.o file found.
            The executable will not be made if a file is found,
            unless force is set to True
        force : bool
            Will make the make file if True, even if an executable
            exists
        """

        if make_file_root_path is None:
            # Assume that the make_file_root_path is located in the
            # caller directory
            frame = inspect.stack()[1]
            module = inspect.getmodule(frame[0])
            make_file_root_path = Path(module.__file__).parent

        self.make_file_root_path = Path(make_file_root_path)

        # FIXME: Don't have print statements
        if force:
            print('Force make')
        else:
            if exec_name is not None:
                exec_name = self._get_exec_name()
            if not self._exec_exist(exec_name):
                print('Did not find any possible executable name for '
                      'the project')

    def _run_make(self):
        """
        Make cleans and makes the .cxx program
        """

        logger.info("Make clean previously compiled code")
        command = "make clean"
        run_subprocess(command, self.make_file_root_path)
        logger.info("Making the .cxx program")
        command = "make"
        run_subprocess(command, self.make_file_root_path)
