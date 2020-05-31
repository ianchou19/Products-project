# Copyright 2019. All Rights Reserved.
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

"""
Test cases for Product Model
Test cases can be run with:
  nosetests
  coverage report -m
"""
import sys
import unittest
import os
from werkzeug.exceptions import NotFound
from service.model import Product, DataValidationError, db
from service import app
from decimal import *

DATABASE_URI = os.getenv(
    'DATABASE_URI', 'postgres://postgres:postgres@localhost:5432/postgres')

######################################################################
#  T E S T   C A S E S
######################################################################
class TestProducts(unittest.TestCase):
    """ Test Cases for Products """

    @classmethod
    def setUpClass(cls):
        """ These run once per Test suite """
        app.debug = False
        getcontext().prec = 2
        # Set up the test database
        app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
        app.config["SQLALCHEMY_POOL_RECYCLE"] = 30

    @classmethod
    def tearDownClass(cls):
        #db.session.remove()
        pass

    def setUp(self):
        Product.init_db(app)
        db.drop_all()    # clean up the last tests
        db.create_all()  # make our sqlalchemy tables

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        db.get_engine(app).dispose()

    ##### Create a product #####
    def test_create_a_product(self):
        """ Create a product and assert that it exists """
        product = Product(name="Wagyu Tenderloin Steak", 
            category="food", stock=11, price=20.56,
            description="The most decadent, succulent cut of beef, ever.")
        self.assertTrue(product != None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Wagyu Tenderloin Steak")
        self.assertEqual(product.category, "food")
        self.assertAlmostEqual(product.price, Decimal(20.56))
        self.assertEqual(product.stock, 11)

    def test_add_a_product(self):
        """ Create a product and add it to the database """
        products = Product.all()
        self.assertEqual(products, [])
        product = Product(name="Wagyu Tenderloin Steak", 
            category="food", stock=11, price=20.56,
            description="The most decadent, succulent cut of beef, ever.")
        self.assertTrue(product != None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Wagyu Tenderloin Steak")
        self.assertEqual(product.category, "food")
        self.assertAlmostEqual(product.price, Decimal(20.56))
        self.assertEqual(product.stock, 11)
        product.save()
        # Asert that it was assigned an id and shows up in the database
        self.assertEqual(product.id, 1)
        products = Product.all()
        self.assertEqual(len(products), 1)

    ##### Update a product #####
    def test_update_a_product(self):
        """ Update a Product """
        product = Product(name="Wagyu Tenderloin Steak", 
            category="food", stock=11, price=20.56,
            description="The most decadent, succulent cut of beef, ever.")
        product.save()
        self.assertEqual(product.id, 1)
        # Change it an save it
        product.category = "beverage"
        product.save()
        self.assertEqual(product.id, 1)
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        products = Product.all()
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].category, "beverage")

    ##### Delete a product #####
    def test_delete_a_product(self):
        """ Delete a Product """
        product = Product(name="Wagyu Tenderloin Steak", 
            category="food", stock=11, price=20.56,
            description="The most decadent, succulent cut of beef, ever.")
        product.save()
        self.assertEqual(len(Product.all()), 1)
        # delete the product and make sure it isn't in the database
        product.delete()
        self.assertEqual(len(Product.all()), 0)

    def test_serialize_a_product(self):
        """ Test serialization of a Product """
        product = Product(name="Wagyu Tenderloin Steak", 
            category="food", stock=11, price=20.56,
            description="The most decadent, succulent cut of beef, ever.")
        data = product.serialize()
        self.assertNotEqual(data, None)
        self.assertIn('id', data)
        self.assertEqual(data['id'], None)
        self.assertIn('name', data)
        self.assertEqual(data['name'], "Wagyu Tenderloin Steak")
        self.assertIn('category', data)
        self.assertEqual(data['category'], "food")
        self.assertIn('stock', data)
        self.assertEqual(data['stock'], 11)
        self.assertIn('price', data)
        self.assertAlmostEqual(data['price'], 20.56)
        self.assertIn('description', data)
        self.assertEqual(data['description'], "The most decadent, succulent cut of beef, ever.")

    def test_deserialize_a_product(self):
        """ Test deserialization of a Product """
        data = {"id": 1, "name": "shampos", "category": "Health Care", "stock": 48, "price": 12.34,"description":"Test"}
        product = Product()
        product.deserialize(data)
        self.assertNotEqual(product, None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "shampos")
        self.assertEqual(product.category, "Health Care")
        self.assertEqual(product.stock, 48)
        self.assertAlmostEqual(product.price, Decimal(12.34))
        self.assertEqual(product.description, "Test")

    def test_deserialize_bad_data(self):
        """ Test deserialization of bad data """
        data = "this is not a dictionary"
        product = Product()
        self.assertRaises(DataValidationError, product.deserialize, data)

    def test_deserialize_a_miss_product(self):
        """ Test deserialization of product missing agrs """
        data = {"id": 1, "name": "shampos", "category": "Health Care"}
        product = Product()
        self.assertRaises(DataValidationError, product.deserialize, data)

    ##### Find a product #####
    def test_find_product(self):
        """ Find a Product by ID """
        Product(name="Wagyu Tenderloin Steak", 
            category="food", stock=11, price=20.56,
            description="The most decadent, succulent cut of beef, ever.").save()
        shampo = Product(name="shampos", category="Health Care", stock=48, price=12.34)
        shampo.save()
        product = Product.find(shampo.id)
        self.assertIsNot(product, None)
        self.assertEqual(product.id, shampo.id)
        self.assertEqual(product.name, "shampos")
        self.assertEqual(product.category, "Health Care")

    def test_find_by_category(self):
        """ Find Products by Category """
        Product(name="Wagyu Tenderloin Steak", 
            category="food", stock=11, price=20.56,
            description="The most decadent, succulent cut of beef, ever.").save()
        Product(name="shampos", category="Health Care", stock=48, price=12.34).save()
        products = Product.find_by_category("food")
        self.assertEqual(products[0].category, "food")
        self.assertEqual(products[0].name, "Wagyu Tenderloin Steak")
        self.assertEqual(products[0].stock, 11)

    def test_find_by_price(self):
        """ Find Products by Price """
        Product(name="Wagyu Tenderloin Steak", 
            category="food", stock=11, price=26.8,
            description="The most decadent, succulent cut of beef, ever.").save()
        Product(name="shampos", category="Health Care", stock=48, price=12.34).save()
        products = Product.find_by_price(25, 50)
        self.assertEqual(products[0].category, "food")
        self.assertEqual(products[0].name, "Wagyu Tenderloin Steak")
        self.assertEqual(products[0].stock, 11)

    def test_find_by_name(self):
        """ Find a Product by Name """
        Product(name="Wagyu Tenderloin Steak", 
            category="food", stock=11, price=20.56,
            description="The most decadent, succulent cut of beef, ever.").save()
        Product(name="shampos", category="Health Care", stock=48, price=12.34).save()
        products = Product.find_by_name("shampos")
        self.assertEqual(products[0].category, "Health Care")
        self.assertEqual(products[0].name, "shampos")
        print(products[0].price)
        print(getcontext())
        self.assertAlmostEqual(products[0].price, Decimal(12.34))
