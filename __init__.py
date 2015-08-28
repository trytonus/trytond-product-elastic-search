# -*- coding: utf-8 -*-
from trytond.pool import Pool
from product import Product, Template


def register():
    Pool.register(
        Template,
        Product,
        module='product_elasticsearch', type_='model'
    )
