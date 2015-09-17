#This file is part systemlogics_modula module for Tryton.
#The COPYRIGHT file at the top level of this repository contains
#the full copyright notices and license terms.
from trytond.pool import Pool
from trytond.model import ModelView, ModelSQL, fields
from trytond.pyson import Eval
from trytond.transaction import Transaction
from itertools import groupby
import genshi
import genshi.template
import os
import operator
import logging
import datetime
import tempfile

__all__ = ['SystemLogicsModula']

loader = genshi.template.TemplateLoader(
    os.path.join(os.path.dirname(__file__), 'template'),
    auto_reload=True)


class SystemLogicsModula(ModelSQL, ModelView):
    'SystemLogics Modula'
    __name__ = 'systemlogics.modula'
    name = fields.Char('Name', required=True)
    dbhost = fields.Selection([
        # ('odbc', 'ODBC'),
        # ('ascii', 'ASCII'),
        ('xml', 'XML'),
        # ('excel', 'Excel'),
        ], 'DB Host', required=True)
    warehouse = fields.Many2One('stock.location', "Warehouse",
        domain=[('type', '=', 'warehouse')],
        help='System Logics Warehouse')
    path = fields.Char('Path',
        states={
            'invisible': ~Eval('dbhost').in_(['xml']),
            'required': Eval('dbhost').in_(['xml']),
            },
        depends=['state'])
    active = fields.Boolean('Active', select=True)

    @staticmethod
    def default_dbhost():
        return 'xml'

    @staticmethod
    def default_path():
        return os.path.dirname(__file__)

    @staticmethod
    def default_active():
        return True

    @classmethod
    def check_xml_record(cls, records, values):
        return True

    @classmethod
    def imp_ordini(self, shipments, template='IMP_ORDINI_OUT', type_='P'):
        Location = Pool().get('stock.location')

        shipments_ordini = []
        for shipment in shipments:
            if shipment.state != 'assigned':
                continue
            if not hasattr(shipment, 'warehouse'):
                warehouse = Transaction().context.get('stock_warehouse')
                if not warehouse:
                    warehouse, = Location.search([('type', '=', 'warehouse')], limit=1)
                shipment.warehouse = warehouse
            shipments_ordini.append(shipment)

        if not shipments_ordini:
            return

        grouped_shipments = groupby(shipments_ordini, operator.attrgetter('warehouse'))
        for warehouse, shipments in grouped_shipments:
            systemlogics = self.search([
                ('name', '=', 'IMP_ORDINI'),
                ('warehouse', '=', warehouse),
                ], limit=1)
            if not systemlogics:
                logging.getLogger('systemlogics-modula').warning(
                    'Configure a IMP_ORDINI related with "%s" warehouse.' % (warehouse.name))
                return

            systemlogic, = systemlogics

            if not os.path.isdir(systemlogic.path):
                logging.getLogger('systemlogics-modula').warning(
                    'Directory "%s" not exist (ID: %s)' % (
                        systemlogic.path,
                        systemlogic.id,
                        ))
                return
    
            ordini = getattr(self, 'imp_ordini_%s' % systemlogic.dbhost)
            ordini(systemlogic, shipments, template, type_)

    @classmethod
    def imp_ordini_odbc(self, systemlogic, shipments, template):
        logging.getLogger('systemlogics-modula').error(
            'IMP_ORDINI ODBC not supported')

    @classmethod
    def imp_ordini_ascii(self, systemlogic, shipments, template):
        logging.getLogger('systemlogics-modula').error(
            'IMP_ORDINI ASCII not supported')

    @classmethod
    def imp_ordini_excel(self, systemlogic, shipments, template):
        logging.getLogger('systemlogics-modula').error(
            'IMP_ORDINI EXCEL not supported')

    @classmethod
    def imp_ordini_xml(self, systemlogic, shipments, template, type_):
        tmpl = loader.load('%s.xml' % template)

        dbname = Transaction().cursor.dbname

        for shipment in shipments:
            xml = tmpl.generate(shipment=shipment, type_=type_, datetime=datetime).render()

            with tempfile.NamedTemporaryFile(
                    dir=systemlogic.path,
                    prefix='%s-%s-' % (dbname, shipment.code),
                    suffix='.xml', delete=False) as temp:
                temp.write(xml)
            logging.getLogger('systemlogics-modula').info(
                'Generated XML %s' % (temp.name))
            temp.close()
