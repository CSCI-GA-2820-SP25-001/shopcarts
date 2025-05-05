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
Test Shopcart API Service Test Suite
"""

# pylint: disable=duplicate-code
import os
import logging
from decimal import Decimal
from unittest import TestCase
from unittest.mock import patch
from wsgi import app
from tests.factories import ShopcartFactory, ItemFactory
from service.models import db, Shopcart
from service.common import status
from service import create_app

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:pgs3cr3t@postgres:5432/postgres"
)

BASE_URL = "/shopcarts"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestShopcartService(TestCase):
    """REST API Server Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Shopcart).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  H E L P E R   M E T H O DS
    ######################################################################

    def _create_shopcarts(self, count):
        """Factory method to create shopcarts in bulk"""
        shopcarts = []
        for _ in range(count):
            shopcart = ShopcartFactory()
            resp = self.client.post(BASE_URL, json=shopcart.serialize())
            self.assertEqual(
                resp.status_code,
                status.HTTP_201_CREATED,
                "Could not create test Shopcart",
            )
            new_shopcart = resp.get_json()
            shopcart.id = new_shopcart["id"]
            shopcarts.append(shopcart)
        return shopcarts

    ######################################################################
    #  SHOPCART  T E S T   C A S E S
    ######################################################################

    def test_index(self):
        """It should call the Home Page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("text/html", resp.content_type)

    def test_health_check(self):
        """It should confirm the service is healthy"""
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["message"], "Healthy")

    def test_get_shopcart_list(self):
        """It should Get a list of shopcarts"""
        self._create_shopcarts(5)
        resp = self.client.get(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 5)

    def test_get_shopcart_by_customer_id(self):
        """It should Get an shopcart by customer_id"""
        shopcarts = self._create_shopcarts(3)
        resp = self.client.get(
            BASE_URL, query_string=f"customer_id={shopcarts[1].customer_id}"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data[0]["customer_id"], shopcarts[1].customer_id)

    def test_get_shopcart(self):
        """It should Read a single shopcart"""
        # get the id of an shopcart
        shopcart = self._create_shopcarts(1)[0]
        resp = self.client.get(
            f"{BASE_URL}/{shopcart.id}", content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["customer_id"], shopcart.customer_id)

    def test_get_shopcart_not_found(self):
        """It should not Read an shopcart that is not found"""
        resp = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_shopcart(self):
        """It should Create a new shopcart"""
        shopcart = ShopcartFactory()
        resp = self.client.post(
            BASE_URL, json=shopcart.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = resp.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_shopcart = resp.get_json()
        self.assertEqual(
            new_shopcart["customer_id"],
            shopcart.customer_id,
            "Customer IDs do not match",
        )
        self.assertEqual(
            new_shopcart["time_atc"],
            shopcart.time_atc.strftime("%a, %d %b %Y %H:%M:%S GMT"),
            "Times do not match",
        )

        # Check that the location header was correct by getting it
        resp = self.client.get(location, content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_shopcart = resp.get_json()
        self.assertEqual(
            new_shopcart["customer_id"],
            shopcart.customer_id,
            "Customer IDs do not match",
        )
        self.assertEqual(
            new_shopcart["time_atc"],
            shopcart.time_atc.strftime("%a, %d %b %Y %H:%M:%S GMT"),
            "Times do not match",
        )

    def test_update_shopcart(self):
        """It should Update an existing shopcart"""
        # create an shopcart to update
        test_shopcart = ShopcartFactory()
        resp = self.client.post(BASE_URL, json=test_shopcart.serialize())
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # update the shopcart
        new_shopcart = resp.get_json()
        new_shopcart["customer_id"] = 1234567
        new_shopcart_id = new_shopcart["id"]
        resp = self.client.put(f"{BASE_URL}/{new_shopcart_id}", json=new_shopcart)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_shopcart = resp.get_json()
        self.assertEqual(updated_shopcart["customer_id"], 1234567)

    def test_delete_shopcart(self):
        """It should Delete an shopcart"""
        # get the id of an shopcart
        shopcart = self._create_shopcarts(1)[0]
        resp = self.client.delete(f"{BASE_URL}/{shopcart.id}")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_bad_request(self):
        """It should not Create when sending the wrong data"""
        resp = self.client.post(BASE_URL, json={"customer_id": "not enough data"})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unsupported_media_type(self):
        """It should not Create when sending wrong media type"""
        shopcart = ShopcartFactory()
        resp = self.client.post(
            BASE_URL, json=shopcart.serialize(), content_type="test/html"
        )
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_method_not_allowed(self):
        """It should not allow an illegal method call"""
        resp = self.client.put(BASE_URL, json={"not": "today"})
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_query_shopcarts_by_item_name(self):
        """It should return shopcarts that have an item with a given name"""
        shopcart = self._create_shopcarts(1)[0]
        item = ItemFactory(name="Bananas")
        self.client.post(f"{BASE_URL}/{shopcart.id}/items", json=item.serialize())

        resp = self.client.get(BASE_URL, query_string={"item_name": "Bananas"})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertTrue(
            any("Bananas" in [i["name"] for i in sc["items"]] for sc in data)
        )

    def test_query_shopcarts_by_customer_id(self):
        """It should return shopcarts filtered by customer_id"""
        shopcarts = self._create_shopcarts(3)
        target_id = shopcarts[1].customer_id

        resp = self.client.get(BASE_URL, query_string={"customer_id": target_id})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertTrue(all(sc["customer_id"] == target_id for sc in data))
        self.assertGreaterEqual(len(data), 1)

    def test_create_shopcart_no_content_type(self):
        """It should fail to create a shopcart with no content type"""
        resp = self.client.post(BASE_URL, data="{}")  # no json= and no headers
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_shopcart_invalid_content_type(self):
        """It should fail to create a shopcart with invalid content type"""
        resp = self.client.post(BASE_URL, data="{}", content_type="text/plain")
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_data_validation_error(self):
        """It should handle DataValidationError"""
        shopcart = self._create_shopcarts(1)[0]
        # Try to update with invalid data type but valid time_atc
        resp = self.client.put(
            f"{BASE_URL}/{shopcart.id}",
            json={
                "customer_id": "not-an-integer",
                "time_atc": shopcart.time_atc.strftime("%a, %d %b %Y %H:%M:%S GMT"),
            },
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        data = resp.get_json()
        self.assertIn("customer_id must be an integer", data["message"])

    def test_mediatype_not_supported(self):
        """It should return 415 when media type is not supported"""
        shopcart = self._create_shopcarts(1)[0]
        resp = self.client.post(
            f"{BASE_URL}/{shopcart.id}/items",
            data="not-json",
            content_type="text/plain",
        )
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_method_not_allowed_on_item(self):
        """It should not allow an illegal method call on item endpoint"""
        shopcart = self._create_shopcarts(1)[0]
        resp = self.client.patch(f"{BASE_URL}/{shopcart.id}/items/1")
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_database_initialization_error(self):
        """It should handle database initialization errors"""
        with patch("service.models.db.create_all") as mock_db:
            mock_db.side_effect = Exception("Could not connect to database")
            with self.assertRaises(SystemExit) as context_manager:
                create_app()
            self.assertEqual(context_manager.exception.code, 4)

    def test_error_handlers(self):
        """Test various error handlers"""
        # Test 404 not found
        resp = self.client.get(f"{BASE_URL}/999999")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        data = resp.get_json()
        self.assertEqual(data["error"], "Not Found")

        # Test 405 method not allowed
        resp = self.client.patch(f"{BASE_URL}/1")
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        data = resp.get_json()
        self.assertEqual(data["error"], "Method not Allowed")

        # Test 415 unsupported media type
        resp = self.client.post(
            BASE_URL, headers={"content-type": "text/xml"}, data="<xml>data</xml>"
        )
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        data = resp.get_json()
        self.assertEqual(data["error"], "Unsupported media type")

        # Test 400 bad request
        resp = self.client.post(
            BASE_URL, headers={"content-type": "application/json"}, data="invalid-json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        data = resp.get_json()
        self.assertEqual(data["error"], "Bad Request")

    ######################################################################
    #  ITEM  T E S T   C A S E S
    ######################################################################

    def test_get_item_list(self):
        """It should Get a list of items"""
        # add two items to shopcart
        shopcart = self._create_shopcarts(1)[0]
        item_list = ItemFactory.create_batch(2)

        # Create item 1
        resp = self.client.post(
            f"{BASE_URL}/{shopcart.id}/items", json=item_list[0].serialize()
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Create item 2
        resp = self.client.post(
            f"{BASE_URL}/{shopcart.id}/items", json=item_list[1].serialize()
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # get the list back and make sure there are 2
        resp = self.client.get(f"{BASE_URL}/{shopcart.id}/items")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertEqual(len(data), 2)

    def test_add_item(self):
        """It should Add an item to an shopcart"""
        shopcart = self._create_shopcarts(1)[0]
        item = ItemFactory()
        resp = self.client.post(
            f"{BASE_URL}/{shopcart.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = resp.headers.get("Location", None)
        self.assertIsNotNone(location)

        data = resp.get_json()
        logging.debug(data)

        self.assertEqual(data["shopcart_id"], shopcart.id)
        self.assertEqual(data["description"], item.description)
        self.assertEqual(data["quantity"], item.quantity)

        price_from_api = Decimal(f"{data['price']:.2f}")
        self.assertEqual(price_from_api, item.price)

        # Check that the location header was correct by getting it
        resp = self.client.get(location, content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_item = resp.get_json()
        self.assertEqual(
            new_item["quantity"], item.quantity, "item quantity does not match"
        )

    def test_get_item(self):
        """It should Get an item from an shopcart"""
        # create a known item
        shopcart = self._create_shopcarts(1)[0]
        item = ItemFactory()
        resp = self.client.post(
            f"{BASE_URL}/{shopcart.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        data = resp.get_json()
        logging.debug(data)
        item_id = data["id"]

        # retrieve it back
        resp = self.client.get(
            f"{BASE_URL}/{shopcart.id}/items/{item_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        logging.debug(data)
        self.assertEqual(data["shopcart_id"], shopcart.id)
        self.assertEqual(data["description"], item.description)
        self.assertEqual(data["quantity"], item.quantity)

        price_from_api = Decimal(f"{data['price']:.2f}")
        self.assertEqual(price_from_api, item.price)

    def test_get_item_not_found(self):
        """It should return 404 if item is not found"""
        shopcart = self._create_shopcarts(1)[0]
        resp = self.client.get(f"{BASE_URL}/{shopcart.id}/items/0")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_item(self):
        """It should Update an item on an shopcart"""
        # create a known item
        shopcart = self._create_shopcarts(1)[0]
        item = ItemFactory()
        resp = self.client.post(
            f"{BASE_URL}/{shopcart.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        data = resp.get_json()
        logging.debug(data)
        item_id = data["id"]
        data["quantity"] = 20

        # send the update back
        resp = self.client.put(
            f"{BASE_URL}/{shopcart.id}/items/{item_id}",
            json=data,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # retrieve it back
        resp = self.client.get(
            f"{BASE_URL}/{shopcart.id}/items/{item_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        logging.debug(data)
        self.assertEqual(data["id"], item_id)
        self.assertEqual(data["shopcart_id"], shopcart.id)
        self.assertEqual(data["quantity"], 20)

    def test_delete_item(self):
        """It should Delete an item"""
        shopcart = self._create_shopcarts(1)[0]
        item = ItemFactory()
        resp = self.client.post(
            f"{BASE_URL}/{shopcart.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.get_json()
        logging.debug(data)
        item_id = data["id"]

        # send delete request
        resp = self.client.delete(
            f"{BASE_URL}/{shopcart.id}/items/{item_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        # retrieve it back and make sure item is not there
        resp = self.client.get(
            f"{BASE_URL}/{shopcart.id}/items/{item_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_clear_all_items_in_shopcart(self):
        """It should delete all items from a shopcart"""
        shopcart = self._create_shopcarts(1)[0]

        # Add two items
        self.client.post(
            f"{BASE_URL}/{shopcart.id}/items", json=ItemFactory().serialize()
        )
        self.client.post(
            f"{BASE_URL}/{shopcart.id}/items", json=ItemFactory().serialize()
        )

        # Confirm 2 items present
        resp = self.client.get(f"{BASE_URL}/{shopcart.id}/items")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 2)

        # Clear all items
        resp = self.client.delete(f"{BASE_URL}/{shopcart.id}/items")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        # Confirm 0 items
        resp = self.client.get(f"{BASE_URL}/{shopcart.id}/items")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 0)

    def test_clear_items_shopcart_not_found(self):
        """It should fail to clear items from non-existent shopcart"""
        resp = self.client.delete(f"{BASE_URL}/0/items")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_query_items_by_name(self):
        """It should return items filtered by name"""
        shopcart = self._create_shopcarts(1)[0]
        item = ItemFactory(name="Milk")
        self.client.post(f"{BASE_URL}/{shopcart.id}/items", json=item.serialize())

        resp = self.client.get(
            f"{BASE_URL}/{shopcart.id}/items", query_string={"name": "Milk"}
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertTrue(all(i["name"] == "Milk" for i in data))

    def test_query_items_by_quantity(self):
        """It should return items filtered by quantity"""
        shopcart = self._create_shopcarts(1)[0]
        item = ItemFactory(quantity=7)
        self.client.post(
            f"{BASE_URL}/{shopcart.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )

        resp = self.client.get(
            f"{BASE_URL}/{shopcart.id}/items", query_string={"quantity": 7}
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertTrue(all(i["quantity"] == 7 for i in data))
        self.assertGreaterEqual(len(data), 1)
