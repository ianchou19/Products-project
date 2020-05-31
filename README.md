# Products

[![Build Status](https://travis-ci.org/Products-Squad/products.svg?branch=master)](https://travis-ci.org/Products-Squad/products)
[![codecov](https://codecov.io/gh/Products-Squad/products/branch/master/graph/badge.svg)](https://codecov.io/gh/Products-Squad/products)

This is the remote master branch for the Products team.

### Products Service Description:

The following APIs are provided in the service.

- Create a new product: [POST] `/products`
- Read the info about a product: [GET] `/products/<id>`;
- Update a product: [PUT] `/products/<id>`;
- Delete a product by id: [DELETE] `/products/<id>`;
- List products: [GET] `/products`;
- Query a product by an attribute:
  - category: [GET] `/products?category=<category>`;
  - name: [GET] `/products?name=<name>`;
- Buy a product: [PUT] `/products/<id>/buy`;

### Prerequisite Installation

To run this service, Vagrant and VirtualBox are required to be installed. After installation of Vagrant and VirtualBox, clone the project from github to your local folder.

```
git clone https://github.com/Products-Squad/products.git
cd products
```

### Running

```
vagrant up
vagrant ssh
cd /vagrant
honcho start
```

The service is running on http://localhost:5000.

### Testing

Run TDD tests with the following command, and code coverage report will be shown.

```
nosetests
coverage report -m
```

Run BDD tests with the following command.

```
behave
```

### Shutdown

Use `Ctrl+C` to stop the server.
Use the following commands to log out and shut down VM.

```
exit
vagrant halt
```

### Service on Cloud

http://nyu-product-service-f19.mybluemix.net/

### API Swagger Docs

http://nyu-product-service-f19.mybluemix.net/apidocs
