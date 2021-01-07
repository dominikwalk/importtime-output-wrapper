from _pytest.capture import capsys
import pytest

import importtime_output_wrapper


def test_cli_empty_module():
    with pytest.raises(SystemExit) as e:
        importtime_output_wrapper.main([])
        assert e.value == 2
