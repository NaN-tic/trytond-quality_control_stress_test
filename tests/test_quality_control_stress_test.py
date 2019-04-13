# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import unittest
from decimal import Decimal

import trytond.tests.test_tryton
from trytond.pool import Pool
from trytond.tests.test_tryton import ModuleTestCase, with_transaction

from trytond.modules.company.tests import create_company, set_company


class TestCase(ModuleTestCase):
    'Test module'
    module = 'quality_control_stress_test'

    @with_transaction()
    def test_account_debit_credit(self):
        'Test account debit/credit'
        pool = Pool()
        Uom = pool.get('product.uom')
        Template = pool.get('product.template')
        Product = pool.get('product.product')
        Model = pool.get('ir.model')
        Sequence = pool.get('ir.sequence')
        CualityConfiguration = pool.get('quality.configuration')
        QualityProof = pool.get('quality.proof')
        QualityValue = pool.get('quality.qualitative.value')
        QualityMethod = pool.get('quality.proof.method')
        QualityValue = pool.get('quality.qualitative.value')
        QualityTemplate = pool.get('quality.template')
        QualitytTest = pool.get('quality.test')

        # Create Company
        company = create_company()
        with set_company(company):

            # Create Product
            unit, = Uom.search([
                    ('name', '=', 'Unit'),
                    ])
            template, = Template.create([{
                        'name': 'Product',
                        'default_uom': unit.id,
                        'type': 'goods',
                        'list_price': Decimal(30),
                        }])
            product, = Product.create([{
                        'template': template.id,
                        }])

            # Configure Quality Control
            sequence, = Sequence.search([('code', '=', 'quality.test')])
            allowed_doc, = Model.search([('model', '=', 'product.product')])
            CualityConfiguration.create([{
                        'allowed_documents': [('create', [{
                                            'quality_sequence': sequence.id,
                                            'document': allowed_doc.id,
                                            }])],
                        }])

            # Create Qualitative Proof
            qlproof, = QualityProof.create([{
                        'name': 'Qualitative Proof',
                        'type': 'qualitative',
                        'methods': [('create', [{
                                            'name': 'Method 1',
                                            'possible_values': [('create', [{
                                                            'name': 'Val 1',
                                                            }, {
                                                            'name': 'Val 2',
                                                            }])]
                                            }])],
                        }])

            # Create Quantitative Proof
            qtproof, = QualityProof.create([{
                        'name': 'Quantitative Proof',
                        'type': 'quantitative',
                        'methods': [('create', [{
                                            'name': 'Method 2',
                                            }])],
                        }])

            # Look For Values
            method1, = QualityMethod.search([('name', '=', 'Method 1')])
            method2, = QualityMethod.search([('name', '=', 'Method 2')])
            val1, = QualityValue.search([('name', '=', 'Val 1')])
            val2, = QualityValue.search([('name', '=', 'Val 2')])

            # Create Quality Template
            quality_template, = QualityTemplate.create([{
                        'name': 'Template 1',
                        'document': str(product),
                        'internal_description': 'Internal description',
                        'external_description': 'External description',
                        'environments': [('create', [{
                                        'name': 'High Temperature',
                                        }, {
                                        'name': 'Low Temperature',
                                        }])],
                        }])

            high_temperature, low_temperature = quality_template.environments
            QualityTemplate.write([quality_template], {
                        'qualitative_lines': [('create', [{
                                        'name': 'Line1',
                                        'proof': qlproof.id,
                                        'method': method1.id,
                                        'environment': high_temperature.id,
                                        'valid_value': val1.id,
                                        'internal_description':
                                        'quality line intenal description',
                                        'external_description':
                                        'quality line external description',
                                        }])],
                        'quantitative_lines': [('create', [{
                                        'name': 'Quantitative Line',
                                        'proof': qtproof.id,
                                        'method': method2.id,
                                        'environment': low_temperature.id,
                                        'unit': unit.id,
                                        'internal_description':
                                        'quality line intenal description',
                                        'external_description':
                                        'quality line external description',
                                        'min_value': Decimal('1.00'),
                                        'max_value': Decimal('2.00'),
                                        }])],
                        })

            # Create And assing template to Test
            test, = QualitytTest.create([{
                        'number': 'TEST/',
                        'document': str(product),
                        'templates': [('add', [quality_template.id])],
                        }])
            test.apply_template_values()

            # Test that values are assigned corretly::
            high_stress_test, low_stress_test = test.stress_tests
            self.assertEqual(high_stress_test.environment, high_temperature)
            high_stress_test.start
            high_stress_test.end
            self.assertEqual(low_stress_test.environment, low_temperature)
            low_stress_test.start
            low_stress_test.end
            ql_line, = test.qualitative_lines
            self.assertEqual(ql_line.stress_test, high_stress_test)
            qt_line, = test.quantitative_lines
            self.assertEqual(qt_line.stress_test, low_stress_test)


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCase))
    return suite
