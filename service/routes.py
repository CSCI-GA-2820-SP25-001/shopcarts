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
