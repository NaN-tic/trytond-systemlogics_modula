#This file is part systemlogics_modula module for Tryton.
#The COPYRIGHT file at the top level of this repository contains
#the full copyright notices and license terms.
from trytond.pool import PoolMeta
from trytond.model import fields
from trytond.pyson import Not, Bool, Eval, Equal

__all__ = ['Location']
__metaclass__ = PoolMeta


class Location:
    __name__ = 'stock.location'
    systemlogics_modula = fields.Boolean('SystemLogics Modula',
        states={
            'invisible': Eval('type') == 'warehouse',
            'readonly': Not(Bool(Eval('active'))),
            },
        depends=['type', 'active'],
        help='SystemLogics Modula location')

    @fields.depends('parent')
    def on_change_with_systemlogics_modula(self, name=None):
        # if parent is a systemlogics location, mark true
        if self.parent and self.parent.systemlogics_modula:
            return True
        return False
