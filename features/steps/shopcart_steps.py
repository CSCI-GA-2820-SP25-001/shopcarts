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
Shopcart and Item Steps

Steps file for Shopcart.feature

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
import requests
from compare3 import expect
from behave import given  # pylint: disable=no-name-in-module

# HTTP Return Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204

WAIT_TIMEOUT = 60


@given("the following shopcarts")
def shopcart_step_impl(context):
    """Delete all Shopcarts and load new ones"""

    # Get a list of all the shopcarts
    rest_endpoint = f"{context.base_url}/shopcarts"
    context.resp = requests.get(rest_endpoint, timeout=WAIT_TIMEOUT)
    expect(context.resp.status_code).equal_to(HTTP_200_OK)

    # Delete them one by one
    for shopcart in context.resp.json():
        context.resp = requests.delete(
            f"{rest_endpoint}/{shopcart['id']}", timeout=WAIT_TIMEOUT
        )
        expect(context.resp.status_code).equal_to(HTTP_204_NO_CONTENT)

    # Load the database with new shopcarts
    for row in context.table:
        payload = {"customer_id": int(row["customer_id"]), "id": int(row["id"])}
        context.resp = requests.post(rest_endpoint, json=payload, timeout=WAIT_TIMEOUT)
        expect(context.resp.status_code).equal_to(HTTP_201_CREATED)


@given("the following items in shopcarts")
def item_step_impl(context):
    """Add items to existing shopcarts"""

    # Get the list of all shopcarts to map shopcart IDs
    shopcarts_endpoint = f"{context.base_url}/shopcarts"
    context.resp = requests.get(shopcarts_endpoint, timeout=WAIT_TIMEOUT)
    expect(context.resp.status_code).equal_to(HTTP_200_OK)

    # Iterate through the items and add them to the respective shopcart
    for shopcart in context.resp.json():
        shopcart_id = shopcart["id"]
        for row in context.table:
            # Construct the REST endpoint for the specific shopcart
            print(row)
            rest_endpoint = f"{context.base_url}/shopcarts/{shopcart_id}/items"
            payload = {
                "id": int(row[0]),  # Include the item ID
                "name": row[1],  # Include the item name
                "quantity": int(row[2]),  # Include the quantity
                "price": float(row[3]),  # Include the price
                "description": row[4],  # Include the description
            }
            # Send POST request to add the item to the shopcart
            context.resp = requests.post(
                rest_endpoint, json=payload, timeout=WAIT_TIMEOUT
            )
            expect(context.resp.status_code).equal_to(HTTP_201_CREATED)