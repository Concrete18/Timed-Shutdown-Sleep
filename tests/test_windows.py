# standard library
import re

# local imports
from library.windows import *


class TestGetActivePowerScheme:

    def test_success(self):
        scheme_guid = get_active_power_scheme()

        guid_regex = re.compile(
            r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
        )
        match = guid_regex.match(scheme_guid)
        assert bool(match)


class TestUsingBattery:

    def test_success(self):
        assert isinstance(using_battery(), bool)


class TestGetCurrentStandbyTime:

    def test_success(self):
        stanby_time = get_current_standby_time()
        assert isinstance(stanby_time, int)
