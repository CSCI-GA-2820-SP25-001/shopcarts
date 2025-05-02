"""
Test Factory to make fake objects for testing
"""

import factory
from factory import post_generation
from factory.fuzzy import FuzzyChoice, FuzzyInteger, FuzzyDecimal
from service.models import Shopcart, Item


class ShopcartFactory(factory.Factory):
    """Creates fake shopcarts that you don't have to feed"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Shopcart

    id = factory.Sequence(lambda n: n)
    customer_id = factory.Sequence(lambda n: n)
    time_atc = factory.Faker("date_time")

    @post_generation
    def items(
        self, create, extracted, **kwargs
    ):  # pylint: disable=method-hidden, unused-argument
        """Creates the items list"""
        if not create:
            return

        if extracted:
            self.items = extracted


class ItemFactory(factory.Factory):
    """Creates fake items for shopcarts with realistic test data

    This factory generates items with common grocery products
    and realistic prices and quantities for testing
    """

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Item

    id = factory.Sequence(lambda n: n)
    shopcart_id = None
    name = FuzzyChoice(
        choices=[
            "Milk",
            "Bread",
            "Eggs",
            "Cheese",
            "Apples",
            "Bananas",
            "Carrots",
            "Tomatoes",
            "Chicken",
            "Beef",
        ]
    )
    description = factory.Faker("sentence", nb_words=3)
    quantity = FuzzyInteger(1, 20)
    price = FuzzyDecimal(0.50, 20.00, precision=2)
    shopcart = factory.SubFactory(ShopcartFactory)
