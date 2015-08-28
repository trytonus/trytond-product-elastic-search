# -*- coding: utf-8 -*-
from pyes import BoolQuery, MatchQuery

from trytond.pool import Pool, PoolMeta

__all__ = ['Template', 'Product']
__metaclass__ = PoolMeta


class Template:
    __name__ = 'product.template'

    @classmethod
    def create(cls, vlist):
        """
        Create a record in elastic search on create
        :param vlist: List of dictionaries of fields with values
        """
        IndexBacklog = Pool().get('elasticsearch.index_backlog')
        Product = Pool().get('product.product')

        templates = super(Template, cls).create(vlist)
        products = []
        for template in templates:
            products.extend([Product(p) for p in template.products])
        IndexBacklog.create_from_records(products)
        return templates

    @classmethod
    def write(cls, templates, values, *args):
        """
        Create a record in elastic search on write
        """
        IndexBacklog = Pool().get('elasticsearch.index_backlog')
        Product = Pool().get('product.product')

        rv = super(Template, cls).write(templates, values, *args)

        products = []
        for template in templates:
            products.extend([Product(p) for p in template.products])
        IndexBacklog.create_from_records(products)
        return rv


class Product:
    __name__ = 'product.product'

    @classmethod
    def create(cls, vlist):
        """Create a record in elastic search on create
        :param vlist: List of dictionaries of fields with values
        """
        IndexBacklog = Pool().get('elasticsearch.index_backlog')

        products = super(Product, cls).create(vlist)
        IndexBacklog.create_from_records(products)
        return products

    @classmethod
    def write(cls, products, values, *args):
        """Create a record in elastic search on write
        """
        IndexBacklog = Pool().get('elasticsearch.index_backlog')
        rv = super(Product, cls).write(products, values, *args)
        IndexBacklog.create_from_records(products)
        return rv

    def elastic_search_json(self):
        """
        This method serializes product information for storage on elasticsearch
        servers. Users who wish to modify which data is sent may override this
        method in downstream modules.
        """
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'description': self.description,
            'type': self.type,
            'active': "true" if self.active else "false",
        }

    @classmethod
    def _build_es_query(cls, search_phrase):
        """
        Return an instance of `~pyes.query.Query` for the given phrase.
        If downstream modules wish to alter the behavior of search, for example
        by adding more fields to the query or changing the ranking in a
        different way, this would be the method to change.
        """
        return BoolQuery(
            should=[
                MatchQuery(
                    'code', search_phrase, boost=1.5
                ),
                MatchQuery(
                    'name', search_phrase, boost=2
                ),
                MatchQuery(
                    'name.partial', search_phrase
                ),
                MatchQuery(
                    'name.metaphone', search_phrase
                ),
            ],
            must=[
                MatchQuery(
                    'active', "true"
                ),
            ]
        )
