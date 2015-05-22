# -*- coding: utf-8 -*-
"""
    __init__.py

    :copyright: (c) 2015 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from trytond.pool import Pool
from product import Product, Template


def register():
    Pool.register(
        Template,
        Product,
        module='product_elasticsearch', type_='model'
    )
