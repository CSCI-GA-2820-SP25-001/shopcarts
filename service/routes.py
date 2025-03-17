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
from service.models import Shopcart
from service.common import status  # HTTP Status Codes


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return (
        "Reminder: return some useful information in json format about the service here",
        status.HTTP_200_OK,
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


# ######################################################################
# UPDATE AN EXISTING Shopcart
######################################################################
@app.route("/shopcarts/<int:item_id>", methods=["PUT"])
def update_items(item_id):
    """
    Update an Shopcart

    This endpoint will update an Shopcart based the body that is posted
    """
    app.logger.info("Request to update Shopcart with id: %s", item_id)
    check_content_type("application/json")

    # See if the Shopcart exists and abort if it doesn't
    Shopcart = Shopcart.find(item_id)
    if not Shopcart:
        abort(status.HTTP_404_NOT_FOUND, f"Shopcart with id '{item_id}' was not found.")

    # Update from the json in the body of the request
    Shopcart.deserialize(request.get_json())
    Shopcart.id = item_id
    Shopcart.update()

    return jsonify(Shopcart.serialize()), status.HTTP_200_OK


######################################################################
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
    shopcart = shopcart.find(shopcart_id)
    if not shopcart:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"shopcart with id '{shopcart_id}' could not be found.",
        )

    # Create an items from the json data
    items = items()
    items.deserialize(request.get_json())

    # Append the items to the shopcart
    shopcart.items.append(items)
    shopcart.update()

    # Prepare a message to return
    message = items.serialize()

    # Send the location to GET the new item
    location_url = url_for(
        "get_items", shopcart_id=shopcart.id, items_id=items.id, _external=True
    )
    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
# DELETE AN ITEM
######################################################################
@app.route("/shopcarts/<int:shopcart_id>/items/<int:items_id>", methods=["DELETE"])
def delete_items(shopcart_id, item_id):
    """
    Delete an item

    This endpoint will delete an item based the id specified in the path
    """
    app.logger.info(
        "Request to delete item %s for shopcart id: %s", (item_id, shopcart_id)
    )

    # See if the item exists and delete it if it does
    item = item.find(item_id)
    if item:
        item.delete()

    return "", status.HTTP_204_NO_CONTENT
