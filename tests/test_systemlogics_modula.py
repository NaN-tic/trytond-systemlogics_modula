# This file is part of the systemlogics_modula module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import unittest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import ModuleTestCase


class SystemlogicsModulaTestCase(ModuleTestCase):
    'Test Systemlogics Modula module'
    module = 'systemlogics_modula'


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        SystemlogicsModulaTestCase))
    return suite