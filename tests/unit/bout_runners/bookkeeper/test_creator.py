"""Contains unittests for the creator."""

import pytest
from bout_runners.bookkeeper.creator import create_system_info_table
from bout_runners.bookkeeper.creator import create_run_table
from bout_runners.bookkeeper.creator import \
    create_file_modification_table
from bout_runners.bookkeeper.creator import create_parameter_tables
from bout_runners.bookkeeper.creator import create_split_table


@pytest.fixture(scope='module')
def make_creator_database(make_test_database):
    """
    Create a database.

    Parameters
    ----------
    make_test_database : function
        The function for creating the database

    Returns
    -------
    bk : Bookkeeper
        The bookkeeper object
    """
    bk = make_test_database('creator.db')
    return bk


def test_create_run_table(make_creator_database):
    """
    Test that the run table is created.

    Parameters
    ----------
    make_creator_database : Bookkeeper
        The bookkeeper object
    """
    bk = make_creator_database
    create_run_table(bk)
    query_str = ('SELECT name FROM sqlite_master '
                 '   WHERE type="table"')
    table = bk.query(query_str)
    assert 'run' in table.loc[:, 'name'].values


def test_create_parameter_tables(make_creator_database, make_project):
    """
    Test that the parameter tables are created.

    Parameters
    ----------
    make_creator_database : Bookkeeper
        The bookkeeper object
    make_project : Path
        The path to the conduction example
    """
    bk = make_creator_database
    project_path = make_project
    create_parameter_tables(bk, project_path)
    query_str = ('SELECT name FROM sqlite_master '
                 '   WHERE type="table"')
    table = bk.query(query_str)
    expected = {'global',
                'conduction',
                'mesh',
                'mesh_ddz',
                'output',
                'restart',
                'solver',
                't',
                'all_boundaries',
                'parameters'}
    assert expected.issubset(set(table.loc[:, 'name'].values))


def test_create_file_modification_table(make_creator_database):
    """
    Test that the modification table is created.

    Parameters
    ----------
    make_creator_database : Bookkeeper
        The bookkeeper object
    """
    bk = make_creator_database
    create_file_modification_table(bk)
    query_str = ('SELECT name FROM sqlite_master '
                 '   WHERE type="table"')
    table = bk.query(query_str)
    assert 'file_modification' in table.loc[:, 'name'].values


def test_create_split_table(make_creator_database):
    """
    Test that the split table is created.

    Parameters
    ----------
    make_creator_database : Bookkeeper
        The bookkeeper object
    """
    bk = make_creator_database
    create_split_table(bk)
    query_str = ('SELECT name FROM sqlite_master '
                 '   WHERE type="table"')
    table = bk.query(query_str)
    assert 'split' in table.loc[:, 'name'].values


def test_create_system_info_table(make_creator_database):
    """
    Test that the system info table is created.

    Parameters
    ----------
    make_creator_database : Bookkeeper
        The bookkeeper object
    """
    bk = make_creator_database
    create_system_info_table(bk)
    query_str = ('SELECT name FROM sqlite_master '
                 '   WHERE type="table"')
    table = bk.query(query_str)
    assert 'system_info' in table.loc[:, 'name'].values
