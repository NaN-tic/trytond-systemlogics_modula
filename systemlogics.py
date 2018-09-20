#This file is part systemlogics_modula module for Tryton.
#The COPYRIGHT file at the top level of this repository contains
#the full copyright notices and license terms.
from trytond.pool import Pool
from trytond.model import ModelView, ModelSQL, fields, Unique
from trytond.wizard import Wizard, StateTransition, StateView, Button
from trytond.pyson import Eval
from trytond.transaction import Transaction
from trytond.rpc import RPC
from itertools import groupby
from xml.dom.minidom import parseString
import genshi
import genshi.template
import os
import operator
import logging
import datetime
import tempfile

__all__ = ['SystemLogicsModula', 'SystemLogicsModulaEXPOrdiniFile',
    'SystemLogicsModulaImportEXPOrdiniFile',
    'SystemLogicsModulaImportEXPOrdiniFileStart']

loader = genshi.template.TemplateLoader(
    os.path.join(os.path.dirname(__file__), 'template'),
    auto_reload=True)
logger = logging.getLogger(__name__)


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
        help='System Logics Warehouse', required=True)
    path = fields.Char('Path',
        states={
            'invisible': ~Eval('dbhost').in_(['xml']),
            'required': Eval('dbhost').in_(['xml']),
            },
        depends=['dbhost'], required=True)
    active = fields.Boolean('Active', select=True)
    not_completed = fields.Char('Not completed',
        help='Not completed message')

    @classmethod
    def __setup__(cls):
        super(SystemLogicsModula, cls).__setup__()
        cls.__rpc__.update({
            'export_ordini_file': RPC(readonly=False),
            })

    @staticmethod
    def default_dbhost():
        return 'xml'

    @classmethod
    def default_warehouse(cls):
        Location = Pool().get('stock.location')
        locations = Location.search(cls.warehouse.domain)
        if locations:
            return locations[0].id

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
            if shipment.__name__ in [
                    'stock.shipment.in', 'stock.shipment.out.return']:
                if shipment.state not in ['received', 'done']:
                    continue
            else:
                if shipment.state != 'assigned':
                    continue

            if not hasattr(shipment, 'warehouse'):
                warehouse = Transaction().context.get('stock_warehouse')
                if not warehouse:
                    warehouse, = Location.search(
                        [('type', '=', 'warehouse')], limit=1)
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
                logger.warning(
                    'Configure a IMP_ORDINI related with "%s" warehouse.' % (
                        warehouse.name))
                return

            systemlogic, = systemlogics

            if not os.path.isdir(systemlogic.path):
                logger.warning(
                    'Directory "%s" not exist (ID: %s)' % (
                        systemlogic.path,
                        systemlogic.id,
                        ))
                return

            ordini = getattr(self, 'imp_ordini_%s' % systemlogic.dbhost)
            ordini(systemlogic, shipments, template, type_)

    @classmethod
    def imp_ordini_odbc(self, systemlogic, shipments, template, type_):
        logger.error('IMP_ORDINI ODBC not supported')

    @classmethod
    def imp_ordini_ascii(self, systemlogic, shipments, template, type_):
        logger.error('IMP_ORDINI ASCII not supported')

    @classmethod
    def imp_ordini_excel(self, systemlogic, shipments, template, type_):
        logger.error('IMP_ORDINI EXCEL not supported')

    @classmethod
    def imp_ordini_xml(self, systemlogic, shipments, template, type_):
        tmpl = loader.load('%s.xml' % template)

        dbname = Transaction().database.name

        xml = tmpl.generate(systemlogic=systemlogic, shipments=shipments,
            type_=type_, datetime=datetime).render()

        with tempfile.NamedTemporaryFile(
                dir=systemlogic.path,
                prefix='%s-%s-' % (dbname,
                    datetime.datetime.now().strftime("%Y%m%d-%H%M%S")),
                suffix='.xml', delete=False) as temp:
            temp.write(xml.encode('utf-8'))
        logger.info('Generated XML %s' % (temp.name))
        temp.close()

    @classmethod
    def imp_articoli(self, products):
        Location = Pool().get('stock.location')

        warehouse = Transaction().context.get('stock_warehouse')
        if not warehouse:
            warehouse, = Location.search(
                [('type', '=', 'warehouse')], limit=1)
        else:
            warehouse = Location(warehouse)

        systemlogics = self.search([
            ('name', '=', 'IMP_ARTICOLI'),
            ('warehouse', '=', warehouse),
            ], limit=1)
        if not systemlogics:
            logger.warning(
                'Configure a IMP_ARTICOLI related with "%s" warehouse.' % (
                    warehouse.name))
            return

        systemlogic, = systemlogics

        if not os.path.isdir(systemlogic.path):
            logger.warning(
                'Directory "%s" not exist (ID: %s)' % (
                    systemlogic.path,
                    systemlogic.id,
                    ))
            return

        articoli = getattr(self, 'imp_articoli_%s' % systemlogic.dbhost)
        articoli(systemlogic, products)

    @classmethod
    def imp_articoli_odbc(self, products):
        logger.error('IMP_ARTICOLI ODBC not supported')

    @classmethod
    def imp_articoli_ascii(self, products):
        logger.error('IMP_ARTICOLI ASCII not supported')

    @classmethod
    def imp_articoli_excel(self, products):
        logger.error('IMP_ARTICOLI EXCEL not supported')

    @classmethod
    def imp_articoli_xml(self, systemlogic, products):
        tmpl = loader.load('IMP_ARTICOLI.xml')

        dbname = Transaction().database.name

        xml = tmpl.generate(products=products).render()

        with tempfile.NamedTemporaryFile(
                dir=systemlogic.path,
                prefix='%s-%s-' % (dbname,
                    datetime.datetime.now().strftime("%Y%m%d-%H%M%S")),
                suffix='.xml', delete=False) as temp:
            temp.write(xml.encode('utf-8'))
        logger.info('Generated XML %s' % (temp.name))
        temp.close()

    @classmethod
    def export_ordini_file(cls, args=None):
        EXPOrdiniFile = Pool().get('systemlogics.modula.exp.ordini.file')

        logger.info('Start read SystemLogics Module files')
        vlist = []
        to_process = []
        for modula in cls.search([('name', '=', 'EXP_ORDINI')]):
            try:
                filenames = os.listdir(modula.path)
            except OSError as e:
                logger.warning('Error reading path: %s' % e)
                continue
            exp_ordini_files = [f.name for f in EXPOrdiniFile.search([
                ('name', 'in', filenames)])]
            for filename in filenames:
                fullname = '%s/%s' % (modula.path, filename)
                values = {}
                if filename in exp_ordini_files:
                    to_process.append(fullname)
                    continue
                try:
                    content = open(fullname, 'r').read()
                except IOError as e:
                    logger.warning('Error reading file %s: %s' % (fullname, e))
                    continue
                values['name'] = filename
                values['modula'] = modula.id
                values['content'] = content
                values['state'] = 'pending'
                vlist.append(values)
                to_process.append(fullname)

        ordini_files = EXPOrdiniFile.create(vlist)
        EXPOrdiniFile.process_export_ordini(ordini_files)
        Transaction().commit()

        for filename in to_process:
            try:
                os.remove(filename)
            except OSError:
                pass
        logger.info('Loaded SystemLogics Module %s files' % (len(to_process)))


class SystemLogicsModulaEXPOrdiniFile(ModelSQL, ModelView):
    'SystemLogics Modula EXP Ordini File'
    __name__ = 'systemlogics.modula.exp.ordini.file'
    name = fields.Char('Name', required=True)
    modula = fields.Many2One('systemlogics.modula', "Systemlogics Modula",
        required=True)
    content = fields.Text('Content', readonly=True)
    state = fields.Selection([
        ('pending', 'Pending'),
        ('in_progress', 'In progress'),
        ('failed', 'Failed'),
        ('done', 'Done'),
        ], 'State', readonly=True)

    @classmethod
    def __setup__(cls):
        super(SystemLogicsModulaEXPOrdiniFile, cls).__setup__()
        t = cls.__table__()
        cls._sql_constraints = [
            ('name_uniq', Unique(t, t.name), 'Name must be unique.'),
            ]
        cls._buttons.update({
            'process_export_ordini': {
                'invisible': ~Eval('state').in_(['pending', 'failed']),
                },
            })

    @classmethod
    def default_state(cls):
        return 'pending'

    @classmethod
    @ModelView.button
    def process_export_ordini(cls, ordini_files, trigger=None):
        ''''
        Read EXP ORDINI file
        1- Try to done a move (RIG_HOSTINF is ID move)
        2- Try to packed shipment if all moves are done
        '''
        pool = Pool()
        Move = pool.get('stock.move')
        Shipment = pool.get('stock.shipment.out')
        EXPOrdiniFile = pool.get('systemlogics.modula.exp.ordini.file')

        EXPOrdiniFile.write(ordini_files, {'state': 'in_progress'})
        Transaction().commit()

        to_do = []
        done_ordini_files = []
        fail_ordini_files = []
        shipments = set()
        for ofile in ordini_files:
            try:
                dom = parseString(ofile.content)
            except:
                fail_ordini_files.append(ofile)
                continue

            quantities = {}
            move_ids = []
            for o in dom.getElementsByTagName('EXP_ORDINI_RIGHE'):
                id_ = int(o.getElementsByTagName(
                    'RIG_HOSTINF')[0].firstChild.data)
                move_ids.append(id_)
                quantities[int(id_)] = float(
                    o.getElementsByTagName('RIG_QTAE')
                    [0].firstChild.data.replace(',', '.'))

            for move in Move.search([('id', 'in', move_ids)]):
                # TODO process shipment out and internal
                if (not move.shipment
                        or move.shipment.__name__ != 'stock.shipment.out'):
                    continue
                if (quantities[move.id] == move.quantity
                        and move.shipment.state == 'assigned'):
                    to_do.append(move)
                    shipments.add(move.shipment)
            done_ordini_files.append(ofile)

        if to_do:
            Move.do(to_do) # TODO try/except move error

        if shipments:
            Shipment._sync_inventory_to_outgoing(shipments)
            Move.assign([m for s in shipments for m in s.outgoing_moves])

        to_package = []
        for shipment in shipments:
            package = True
            for move in shipment.outgoing_moves:
                if move.state != 'assigned':
                    package = False
            if package:
                to_package.append(shipment)

        if to_package:
            Shipment.pack(to_package)

        if done_ordini_files:
            cls.write(done_ordini_files, {'state': 'done'})
        if fail_ordini_files:
            cls.write(fail_ordini_files, {'state': 'failed'})


class SystemLogicsModulaImportEXPOrdiniFileStart(ModelView):
    'SystemLogcics Modula Import EXP Ordini File Start'
    __name__ = 'systemlogics.modula.import.exp.ordini.file.start'


class SystemLogicsModulaImportEXPOrdiniFile(Wizard):
    'SystemLogics Modula Import EXP Ordini File'
    __name__ = "systemlogics.modula.import.exp.ordini.file"
    start = StateView('systemlogics.modula.import.exp.ordini.file.start',
        'systemlogics_modula.systemlogics_modula_import_exp_ordini_file_start', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Import', 'import_', 'tryton-ok', default=True),
            ])
    import_ = StateTransition()

    def transition_import_(self):
        SystemLogicsModula = Pool().get('systemlogics.modula')
        SystemLogicsModula.export_ordini_file()
        return 'end'
