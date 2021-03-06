"""Contains the local submitter class."""


import logging

# NOTE: Subprocess below is safe against shell injections
# https://github.com/PyCQA/bandit/issues/280
import subprocess  # nosec
from pathlib import Path

from typing import Optional

from bout_runners.submitter.abstract_submitter import AbstractSubmitter
from bout_runners.submitter.processor_split import ProcessorSplit
from bout_runners.utils.file_operations import get_caller_dir


class LocalSubmitter(AbstractSubmitter):
    r"""
    Submits a command.

    FIXME: this has been updated
    FIXME: Add to abstract submitter

    Attributes
    ----------
    __pid : None or int
        Getter variable for pid
    __return_code : None or int
        Getter variable for return_code
    __std_out : None or str
        Getter variable for std_out
    __std_err : None or str
        Getter variable for std_err
    __path : Path or str
        Directory to run the command from
    __process : None or Popen
        The Popen process if it has been created
    processor_split : ProcessorSplit
        Object containing the processor split
    pid : None or int
        The processor id if the process has started
    return_code : None or int
        The return code if the process has finished
    std_out : None or str
        The standard output if the process has finished
    std_err : None or str
        The standard error if the process has finished

    Methods
    -------
    submit_command(command)
        Run a subprocess
    write_python_script(path, function, args, kwargs)
        Write python function to file
    completed()
        Return the completed status
    errored()
        Return True if the process errored
    raise_error(self)
        Raise and error from the subprocess in a clean way

    Examples
    --------
    >>> submitter = LocalSubmitter()
    >>> submitter.submit_command('ls')
    >>> while submitter.completed() is not True:
    >>>     pass
    >>> print(submitter.std_out)
    __init__.py
    test_local_submitter.py
    test_processor_split.py
    test_submitter_factory.py
    """

    def __init__(
        self,
        path: Optional[Path] = None,
        processor_split: Optional[ProcessorSplit] = None,
    ) -> None:
        """
        Set the path from where the calls are made from.

        Parameters
        ----------
        path : Path or str or None
            Directory to run the command from
            If None, the calling directory will be used
        processor_split : ProcessorSplit or None
            Object containing the processor split
            If None, default values will be used
        """
        # NOTE: We are not setting the default as a keyword argument
        #       as this would mess up the paths
        self.__path = Path(path).absolute() if path is not None else get_caller_dir()
        self.__process: Optional[subprocess.Popen] = None

        # Attributes with getters
        self.__pid: Optional[int] = None
        self.__return_code: Optional[int] = None
        self.__std_out: Optional[str] = None
        self.__std_err: Optional[str] = None

        self.processor_split = (
            processor_split if processor_split is not None else ProcessorSplit()
        )

    @property
    def pid(self) -> Optional[int]:
        """
        Return the process id.

        Returns
        -------
        self.__pid : int or None
            The process id if a process has been called, else None
        """
        return self.__pid

    @property
    def return_code(self) -> Optional[int]:
        """
        Return the return code.

        Returns
        -------
        self.__return_code : int or None
            The return code if the process has completed
        """
        return self.__return_code

    @property
    def std_out(self) -> Optional[str]:
        """
        Return the standard output.

        Returns
        -------
        self.__std_out : str or None
            The standard output
            None if the process has not completed
        """
        return self.__std_out

    @property
    def std_err(self) -> Optional[str]:
        """
        Return the standard error.

        Returns
        -------
        self.__std_err : str or None
            The standard error
            None if the process has not completed
        """
        return self.__std_err

    def submit_command(self, command: str) -> None:
        """
        Submit a subprocess.

        Parameters
        ----------
        command : str
            The command to run
        """
        self.__process = subprocess.Popen(
            command.split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=self.__path,
            # https://docs.python.org/3/library/subprocess.html#security-considerations
            # https://github.com/PyCQA/bandit/issues/280
            shell=False,  # nosec
        )
        self.__pid = self.__process.pid
        logging.info("pid %s given %s in %s", self.pid, command, self.__path)

    def wait_until_completed(self, raise_error: bool = True) -> None:
        """
        Wait until the process has completed.

        Parameters
        ----------
        raise_error : bool
            Whether or not to raise errors
        """
        if self.__process is not None:
            std_out, std_err = self.__process.communicate()
            self.__return_code = self.__process.poll()

            self.__std_out = std_out.decode("utf8").strip()
            self.__std_err = std_err.decode("utf8").strip()

            if self.return_code != 0:
                logging.error(
                    "Subprocess with pid %s failed with return code %s",
                    self.__process.pid,
                    self.return_code,
                )
                logging.error("stdout:")
                logging.error(self.std_out)
                logging.error("stderr:")
                logging.error(self.std_err)
                if raise_error:
                    self.raise_error()
            else:
                logging.info("pid %s has successfully completed", self.__process.pid)

    def completed(self) -> bool:
        """
        Return the completed status.

        Communicate the process has completed.

        Returns
        -------
        bool
            True if the process has completed
        """
        if self.__process is not None:
            if self.__process.poll() is not None:
                return True
        return False

    def errored(self) -> bool:
        """
        Return True if the process errored.

        Returns
        -------
        bool
            True if the process returned a non-zero code
        """
        if self.__process is not None:
            return_code = self.__process.poll()
            if return_code not in (0, None):
                logging.error("pid %s errored with exit code %s", self.pid, return_code)
                return True
        return False

    def raise_error(self) -> None:
        """Raise and error from the subprocess in a clean way."""
        if self.completed():
            if isinstance(self.__process, subprocess.Popen) and isinstance(
                self.return_code, int
            ):
                result = subprocess.CompletedProcess(
                    self.__process.args, self.return_code, self.std_out, self.std_err
                )

                result.check_returncode()
