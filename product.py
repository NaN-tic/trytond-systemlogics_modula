#This file is part systemlogics_modula module for Tryton.
#The COPYRIGHT file at the top level of this repository contains
#the full copyright notices and license terms.
from trytond.pool import Pool, PoolMeta

__all__ = ['ProductCode']
__metaclass__ = PoolMeta
_TYPE_BARCODES = ['EAN13']


class ProductCode:
    __name__ = 'product.code'

    @classmethod
    def validate(cls, codes):
        super(ProductCode, cls).validate(codes)
        for code in codes:
            code.systemlogics_modula()

    def systemlogics_modula(self):
        SystemLogicsModula = Pool().get('systemlogics.modula')

        if self.barcode in _TYPE_BARCODES and self.number:
            SystemLogicsModula.imp_articoli([self.product])
