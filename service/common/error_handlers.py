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
Error handlers for RESTful API
"""
from flask import jsonify
from service.common import status
from service.models import DataValidationError


def not_found(error):
    """Creates a not found error response"""
    return (
        jsonify(
            status=status.HTTP_404_NOT_FOUND,
            error="Not Found",
            message=error.description,
        ),
        status.HTTP_404_NOT_FOUND,
    )


def method_not_supported(error):
    """Creates a method not supported error response"""
    return (
        jsonify(
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
            error="Method not Allowed",
            message=error.description,
        ),
        status.HTTP_405_METHOD_NOT_ALLOWED,
    )


def mediator_unsupported(error):
    """Creates a mediator not supported error response"""
    return (
        jsonify(
            status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            error="Unsupported media type",
            message=error.description,
        ),
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
    )


def bad_request(error):
    """Creates a bad request error response"""
    return (
        jsonify(
            status=status.HTTP_400_BAD_REQUEST,
            error="Bad Request",
            message=error.description,
        ),
        status.HTTP_400_BAD_REQUEST,
    )


def data_validation_error(error):
    """Creates a data validation error response"""
    return (
        jsonify(
            status=status.HTTP_400_BAD_REQUEST,
            error="Bad Request",
            message=error.message,
        ),
        status.HTTP_400_BAD_REQUEST,
    )


def initialize_error_handlers(app):
    """Initialize all error handlers"""
    app.errorhandler(DataValidationError)(data_validation_error)
    app.errorhandler(status.HTTP_400_BAD_REQUEST)(bad_request)
    app.errorhandler(status.HTTP_404_NOT_FOUND)(not_found)
    app.errorhandler(status.HTTP_405_METHOD_NOT_ALLOWED)(method_not_supported)
    app.errorhandler(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)(mediator_unsupported)
