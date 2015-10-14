#This file is part systemlogics_modula module for Tryton.
#The COPYRIGHT file at the top level of this repository contains
#the full copyright notices and license terms.
from trytond.pool import Pool, PoolMeta
from trytond.model import fields
from trytond.transaction import Transaction

__all__ = ['ShipmentOut', 'ShipmentInternal']
__metaclass__ = PoolMeta


class ShipmentOut:
    __name__ = 'stock.shipment.out'
    systemlogics_modula = fields.Boolean('SystemLogics Modula')

    @staticmethod
    def default_systemlogics_modula():
        return False

    @classmethod
    def generate_systemlogics_modula(cls, shipments):
        '''Active System Logics process when a move from location is systemlogics marked'''
        SystemLogicsModula = Pool().get('systemlogics.modula')

        systemlogics_shipments = []
        for s in shipments:
            if hasattr(s, 'review'):
                if s.review:
                    continue
            systemLogics = False
            for move in s.inventory_moves:
                if move.from_location.systemlogics_modula:
                    systemLogics = True
                    break
            if systemLogics:
                systemlogics_shipments.append(s)

        if systemlogics_shipments:
            cls.write(systemlogics_shipments, {'systemlogics_modula': True})

            # Force not get a rollback to generate XML file
            shipment_ids = [s.id for s in systemlogics_shipments]
            Transaction().cursor.commit()
            # Search shipment ID to sure not have a rollback
            shipments = cls.search([
                ('id', 'in', shipment_ids),
                ])
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
                    dep_shipments, template='IMP_ORDINI_IN', type_='V')

    @classmethod
    def assign(cls, shipments):
        super(ShipmentInternal, cls).assign(shipments)
        cls.generate_systemlogics_modula(shipments)
