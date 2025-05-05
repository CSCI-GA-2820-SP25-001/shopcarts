######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Test cases for Item
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from wsgi import app
from service.models import Shopcart, Item, db
from .factories import ShopcartFactory, ItemFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:pgs3cr3t@postgres:5432/postgres"
)

BASE_URL = "/shopcarts"


######################################################################
#  Shopcart   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestItem(TestCase):
    """Test Cases for Item Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Shopcart).delete()  # clean up the last tests
        db.session.query(Item).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    # ITEM T E S T   C A S E S
    ######################################################################

    def test_add_shopcart_item(self):
        """It should Create an shopcart with an item and add it to the database"""
        shopcarts = Shopcart.all()
        self.assertEqual(shopcarts, [])
        shopcart = ShopcartFactory()
        item = ItemFactory(shopcart=shopcart)
        shopcart.items.append(item)
        shopcart.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(shopcart.id)
        shopcarts = Shopcart.all()
        self.assertEqual(len(shopcarts), 1)

        new_shopcart = Shopcart.find(shopcart.id)
        self.assertEqual(new_shopcart.items[0].name, item.name)

        item2 = ItemFactory(shopcart=shopcart)
        shopcart.items.append(item2)
        shopcart.update()

        new_shopcart = Shopcart.find(shopcart.id)
        self.assertEqual(len(new_shopcart.items), 2)
        self.assertEqual(new_shopcart.items[1].name, item2.name)

    def test_update_shopcart_item(self):
        """It should Update an shopcarts item"""
        shopcarts = Shopcart.all()
        self.assertEqual(shopcarts, [])

        shopcart = ShopcartFactory()
        item = ItemFactory(shopcart=shopcart)
        shopcart.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(shopcart.id)
        shopcarts = Shopcart.all()
        self.assertEqual(len(shopcarts), 1)

        # Fetch it back
        shopcart = Shopcart.find(shopcart.id)
        old_item = shopcart.items[0]
        print("%r", old_item)
        self.assertEqual(old_item.quantity, item.quantity)
        # Change the city
        old_item.quantity = 10
        shopcart.update()

        # Fetch it back again
        shopcart = Shopcart.find(shopcart.id)
        item = shopcart.items[0]
        self.assertEqual(item.quantity, 10)

    def test_delete_shopcart_item(self):
        """It should Delete an shopcarts item"""
        shopcarts = Shopcart.all()
        self.assertEqual(shopcarts, [])

        shopcart = ShopcartFactory()
        item = ItemFactory(shopcart=shopcart)
        shopcart.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(shopcart.id)
        shopcarts = Shopcart.all()
        self.assertEqual(len(shopcarts), 1)

        # Fetch it back
        shopcart = Shopcart.find(shopcart.id)
        item = shopcart.items[0]
        item.delete()
        shopcart.update()

        # Fetch it back again
        shopcart = Shopcart.find(shopcart.id)
        self.assertEqual(len(shopcart.items), 0)

    def test_serialize_an_item(self):
        """It should serialize an Item"""
        item = ItemFactory()
        serial_item = item.serialize()
        self.assertEqual(serial_item["id"], item.id)
        self.assertEqual(serial_item["name"], item.name)
        self.assertEqual(serial_item["shopcart_id"], item.shopcart_id)
        self.assertEqual(serial_item["description"], item.description)
        self.assertEqual(serial_item["quantity"], item.quantity)
        self.assertEqual(serial_item["price"], item.price)

    def test_deserialize_an_item(self):
        """It should deserialize an Item"""
        item = ItemFactory()
        item.create()
        new_item = Item()
        new_item.deserialize(item.serialize())
        self.assertEqual(new_item.id, item.id)
        self.assertEqual(new_item.name, item.name)
        self.assertEqual(new_item.shopcart_id, item.shopcart_id)
        self.assertEqual(new_item.description, item.description)
        self.assertEqual(new_item.quantity, item.quantity)
        self.assertEqual(new_item.price, item.price)

    def test_delete_item_directly(self):
        """It should delete an item using the model's delete()"""
        item = ItemFactory()
        item.create()
        item_id = item.id
        item.delete()
        self.assertIsNone(Item.find(item_id))

    def test_item_deserialize_return_type(self):
        """It should return self when deserializing"""
        item = Item()
        result = item.deserialize(ItemFactory().serialize())
        self.assertIs(result, item)

    def test_delete_item_triggers_commit(self):
        """It should commit when deleting an item"""
        item = ItemFactory()
        item.create()
        item_id = item.id
        item.delete()
        self.assertIsNone(Item.find(item_id))
