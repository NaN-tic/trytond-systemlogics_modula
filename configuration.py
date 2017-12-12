# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import fields
from trytond.pool import PoolMeta

__all__ = ['Configuration']


class Configuration:
    __name__ = 'stock.configuration'
    __metaclass__ = PoolMeta

    try_generate_systemlogics_modula = fields.Boolean(
        'Try Generate SystemLogic Modula',
        help="Try generate SystemLogic Modula files")
    slice_systemlogics_modula = fields.Integer(
        'Cron Slice SystemLogics Modula',
        help=("Number of blocs of shipments to generate the systemlogics "
            "modula file. If 0 or null it will be all."))

    @staticmethod
    def default_try_generate_systemlogics_modula():
        return False

    @staticmethod
    def default_slice_systemlogics_modula():
        return 100
