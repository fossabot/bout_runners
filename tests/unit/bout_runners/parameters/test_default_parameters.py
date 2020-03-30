"""Contains unittests for default parameters."""


from bout_runners.parameters.default_parameters import DefaultParameters


def test_default_parameters(get_test_data_path,
                            get_bout_path_conduction):
    """
    Test the DefaultParameter.

    Test by:
    1. Checking that setting only the `settings_path` parameter
       yields a dict
    2. Checking that setting only the `bout_paths` parameter
       yields a dict

    Parameters
    ----------
    get_test_data_path : Path
        Path to the test data
    get_bout_path_conduction : function
        Function returning the bout_paths object
    """
    settings_path = get_test_data_path.joinpath('BOUT.settings')
    default_parameters_settings = \
        DefaultParameters(settings_path=settings_path)
    settings_dict = default_parameters_settings.get_default_parameters()

    assert isinstance(settings_dict, dict)

    bout_paths = get_bout_path_conduction('test_default_parameters')
    default_parameters_bout_paths = \
        DefaultParameters(bout_paths=bout_paths)
    bout_paths_dict = \
        default_parameters_bout_paths.get_default_parameters()

    assert isinstance(bout_paths_dict, dict)
