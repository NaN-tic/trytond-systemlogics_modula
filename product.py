#This file is part systemlogics_modula module for Tryton.
#The COPYRIGHT file at the top level of this repository contains
#the full copyright notices and license terms.
from trytond.pool import Pool, PoolMeta

__all__ = ['Product', 'ProductCode']
__metaclass__ = PoolMeta


class Product:
    __name__ = 'product.product'

    @classmethod
    def create(cls, vlist):
        SystemLogicsModula = Pool().get('systemlogics.modula')

        products = super(Product, cls).create(vlist)

        systemlogics_products = []
        for product in products:
            if product.code and not product.codes:
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
            if values.get('code') and not values.get('codes'):
                systemlogics_products = products

        if systemlogics_products:
            SystemLogicsModula.imp_articoli(systemlogics_products)


class ProductCode:
    __name__ = 'product.code'

    @classmethod
    def create(cls, vlist):
        pool = Pool()
        SystemLogicsModula = pool.get('systemlogics.modula')
        Product = pool.get('product.product')

        codes = super(ProductCode, cls).create(vlist)

        vlist = [v.copy() for v in vlist]
        systemlogics_products = set()
        for values in vlist:
            systemlogics_products.add(values.get('product'))
        if systemlogics_products:
            products = Product.browse(list(systemlogics_products))
            SystemLogicsModula.imp_articoli(products)
        return codes

    @classmethod
    def write(cls, *args):
        pool = Pool()
        SystemLogicsModula = pool.get('systemlogics.modula')
        Product = pool.get('product.product')

        super(ProductCode, cls).write(*args)

        codes = sum(args[::2], [])
        systemlogics_products = set(c.product for c in codes)
        if systemlogics_products:
            products = Product.browse(list(systemlogics_products))
            SystemLogicsModula.imp_articoli(products)
