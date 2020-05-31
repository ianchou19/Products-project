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
Product API Service Test Suite
Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
  codecov --token=$CODECOV_TOKEN
"""

import unittest
import os
import logging
from flask_api import status    # HTTP Status Codes
from unittest.mock import MagicMock, patch

from service.model import Product, DataValidationError, db
from .product_factory import ProductFactory
from service import app
from service.service import init_db, request_validation_error, generate_apikey
from loggin.logger import initialize_logging

DATABASE_URI = os.getenv(
    'DATABASE_URI', 'postgres://postgres:postgres@localhost:5432/postgres')

######################################################################
#  T E S T   C A S E S
######################################################################


class TestProductServer(unittest.TestCase):
    """ Product Server Tests """

    @classmethod
    def setUpClass(cls):
        """ Run once before all tests """
        app.debug = False
        initialize_logging()
        # Get API key
        api_key = generate_apikey()
        app.config['API_KEY'] = api_key
        # Set up the test database
        app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        """ Runs before each test """
        init_db()
        db.drop_all()    # clean up the last tests
        db.create_all()  # create new tables
        self.app = app.test_client()
        self.headers = {
            'X-Api-Key': app.config['API_KEY']
        }

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        db.get_engine(app).dispose()

    def _create_products(self, count):
        """ Factory method to create products in bulk """
        products = []
        for _ in range(count):
            test_product = ProductFactory()
            resp = self.app.post('/products',
                                 json=test_product.serialize(),
                                 content_type='application/json',
                                 headers=self.headers)
            self.assertEqual(
                resp.status_code, status.HTTP_201_CREATED, 'Could not create test product')
            new_product = resp.get_json()
            test_product.id = new_product['id']
            products.append(test_product)
        return products

    ##### Home page #####
    def test_home_page(self):
        """ Test the Home Page """
        resp = self.app.get('/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    ##### List products #####
    def test_get_product_list(self):
        """ Get a list of Products """
        self._create_products(5)
        resp = self.app.get('/products')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 5)

    ##### Create products ####
    def test_create_product(self):
        """ Create a new Product """
        test_product = ProductFactory()
        resp = self.app.post('/products',
                             json=test_product.serialize(),
                             content_type='application/json',
                             headers=self.headers)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Make sure location header is product
        location = resp.headers.get('Location', None)
        self.assertTrue(location != None)
        # Check the data is correct
        new_product = resp.get_json()
        self.assertEqual(new_product['name'],
                         test_product.name, "Names do not match")
        self.assertEqual(
            new_product['category'], test_product.category, "Categories do not match")
        self.assertEqual(new_product['stock'],
                         test_product.stock, "Stock does not match")
        self.assertEqual(
            new_product['description'], test_product.description, "Description does not match")
        self.assertEqual(new_product['price'],
                         test_product.price, "Price does not match")
        # Check that the location header was correct
        resp = self.app.get(location,
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_product = resp.get_json()
        self.assertEqual(new_product['name'],
                         test_product.name, "Names do not match")
        self.assertEqual(
            new_product['category'], test_product.category, "Categories do not match")
        self.assertEqual(new_product['stock'],
                         test_product.stock, "Stock does not match")
        self.assertEqual(
            new_product['description'], test_product.description, "Description does not match")
        self.assertEqual(new_product['price'],
                         test_product.price, "Price does not match")

    ##### Get products #####
    def test_get_product(self):
        """ Get a single Product """
        test_product = self._create_products(1)[0]
        resp = self.app.get('/products/{}'.format(test_product.id),
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data['name'], test_product.name)

    def test_get_product_not_found(self):
        """ Get a Product thats not found """
        resp = self.app.get('/products/0')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    ##### Update products #####
    def test_update_product(self):
        """ Update an existing Product """
        # create a product to update
        test_product = ProductFactory()
        resp = self.app.post('/products',
                             json=test_product.serialize(),
                             content_type='application/json',
                             headers=self.headers)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # update the product
        new_product = resp.get_json()
        new_product['category'] = 'unknown'
        resp = self.app.put('/products/{}'.format(new_product['id']),
                            json=new_product,
                            content_type='application/json',
                            headers=self.headers)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_product = resp.get_json()
        self.assertEqual(updated_product['category'], 'unknown')

    def test_update_product_not_found(self):
        """ Update a non-existing Product """
        # new a product without posting
        test_product = ProductFactory().serialize()
        # update the product
        test_product['category'] = 'unknown'
        resp = self.app.put('/products/{}'.format(test_product['id']),
                            json=test_product,
                            content_type='application/json',
                            headers=self.headers)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_product_not_authorized(self):
        """ Update a product Not Authorized """
        # create a product to update
        test_product = ProductFactory()
        resp = self.app.post('/products',
                             json=test_product.serialize(),
                             content_type='application/json',
                             headers=self.headers)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # update the product
        new_product = resp.get_json()
        resp = self.app.put('/products/{}'.format(new_product['id']),
                            json=new_product,
                            content_type='application/json')

        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    ##### Delete a product #####
    def test_delete_product(self):
        """ Delete a Product """
        test_product = self._create_products(1)[0]
        resp = self.app.delete('/products/{}'.format(test_product.id),
                               content_type='application/json',
                               headers=self.headers)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)
        # make sure they are deleted
        resp = self.app.get('/products/{}'.format(test_product.id),
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_product_list(self):
        """ Delete a list of Products """
        self._create_products(5)
        resp = self.app.get('/products')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 5)
        resp = self.app.delete('/products/reset', headers=self.headers)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)

    ##### Query a product #####
    def test_query_product_list_by_category(self):
        """ Query Products by Category """
        products = self._create_products(10)
        test_category = products[0].category
        category_products = [
            product for product in products if product.category == test_category]
        resp = self.app.get('/products',
                            query_string='category={}'.format(test_category))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(category_products))
        # check the data just to be sure
        for product in data:
            self.assertEqual(product['category'], test_category)

    def _get_priceid_by_price(self, test_price):
        if test_price > 0 and test_price <= 25:
            return 1
        elif test_price <= 50:
            return 2
        elif test_price <= 75:
            return 3
        else:
            return 0

    def _test_price(self, price, products):
        price_products = [product for product in products
                          if self._get_priceid_by_price(product.price) == price]
        resp = self.app.get('/products',
                            query_string='price={}'.format(price))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(price_products))
        # check the data just to be sure
        for product in data:
            self.assertEqual(self._get_priceid_by_price(
                product['price']), price)

    def test_query_product_list_by_price(self):
        """ Query Products by Price """
        products = self._create_products(10)
        test_prices = [1, 2, 3]
        for price in test_prices:
            self._test_price(price, products)

    ##### Buy a product #####
    def test_buy_product_with_stock(self):
        """ Buy a Product in stock """
        # create a test product
        product = ProductFactory()
        resp = self.app.post('/products',
                             json=product.serialize(),
                             content_type='application/json',
                             headers=self.headers)
        test_product = resp.get_json()
        # update this product with stock > 0
        test_product['stock'] = 10
        resp = self.app.put('/products/{}'.format(test_product['id']),
                            json=test_product,
                            content_type='application/json',
                            headers=self.headers)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_product = resp.get_json()
        # check the data just to be sure
        self.assertEqual(updated_product['stock'], test_product['stock'])
        # buy this product
        resp = self.app.put('/products/{}/buy'.format(updated_product['id']),
                            json=updated_product,
                            content_type='application/json')
        # check the remain stock
        bought_product = resp.get_json()
        self.assertEqual(bought_product['stock'], updated_product['stock'] - 1)

    def test_buy_product_with_wrong_id(self):
        """ Try to buy a product with wrong product id """
        # create a test product
        product = ProductFactory()
        resp = self.app.post('/products',
                             json=product.serialize(),
                             content_type='application/json',
                             headers=self.headers)
        test_product = resp.get_json()
        # buy this product with wrong id
        resp = self.app.put('/products/{}/buy'.format(2),
                            json=test_product,
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_buy_product_out_of_stock(self):
        """ Buy a Product out of stock """
        # create a test product
        product = ProductFactory()
        resp = self.app.post('/products',
                             json=product.serialize(),
                             content_type='application/json',
                             headers=self.headers)
        test_product = resp.get_json()
        # update this product with stock = 0
        test_product['stock'] = 0
        resp = self.app.put('/products/{}'.format(test_product['id']),
                            json=test_product,
                            content_type='application/json',
                            headers=self.headers)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_product = resp.get_json()
        # check the data just to be sure
        self.assertEqual(updated_product['stock'], test_product['stock'])
        # buy this product with failure
        resp = self.app.put('/products/{}/buy'.format(updated_product['id']),
                            json=updated_product,
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)

    def test_invalid_method_request(self):
        """ Test a Invalid Request error """
        resp = self.app.put(
            '/products', content_type='application/json', headers=self.headers)
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_unsupported_media_type_request(self):
        """ Test a request with unsupported media type error """
        test_product = ProductFactory()
        resp = self.app.post('/products',
                             json=test_product.serialize(),
                             content_type='xxx',
                             headers=self.headers)
        self.assertEqual(resp.status_code,
                         status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_update_product_missing_name(self):
        """ Update a Product with missing name"""
        # create a test product
        product = ProductFactory()
        resp = self.app.post('/products',
                             json=product.serialize(),
                             content_type='application/json',
                             headers=self.headers)
        test_product = resp.get_json()
        del test_product['name']
        resp = self.app.put('/products/{}'.format(test_product['id']), json=test_product,
                            content_type='application/json',
                            headers=self.headers)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_product_with_empty_name(self):
        """ Update a Product with empty name"""
        # create a test product
        product = ProductFactory()
        resp = self.app.post('/products',
                             json=product.serialize(),
                             content_type='application/json',
                             headers=self.headers)
        test_product = resp.get_json()
        test_product['name'] = ''
        resp = self.app.put('/products/{}'.format(test_product['id']), json=test_product,
                            content_type='application/json',
                            headers=self.headers)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    #####  Mock data #####
    @patch('service.model.Product.find_by_name')
    def test_mock_search_data(self, product_find_mock):
        """ Test showing how to mock data """
        product_find_mock.return_value = [
            MagicMock(serialize=lambda: {'name': 'steak'})]
        resp = self.app.get('/products', query_string='name=steak')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    @patch('service.model.Product.find_by_name')
    def test_internal_server_error(self, request_mock):
        """ Test a request with internal server error """
        request_mock.return_value = None
        resp = self.app.get('/products', query_string='name=steak')
        self.assertEqual(resp.status_code,
                         status.HTTP_500_INTERNAL_SERVER_ERROR)
