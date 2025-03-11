"""
Test Factory to make fake objects for testing
"""

import factory
from service.models import Shopcart


class ShopcartFactory(factory.Factory):
    """Creates fake pets that you don't have to feed"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Shopcart

    id = factory.Sequence(lambda n: n)
    customer_id = factory.Sequence(lambda n: n)

    time_atc = factory.Faker("date_time_between", start_date="-2y", end_date="now")

    # Todo: Add your other attributes here...
