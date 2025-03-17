"""
Test Factory to make fake objects for testing
"""

import factory
from service.models import Shopcart, Item
from factory import Factory, SubFactory, Sequence, Faker, post_generation
from factory.fuzzy import FuzzyChoice, FuzzyInteger, FuzzyDecimal


class ShopcartFactory(factory.Factory):
    """Creates fake shopcarts that you don't have to feed"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Shopcart

    id = factory.Sequence(lambda n: n)
    customer_id = factory.Sequence(lambda n: n)

    time_atc = factory.Faker("date_time_between", start_date="-2y", end_date="now")

    @post_generation
    def items(
        self, create, extracted, **kwargs
    ):  # pylint: disable=method-hidden, unused-argument
        """Creates the items list"""
        if not create:
            return

        if extracted:
            self.items = extracted

    # Todo: Add your other attributes here...


class ItemFactory(factory.Factory):
    """Creates fake grocery items with realistic test data"""

    class Meta:
        model = Item  # Assuming the Item model is defined elsewhere

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
    description = factory.Faker("sentence", nb_words=10)
    quantity = FuzzyInteger(1, 20)
    price = FuzzyDecimal(0.50, 20.00, precision=2)
    shopcart = factory.SubFactory(ShopcartFactory)
