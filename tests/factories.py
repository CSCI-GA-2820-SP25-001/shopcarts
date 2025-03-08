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
    name = factory.Faker("name")
    quantity = factory.Faker("quantity")
    price = factory.Faker("price")
    time_atc = factory.Faker("time_atc")

    # Todo: Add your other attributes here...
