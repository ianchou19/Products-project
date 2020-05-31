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
Test Factory to make fake objects for testing
"""
import factory
import random
from factory.fuzzy import FuzzyChoice
from service.model import Product

MIN_PRICE = 0
MAX_PRICE = 75
MIN_STOCK = 0
MAX_STOCK = 50

class ProductFactory(factory.Factory):
    """ Creates fake product that you don't have to feed """
    class Meta:
        model = Product
    id = factory.Sequence(lambda n: n)
    name = factory.Faker('first_name')
    stock = factory.LazyAttribute(lambda x: random.randrange(MIN_STOCK, MAX_STOCK))
    price = factory.LazyAttribute(lambda x: round(random.uniform(MIN_PRICE,MAX_PRICE), 2))
    description = factory.Faker('sentence')
    category = FuzzyChoice(choices=['food', 'cloth', 'electronic', 'pet'])


if __name__ == '__main__':
    for _ in range(10):
        product = ProductFactory()
        print(product.serialize())