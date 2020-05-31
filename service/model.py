# Copyright 2019. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Models for Product Service
All of the models are stored in this module
Models
------
Product - A Product used in the Product Store
Attributes:
-----------
name (string) - the name of the product
stock (integer) - the amound of the product in stock
price (numeric)) - the price of the product
description (string) - the description of the product
category (string) - the category the product belongs to (i.e. apparel, Electric appliance)
"""

import logging
from flask_sqlalchemy import SQLAlchemy
import flask

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()

class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """
    pass

class Product(db.Model):
    """
    Class that represents a Product
    """

    logger = logging.getLogger('app')
    app = None

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    stock = db.Column(db.Integer)
    price = db.Column(db.Numeric(18,2))
    description = db.Column(db.String(255))
    category = db.Column(db.String(50))

    def save(self):
        """
        Saves a Product to the data store
        """
        Product.logger.info('Saving %s', self.name)
        if not self.id:
            db.session.add(self)
        db.session.commit()

    def delete(self):
        Product.logger.info("Deleting %s", self.name)
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def delete_all(cls):
        Product.logger.info("Deleting all products")
        db.session.query(cls).delete()
        db.session.commit()

    def serialize(self):
        """ Serializes a Product into a dictionary """
        return {"id": self.id,
                "name": self.name,
                "stock": self.stock,
                "price": float(self.price),
                "description": self.description,
                "category": self.category}

    def deserialize(self, data):
        """
        Deserializes a Product from a dictionary
        Args:
            data (dict): A dictionary containing the Product data
        """
        try:
            if data['name'] == '' or data['category'] == '' :
                raise DataValidationError('Field cannot be empty string')
            self.name = data['name']
            self.stock = data['stock']
            self.price = data['price']
            self.description = data['description']
            self.category = data['category']
        except KeyError as error:
            raise DataValidationError(
                'Invalid product: missing ' + error.args[0])
        except TypeError as error:
            raise DataValidationError('Invalid pet: body of request contained'
                                      'bad or no data')
        return self

    @classmethod
    def init_db(cls, app):
        """ Initializes the database session """
        cls.logger.info('Initializing database')
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        if flask.has_request_context() == False:
            app.app_context().push()
        with app.app_context():
            db.create_all()  # make our sqlalchemy tables

    @classmethod
    def find(cls, product_id):
        """ Finds a Product by it's ID """
        cls.logger.info('Processing lookup for id %s ...', product_id)
        return cls.query.get(product_id)

    @classmethod
    def find_by_category(cls, category):
        cls.logger.info('Processing category query for %s ...', category)
        return cls.query.filter(cls.category == category)

    @classmethod
    def find_by_name(cls, name):
        cls.logger.info('Processing name query for %s ...', name)
        return cls.query.filter(cls.name == name)

    @classmethod
    def find_by_price(cls, low, high):
        cls.logger.info('Processing price query as range (%d %d] ...', low, high)
        return cls.query.filter(db.and_(cls.price > low, cls.price <= high))

    @classmethod
    def all(cls):
        cls.logger.info('Processing all Products')
        return cls.query.all()
