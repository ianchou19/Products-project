# Copyright 2016, 2019 John J. Rofrano. All Rights Reserved.
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
Product Service

Paths:
------
GET /products - Returns a list all of the Products
GET /products/{id} - Returns the Product with a given id number
POST /products - creates a new Product record in the database
PUT /products/{id} - updates a Product record in the database
DELETE /products/{id} - deletes a Product record in the database
GET /products?category={category} - query a list of the Products match the specific category
PUT /products/{id}/buy - updates the purchase amoubt of a Product record
"""

import uuid
from functools import wraps
from flask import Flask, jsonify, request, url_for, make_response, abort
from flask_api import status
from flask import jsonify, request, url_for, make_response
from flask_restplus import Api, Resource, fields, reqparse, inputs
# Import Flask application
from . import app
from werkzeug.exceptions import NotFound
from service.model import Product, DataValidationError

# The type of autorization required
authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'X-Api-Key'
    }
}

######################################################################
# RESTPlus Service
######################################################################
######################################################################
# GET INDEX
######################################################################
@app.route('/')
def index():
    """ Root URL response """
    # return jsonify(name='Product REST API Service',
    #                version='1.0',
    #                paths=url_for('list_products', _external=True)
    #                ), status.HTTP_200_OK
    # return index.html from static folder
    return app.send_static_file('index.html')


######################################################################
# GET HEALTH CHECK
######################################################################
@app.route('/healthcheck')
def healthcheck():
    """ Let them know our heart is still beating """
    return make_response(jsonify(status=200, message='Healthy'), status.HTTP_200_OK)


######################################################################
# Configure Swagger before initilaizing it
######################################################################
api = Api(app,
          version='1.0.0',
          title='Product REST API Service',
          description='This is a Product server.',
          default='products',
          default_label='Product operations',
          doc='/apidocs',  # default also could use doc='/apidocs/'
          authorizations=authorizations
          # prefix='/api'
          )


# Define data model so that docs reflect what can be sent
product_model = api.model('Product', {
    'id': fields.Integer(readOnly=True,
                         description='A unique id is assigned automatically by service'),
    'name': fields.String(required=True,
                          description='The name of the product'),
    'price': fields.Float(required=True,
                          description='The price of the product'),
    'stock': fields.Integer(required=True,
                            description='The number of the product in stock'),
    'description': fields.String(required=True,
                                 description='Information describing the product'),
    'category': fields.String(required=True,
                              description='The category of the product')
})

create_model = api.model('Product', {
    'name': fields.String(required=True,
                          description='The name of the product'),
    'price': fields.Float(required=True,
                          description='The price of the product'),
    'stock': fields.Integer(required=True,
                            description='The number of the product in stock'),
    'description': fields.String(required=True,
                                 description='Information describing the product'),
    'category': fields.String(required=True,
                              description='The category of the product')
})


# query string arguments
product_args = reqparse.RequestParser()
product_args.add_argument(
    'name', type=str, required=False, help='List Products by name')
product_args.add_argument('category', type=str,
                          required=False, help='List Products by category')
product_args.add_argument(
    'price', type=int, required=False, help='List Products by price')


######################################################################
# Special Error Handlers
######################################################################
@api.errorhandler(DataValidationError)
def request_validation_error(error):
    """ Handles Value Errors from bad data """
    message = str(error)
    app.logger.error(message)
    return {'status_code': status.HTTP_400_BAD_REQUEST,
            'error': 'Bad Request',
            'message': message}, status.HTTP_400_BAD_REQUEST


######################################################################
# Generate a random API key
######################################################################
def generate_apikey():
    """ Helper function for generating API keys """
    return uuid.uuid4().hex

def get_apikey_for_behave():
    return app.config['API_KEY']

######################################################################
# Authorization Decorator
######################################################################
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'X-Api-Key' in request.headers:
            token = request.headers['X-Api-Key']
            app.config['API_KEY'] = token
        # if app.config.get('API_KEY') and app.config['API_KEY'] == token:
            return f(*args, **kwargs)
        else:
            return {'message': 'Invalid or missing token'}, 401
    return decorated


######################################################################
#  PATH: /products/{id}
######################################################################
@api.route('/products/<product_id>')
@api.param('product_id', 'The Product identifier')
class ProductResource(Resource):
    """
    ProductResource class

    Allows the manipulation of a single Product
    GET /product{id} - Returns a Product with the id
    PUT /product{id} - Update a Product with the id
    DELETE /product{id} -  Deletes a Product with the id
    """
    # ------------------------------------------------------------------
    # RETRIEVE A PRODUCT
    # ------------------------------------------------------------------
    @api.doc('get_products')
    @api.response(404, 'Product not found')
    @api.marshal_with(product_model)
    def get(self, product_id):
        """
        Retrieve a single Product 
        This endpoint will return a Product based on it's id
        """
        app.logger.info('Request for product with id: %s', product_id)
        product = Product.find(product_id)
        if not product:
            api.abort(status.HTTP_404_NOT_FOUND,
                      "Product with id '{}' was not found.".format(product_id))
        return product.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # UPDATE AN EXISTING PRODUCT
    # ------------------------------------------------------------------
    @api.doc('update_products', security='apikey')
    @api.response(404, 'Product not found')
    @api.response(400, 'The posted Product data was not valid')
    @api.expect(product_model)
    @api.marshal_with(product_model)
    @token_required
    def put(self, product_id):
        app.logger.info('Request to update product with id: %s', product_id)
        check_content_type('application/json')
        product = Product.find(product_id)
        if not product:
            api.abort(status.HTTP_404_NOT_FOUND,
                      "Product with id {} was not found.".format(product_id))
        app.logger.debug('Payload = %s', api.payload)
        data = api.payload
        product.deserialize(data)
        product.id = product_id
        product.save()
        return product.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DELETE A PRODUCT
    # ------------------------------------------------------------------
    @api.doc('delete_products', security='apikey')
    @api.response(204, 'Product deleted')
    @token_required
    def delete(self, product_id):
        """Delete a Product by id"""
        app.logger.info(
            'Request to delete product with the id [%s] provided', product_id)
        product = Product.find(product_id)
        if product:
            product.delete()
        return '', status.HTTP_204_NO_CONTENT

######################################################################
#  PATH: /products
######################################################################
@api.route('/products', strict_slashes=False)
class ProductCollection(Resource):
    """ Handles all interactions with collections of Products """
    # ------------------------------------------------------------------
    # LIST ALL PRODUCTS
    # QUERY PRODUCTS LISTS BY ATTRIBUTE
    # ------------------------------------------------------------------
    @api.doc('list_products')
    @api.expect(product_args, validate=True)
    @api.marshal_list_with(product_model)
    def get(self):
        """Returns all of the Products"""
        app.logger.info('Request for product list')
        products = []
        category = request.args.get('category')
        name = request.args.get('name')
        price = request.args.get('price')
        if category:
            products = Product.find_by_category(category)
        elif name:
            products = Product.find_by_name(name)
        elif price and int(price) > 0 and int(price) < 4:  # query price by range
            if int(price) == 1:
                products = Product.find_by_price(0, 25)
            elif int(price) == 2:
                products = Product.find_by_price(25, 50)
            else:
                products = Product.find_by_price(50, 75)
        else:
            products = Product.all()
        results = [product.serialize() for product in products]
        return results, status.HTTP_200_OK

    # ------------------------------------------------------------------
    # ADD A NEW PRODUCT
    # ------------------------------------------------------------------
    @api.doc('create_products', security='apikey')
    @api.expect(create_model)
    @api.response(400, 'The posted Product data was not valid')
    @api.response(201, 'Product created successfully')
    @api.marshal_with(product_model, code=201)
    @token_required
    def post(self):
        """
        Creates a Product
        This endpoint will create a Product based the data in the body that is posted
        """
        app.logger.info('Request to create a product')
        check_content_type('application/json')
        product = Product()
        app.logger.debug('Payload = %s', api.payload)
        product.deserialize(api.payload)
        product.save()
        location_url = api.url_for(
            ProductResource, product_id=product.id, _external=True)
        return product.serialize(), status.HTTP_201_CREATED, {'Location': location_url}

######################################################################
#  PATH: /products/{id}/buy
######################################################################
@api.route('/products/<product_id>/buy')
@api.param('product_id', 'The Product identifier')
class BuyResource(Resource):
    """ Buy actions on a Product """
    # ------------------------------------------------------------------
    # BUY A PRODUCT
    # ------------------------------------------------------------------
    @api.doc('buy_products')
    @api.response(404, 'Product not found')
    @api.response(409, 'The Product is not available for purchase')
    @api.marshal_with(product_model)
    def put(self, product_id):
        """Buy a Product by id"""
        app.logger.info('Request for buy a product')
        product = Product.find(product_id)
        if not product:
            api.abort(status.HTTP_404_NOT_FOUND,
                      "Product with id '{}' was not found.".format(product_id))
        elif product.stock == 0:
            api.abort(status.HTTP_409_CONFLICT,
                      "Product with id '{}' has been sold out!".format(product_id))
        else:
            product.stock = product.stock - 1
        product.save()
        app.logger.info('Product with id [%s] has been bought!', product.id)
        return product.serialize(), status.HTTP_200_OK

######################################################################
# DELETE ALL PRODUCTS (for testing only)
######################################################################
@app.route('/products/reset', methods=['DELETE'])
def delete_products_all():
    """Delete all Products"""
    app.logger.info('Request to delete all products')
    Product.delete_all()
    return make_response('', status.HTTP_204_NO_CONTENT)

# Deprecated code
# @app.errorhandler(status.HTTP_404_NOT_FOUND)
# def not_found(error):
#     """ Handles resources not found with 404_NOT_FOUND """
#     message = str(error)
#     app.logger.warning(message)
#     return jsonify(status=status.HTTP_404_NOT_FOUND,
#                    error='Not Found',
#                    message=message), status.HTTP_404_NOT_FOUND


# @app.errorhandler(status.HTTP_405_METHOD_NOT_ALLOWED)
# def method_not_supported(error):
#     """ Handles unsuppoted HTTP methods with 405_METHOD_NOT_SUPPORTED """
#     message = str(error)
#     app.logger.warning(message)
#     return jsonify(status=status.HTTP_405_METHOD_NOT_ALLOWED,
#                    error='Method not Allowed',
#                    message=message), status.HTTP_405_METHOD_NOT_ALLOWED


# @app.errorhandler(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
# def mediatype_not_supported(error):
#     """ Handles unsuppoted media requests with 415_UNSUPPORTED_MEDIA_TYPE """
#     message = str(error)
#     app.logger.warning(message)
#     return jsonify(status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
#                    error='Unsupported media type',
#                    message=message), status.HTTP_415_UNSUPPORTED_MEDIA_TYPE


# @app.errorhandler(status.HTTP_500_INTERNAL_SERVER_ERROR)
# def internal_server_error(error):
#     """ Handles unexpected server error with 500_SERVER_ERROR """
#     message = str(error)
#     app.logger.error(message)
#     return jsonify(status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                    error='Internal Server Error',
#                    message=message), status.HTTP_500_INTERNAL_SERVER_ERROR

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################
@app.before_first_request
def init_db():
    """ Initialies the SQLAlchemy app """
    global app
    Product.init_db(app)


def check_content_type(content_type):
    """ Checks that the media type is correct """
    if request.headers['Content-Type'] == content_type:
        return
    app.logger.error('Invalid Content-Type: %s',
                     request.headers['Content-Type'])
    abort(415, 'Content-Type must be {}'.format(content_type))
