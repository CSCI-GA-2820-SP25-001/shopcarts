"""
Models for Shopcart

All of the models are stored in this module
"""

import logging

from .persistent_base import db, PersistentBase, DataValidationError
from .item import Item

logger = logging.getLogger("flask.app")


class Shopcart(db.Model, PersistentBase):
    """
    Class that represents a Shopcart
    """

    ### Translator
    # Shopcart = Account
    # Item = Address

    ##################################################
    # Table Schema
    ##################################################
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, nullable=False)
    time_atc = db.Column(
        db.DateTime, nullable=True, default=db.func.current_timestamp()
    )
    items = db.relationship("Item", backref="shopcart", passive_deletes=True)

    def __repr__(self):
        return f"<Shopcart {self.customer_id} id=[{self.id}]>"

    def serialize(self):
        """Serializes a Shopcart into a dictionary"""
        shopcart = {
            "id": self.id,
            "customer_id": self.customer_id,
            "time_atc": self.time_atc,
            "items": [],
        }
        for item in self.items:
            shopcart["items"].append(item.serialize())

        return shopcart

    def deserialize(self, data):
        """
        Deserializes a Shopcart from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.id = data["id"]
            self.customer_id = data["customer_id"]
            self.time_atc = data["time_atc"]
            # handle inner list of items
            item_list = data.get("items")
            for json_item in item_list:
                item = Item()
                item.deserialize(json_item)
                self.items.append(item)

        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid Shopcart: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Shopcart: body of request contained bad or no data "
                + str(error)
            ) from error
        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def find_by_customer(cls, customer_id):
        """Returns all Shopcarts with the given customer

        Args:
            customer_id (int): the customer ID of the Shopcarts you want to match
        """
        logger.info("Processing name query for %s ...", customer_id)
        return cls.query.filter(cls.customer_id == customer_id)
