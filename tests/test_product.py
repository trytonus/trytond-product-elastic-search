# -*- coding: utf-8 -*-
import unittest
import time
from pyes.managers import Indices

import trytond.tests.test_tryton
from trytond.transaction import Transaction
from trytond.tests.test_tryton import POOL, USER, DB_NAME, CONTEXT


class TestProduct(unittest.TestCase):
    """
    TestProduct
    """

    def setUp(self):
        """
        Set up data used in the tests.
        this method is called before each test function execution.
        """
        trytond.tests.test_tryton.install_module('product_elasticsearch')
        self.Product = POOL.get('product.product')
        self.ProductTemplate = POOL.get('product.template')
        self.Uom = POOL.get('product.uom')
        self.IndexBacklog = POOL.get('elasticsearch.index_backlog')
        self.ElasticDocumentType = POOL.get('elasticsearch.document.type')
        self.ElasticConfig = POOL.get('elasticsearch.configuration')

    def clear_server(self):
        """
        Clear the elasticsearch server.
        """
        conn = self.ElasticConfig(1).get_es_connection()
        index_name = self.ElasticConfig(1).get_index_name(name=None)

        indices = Indices(conn)
        indices.delete_index_if_exists(index_name)

    def update_mapping(self):
        """
        Update mapping.
        """
        product_doc, = self.ElasticDocumentType.search([])
        self.ElasticConfig.update_settings([self.ElasticConfig(1)])
        self.ElasticDocumentType.update_mapping([product_doc])

    def test_0010_test_product_indexing_and_search(self):
        """
        Tests indexing and search on creation and updation of product
        """
        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            self.update_mapping()

            uom, = self.Uom.search([('symbol', '=', 'u')])

            template, = self.ProductTemplate.create([{
                'name': 'Bat Mobile',
                'type': 'goods',
                'list_price': 50000,
                'cost_price': 40000,
                'default_uom': uom.id,
            }])
            product, = self.Product.create([{
                'template': template,
                'code': 'Batman has a code',
                'description': 'This is the BatMobile',
            }])
            # Clear backlog list
            self.IndexBacklog.delete(self.IndexBacklog.search([]))
            self.assertEqual(self.IndexBacklog.search([], count=True), 0)
            self.ProductTemplate.write([template], {
                'name': 'Bat Mobile Advanced',
            })
            # Update the product
            self.Product.write([product], {
                'description': "Batman's ride",
            })
            self.assertEqual(self.IndexBacklog.search([], count=True), 1)

            # Create new product
            product, = self.Product.create([{
                'template': template,
                'code': 'AVENGE',
                'description': 'Avengers beats Justice League',
            }])

            # Update index on Elastic-Search server
            self.IndexBacklog.update_index()
            time.sleep(2)

            # Test if new records have been uploaded on elastic server
            # If Index Backlog if empty, it means the records got updated
            self.assertEqual(self.IndexBacklog.search([], count=True), 0)

            conn = self.ElasticConfig(1).get_es_connection(timeout=5)
            search_obj = self.Product._build_es_query('Batman').search()

            results = conn.search(
                search_obj,
                doc_types=[self.ElasticConfig(1).make_type_name(
                    'product.product'
                )]
            )
            self.assertEqual(len(results), 1)

            self.clear_server()


def suite():
    "Define suite"
    test_suite = trytond.tests.test_tryton.suite()
    test_suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(TestProduct)
    )
    return test_suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
