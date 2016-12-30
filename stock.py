#This file is part systemlogics_modula module for Tryton.
#The COPYRIGHT file at the top level of this repository contains
#the full copyright notices and license terms.
from trytond.pool import Pool, PoolMeta
from trytond.model import  ModelView, fields
from trytond.transaction import Transaction
from trytond.pyson import Eval
from trytond.wizard import Wizard, StateView, Button, StateTransition

__all__ = ['ShipmentIn', 'ShipmentOut', 'ShipmentInternal', 'Move',
    'ShipmentOutSystemlogicsModulaExportStart', 'ShipmentOutSystemlogicsModulaExport']
__metaclass__ = PoolMeta


class ShipmentIn:
    __name__ = 'stock.shipment.in'
    systemlogics_modula = fields.Boolean('SystemLogics Modula')

    @classmethod
    def __setup__(cls):
        super(ShipmentIn, cls).__setup__()
        cls._buttons.update({
            'do_systemlogics_modula': {
                'invisible': Eval('state').in_(['draft', 'cancel']),
                },
            })

    @staticmethod
    def default_systemlogics_modula():
        return False

    @classmethod
    def copy(cls, shipments, default=None):
        if default is None:
            default = {}
        default = default.copy()
        default['systemlogics_modula'] = None
        return super(ShipmentIn, cls).copy(shipments, default=default)

    @classmethod
    def generate_systemlogics_modula(cls, shipments):
        '''Active System Logics process when a move location is systemlogics marked'''
        SystemLogicsModula = Pool().get('systemlogics.modula')

        deposit_shipments = []
        for s in shipments:
            systemLogics = False
            for move in s.inventory_moves:
                if move.to_location.systemlogics_modula:
                    systemLogics = True

            if systemLogics:
                deposit_shipments.append(s)

        if deposit_shipments:
            cls.write(deposit_shipments, {'systemlogics_modula': True})

            # Force not get a rollback to generate XML file
            shipment_ids = [s.id for s in deposit_shipments]
            Transaction().cursor.commit()
            # Search shipment ID to sure not have a rollback
            shipments = cls.search([
                ('id', 'in', shipment_ids),
                ])
            SystemLogicsModula.imp_ordini(
                shipments, template='IMP_ORDINI_IN', type_='V')

    @classmethod
    @ModelView.button
    def do_systemlogics_modula(cls, shipments):
        cls.generate_systemlogics_modula(shipments)


class ShipmentOut:
    __name__ = 'stock.shipment.out'
    systemlogics_modula = fields.Boolean('SystemLogics Modula')
    systemlogics_modula_completed = fields.Boolean(
        'SystemLogics Modula Completed')

    @staticmethod
    def default_systemlogics_modula():
        return False

    @classmethod
    def copy(cls, shipments, default=None):
        if default is None:
            default = {}
        default = default.copy()
        default['systemlogics_modula'] = None
        default['systemlogics_modula_completed'] = None
        return super(ShipmentOut, cls).copy(shipments, default=default)

    @classmethod
    def generate_systemlogics_modula(cls, shipments):
        '''Active System Logics process when a move from location is systemlogics marked'''
        SystemLogicsModula = Pool().get('systemlogics.modula')

        s_completed = [] # shipments completed
        s_incompleted = [] # shipments incompleted
        for s in shipments:
            if hasattr(s, 'review'):
                if s.review:
                    continue
            systemLogics = False
            completed = True
            for move in s.inventory_moves:
                if move.from_location.systemlogics_modula:
                    systemLogics = True
                else:
                    completed = False
            if systemLogics:
                if completed:
                    s_completed.append(s)
                else:
                    s_incompleted.append(s)

        if s_completed or s_incompleted:
            if s_completed:
                cls.write(s_completed, {
                    'systemlogics_modula': True,
                    'systemlogics_modula_completed': True,
                    })
            if s_incompleted:
                cls.write(s_incompleted, {
                    'systemlogics_modula': True,
                    'systemlogics_modula_completed': False,
                    })

            # Force not get a rollback to generate XML file
            shipment_ids = [s.id for s in (s_completed + s_incompleted)]
            Transaction().cursor.commit()
            # Search shipment ID to sure not have a rollback
            shipments = cls.search([
                ('id', 'in', shipment_ids),
                ], order=[('systemlogics_modula_completed', 'DESC')])
            SystemLogicsModula.imp_ordini(
                shipments, template='IMP_ORDINI_OUT', type_='P')

    @classmethod
    def assign(cls, shipments):
        super(ShipmentOut, cls).assign(shipments)
        # control generate systemlogics module with context
        if Transaction().context.get('generate_systemlogics_modula', True):
            cls.generate_systemlogics_modula(shipments)


class ShipmentInternal:
    __name__ = 'stock.shipment.internal'
    systemlogics_modula = fields.Boolean('SystemLogics Modula')

    @staticmethod
    def default_systemlogics_modula():
        return False

    @classmethod
    def copy(cls, shipments, default=None):
        if default is None:
            default = {}
        default = default.copy()
        default['systemlogics_modula'] = None
        return super(ShipmentInternal, cls).copy(shipments, default=default)

    @classmethod
    def generate_systemlogics_modula(cls, shipments):
        '''Active System Logics process when a move location is systemlogics marked'''
        SystemLogicsModula = Pool().get('systemlogics.modula')

        extract_shipments = []
        deposit_shipments = []
        for s in shipments:
            if s.from_location.systemlogics_modula:
                extract_shipments.append(s)
            if s.to_location.systemlogics_modula:
                deposit_shipments.append(s)

        if extract_shipments or deposit_shipments:
            cls.write(extract_shipments + deposit_shipments, {'systemlogics_modula': True})

            # Force not get a rollback to generate XML file
            extract_shipments_ids = [shipment.id for shipment in extract_shipments]
            deposit_shipments_ids = [shipment.id for shipment in deposit_shipments]
            Transaction().cursor.commit()

            if extract_shipments_ids:
                # Search shipment ID to sure not have a rollback
                ext_shipments = cls.search([
                    ('id', 'in', extract_shipments_ids),
                    ])
                SystemLogicsModula.imp_ordini(
                    ext_shipments, template='IMP_ORDINI_IN', type_='P')
            if deposit_shipments_ids:
                # Search shipment ID to sure not have a rollback
                dep_shipments = cls.search([
                    ('id', 'in', deposit_shipments_ids),
                    ])
                SystemLogicsModula.imp_ordini(
                    dep_shipments, template='IMP_ORDINI_INTERNAL', type_='V')

    @classmethod
    def assign(cls, shipments):
        super(ShipmentInternal, cls).assign(shipments)
        cls.generate_systemlogics_modula(shipments)


class Move:
    __name__ = 'stock.move'
    modula_notes = fields.Function(fields.Char('Modula Notes'),
        'get_modula_notes')

    def get_modula_notes(self, name):
        return


class ShipmentOutSystemlogicsModulaExportStart(ModelView):
    'Customer shipments export Systemlogics Modula Start'
    __name__ = 'stock.shipment.out.systemlogics.modula.export.start'
    shipments = fields.Many2Many('stock.shipment.out', None, None, 'Shipments',
        domain=[
            ('state', 'in', ['assigned']),
            ],
        states={
            'required': True,
            },
        help='Assigned customer shipments to export Systemlogics Modula.')

    @staticmethod
    def default_shipments():
        ShipmentOut = Pool().get('stock.shipment.out')

        active_ids = Transaction().context.get('active_ids', [])
        shipments =  ShipmentOut.search([
            ('id', 'in', active_ids),
            ('state', 'in', ['assigned']),
            ])
        return [s.id for s in shipments]


class ShipmentOutSystemlogicsModulaExport(Wizard):
    'Customer shipments export Systemlogics Modula'
    __name__ = 'stock.shipment.out.systemlogics.modula.export'

    start = StateView('stock.shipment.out.systemlogics.modula.export.start',
        'systemlogics_modula.shipment_out_export_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Export', 'export', 'tryton-ok', True),
            ])
    export = StateTransition()

    def transition_export(self):
        ShipmentOut = Pool().get('stock.shipment.out')

        shipments = self.start.shipments
        if shipments:
            ShipmentOut.generate_systemlogics_modula(shipments)
        return 'end'
