#This file is part systemlogics_modula module for Tryton.
#The COPYRIGHT file at the top level of this repository contains
#the full copyright notices and license terms.
from trytond.pool import Pool, PoolMeta
from trytond.model import ModelView, fields
from trytond.wizard import Wizard, StateTransition, StateView, Button
from trytond.transaction import Transaction

__all__ = ['Product', 'SystemlogicsModulaArticoli', 'SystemlogicsModulaArticoliResult']
__metaclass__ = PoolMeta


class Product:
    __name__ = 'product.product'

    @classmethod
    def create(cls, vlist):
        SystemLogicsModula = Pool().get('systemlogics.modula')

        products = super(Product, cls).create(vlist)

        systemlogics_products = []
        for product in products:
            if product.code:
                systemlogics_products.append(product)
        if systemlogics_products:
            SystemLogicsModula.imp_articoli(systemlogics_products)
        return products

    @classmethod
    def write(cls, *args):
        SystemLogicsModula = Pool().get('systemlogics.modula')

        super(Product, cls).write(*args)

        systemlogics_products = []
        actions = iter(args)
        for products, values in zip(actions, actions):
            # generate xml if code or codes changed
            if values.get('code') or values.get('codes'):
                systemlogics_products = products

        if systemlogics_products:
            SystemLogicsModula.imp_articoli(systemlogics_products)


class SystemlogicsModulaArticoliResult(ModelView):
    'Systemlogics Modula Articoli Result'
    __name__ = 'systemlogics.modula.articoli.result'
    info = fields.Text('Info', readonly=True)


class SystemlogicsModulaArticoli(Wizard):
    'Systemlogics Modula Articoli'
    __name__ = 'systemlogics.modula.articoli'
    start_state = 'export'

    export = StateTransition()
    result = StateView('systemlogics.modula.articoli.result',
        'systemlogics_modula.systemlogics_modula_articoli_result', [
            Button('Close', 'end', 'tryton-close'),
            ])

    @classmethod
    def __setup__(cls):
        super(SystemlogicsModulaArticoli, cls).__setup__()
        cls._error_messages.update({
                'export_info': 'Export %s product/s (IMP ARTICOLI)',
                })

    def transition_export(self):
        pool = Pool()
        Product = pool.get('product.product')
        SystemLogicsModula = pool.get('systemlogics.modula')

        products = Product.browse(Transaction().context['active_ids'])
        SystemLogicsModula.imp_articoli(products)
        self.result.info = self.raise_user_error('export_info',
            (len(products)), raise_exception=False)
        return 'result'

    def default_result(self, fields):
        info_ = self.result.info
        return {
            'info': info_,
            }
