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
Shopcart Service

This service implements a REST API that allows you to Create, Read, Update
and Delete Shopcart
"""

from flask import jsonify, request, url_for, abort
from flask import current_app as app  # Import Flask application
from service.models import Shopcart, Item
from service.common import status  # HTTP Status Codes


######################################################################
# GET HEALTH CHECK
######################################################################
@app.route("/health")
def health_check():
    """Let them know our heart is still beating"""
    return jsonify(status=200, message="Healthy"), status.HTTP_200_OK


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    app.logger.info("Request for Root URL")
    return (
        jsonify(
            name="Shopcarts REST API Service",
            version="1.0",
            paths=url_for("list_shopcarts", _external=True),
        ),
        status.HTTP_200_OK,
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


# ######################################################################
# UPDATE AN EXISTING Shopcart
######################################################################
@app.route("/shopcarts/<int:shopcart_id>/items/<int:item_id>", methods=["PUT"])
def update_item(shopcart_id, item_id):
    app.logger.info("Request to update item %s for shopcart %s", item_id, shopcart_id)
    check_content_type("application/json")

    # Verify the shopcart exists
    shopcart = Shopcart.find(shopcart_id)
    if not shopcart:
        abort(status.HTTP_404_NOT_FOUND, f"Shopcart with id '{shopcart_id}' not found.")

    # Locate the specific item within the shopcart's items
    item = next((i for i in shopcart.items if i.id == item_id), None)
    if not item:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Item with id '{item_id}' not found in Shopcart {shopcart_id}.",
        )

    item.deserialize(request.get_json())
    item.id = item_id
    item.update()  # Ensure your Item model has an update() that commits changes

    return jsonify(item.serialize()), status.HTTP_200_OK


# CREATE A NEW SHOPCART
######################################################################
@app.route("/shopcarts", methods=["POST"])
def create_shopcart():
    """
    Creates a Shopcart
    This endpoint will create an Shopcart based the data in the body that is posted
    """
    app.logger.info("Request to create a Shopcart")
    check_content_type("application/json")

    # Create the shopcart
    shopcart = Shopcart()
    shopcart.deserialize(request.get_json())
    shopcart.create()

    # Create a message to return
    message = shopcart.serialize()
    location_url = url_for("get_shopcarts", shopcart_id=shopcart.id, _external=True)

    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def check_content_type(content_type):
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, f"Content-Type must be {content_type}"
    )


# CREATE A NEW ITEM IN SHOPCART
######################################################################
@app.route("/shopcarts/<int:shopcart_id>/items", methods=["POST"])
def create_items(shopcart_id):
    """
    Create an items on an shopcart

    This endpoint will add an items to an shopcart
    """
    app.logger.info("Request to create an items for shopcart with id: %s", shopcart_id)
    check_content_type("application/json")

    # See if the shopcart exists and abort if it doesn't
    shopcart = Shopcart.find(shopcart_id)
    if not shopcart:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"shopcart with id '{shopcart_id}' could not be found.",
        )

    # Create an items from the json data
    item = Item()
    item.deserialize(request.get_json())

    # Append the items to the shopcart
    shopcart.items.append(item)
    item.create()

    # Prepare a message to return
    message = item.serialize()

    # Send the location to GET the new item
    location_url = url_for(
        "get_items", shopcart_id=shopcart_id, item_id=item.id, _external=True
    )
    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
# DELETE AN ITEM
######################################################################
@app.route("/shopcarts/<int:shopcart_id>/items/<int:item_id>", methods=["DELETE"])
def delete_items(shopcart_id, item_id):
    """
    Delete an item

    This endpoint will delete an item based the id specified in the path
    """
    app.logger.info(
        "Request to delete item %s for shopcart id: %s", (item_id, shopcart_id)
    )

    # See if the item exists and delete it if it does
    item = Item.find(item_id)
    if item:
        item.delete()

    return "", status.HTTP_204_NO_CONTENT


######################################################################
# READ A SHOPCART
######################################################################
@app.route("/shopcarts/<int:shopcart_id>", methods=["GET"])
def get_shopcarts(shopcart_id):
    """
    Retrieve a single Shopcart

    This endpoint will return a Shopcart based on it's id
    """
    app.logger.info("Request to Retrieve a Shopcart with id [%s]", shopcart_id)

    # Attempt to find the Shopcart and abort if not found
    shopcart = Shopcart.find(shopcart_id)
    if not shopcart:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Shopcart with id '{shopcart_id}' was not found.",
        )

    return jsonify(shopcart.serialize()), status.HTTP_200_OK


######################################################################
# UPDATE AN EXISTING SHOPCART
######################################################################
@app.route("/shopcarts/<int:shopcart_id>", methods=["PUT"])
def update_shopcarts(shopcart_id):
    """
    Update a Shopcart

    This endpoint will update a Shopcart based the body that is posted
    """
    app.logger.info("Request to Update a shopcart with id [%s]", shopcart_id)
    check_content_type("application/json")

    # Attempt to find the Shopcart and abort if not found
    shopcart = Shopcart.find(shopcart_id)
    if not shopcart:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Shopcart with id '{shopcart_id}' was not found.",
        )

    # Update from the json in the body of the request
    shopcart.deserialize(request.get_json())
    shopcart.id = shopcart_id
    shopcart.update()

    return jsonify(shopcart.serialize()), status.HTTP_200_OK


######################################################################
# LIST ALL SHOPCARTS
######################################################################
@app.route("/shopcarts", methods=["GET"])
def list_shopcarts():
    """Returns all of the shopcarts"""
    app.logger.info("Request for shopcart list")

    shopcarts = []

    # Process the query string if any
    customer_id = request.args.get("customer_id")
    if customer_id:
        customer_id = int(customer_id)
        shopcarts = Shopcart.find_by_customer(customer_id)
    else:
        shopcarts = Shopcart.all()

    # Return as an array of dictionaries
    results = [shopcart.serialize() for shopcart in shopcarts]

    return jsonify(results), status.HTTP_200_OK


######################################################################
# READ AN ITEM FROM SHOPCART
######################################################################
@app.route("/shopcarts/<int:shopcart_id>/items/<int:item_id>", methods=["GET"])
def get_items(shopcart_id, item_id):
    """
    Get an Item

    This endpoint returns just an item
    """
    app.logger.info(
        "Request to retrieve Item %s for Shopcart id: %s", (item_id, shopcart_id)
    )

    # See if the item exists and abort if it doesn't
    item = Item.find(item_id)
    if not item:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"item with id '{item_id}' could not be found.",
        )

    return jsonify(item.serialize()), status.HTTP_200_OK


######################################################################
# DELETE A SHOPCART
######################################################################
@app.route("/shopcarts/<int:shopcart_id>", methods=["DELETE"])
def delete_shopcarts(shopcart_id):
    """
    Delete a Shopcart

    This endpoint will delete an Shopcart based the id specified in the path
    """
    app.logger.info("Request to delete shopcart with id: %s", shopcart_id)

    # Retrieve the account to delete and delete it if it exists
    shopcart = Shopcart.find(shopcart_id)
    if shopcart:
        shopcart.delete()

    return "", status.HTTP_204_NO_CONTENT


######################################################################
# LIST ADDRESSES
######################################################################
@app.route("/shopcarts/<int:shopcart_id>/items", methods=["GET"])
def list_items(shopcart_id):
    """Returns all of the items for a Shopping Cart"""
    app.logger.info("Request for all items for shopcart with id: %s", shopcart_id)

    # See if the shopcart exists and abort if it doesn't
    shopcart = Shopcart.find(shopcart_id)
    if not shopcart:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Shopcart with id '{shopcart_id}' could not be found.",
        )

    # Get the addresses for the account
    results = [item.serialize() for item in shopcart.items]

    return jsonify(results), status.HTTP_200_OK
