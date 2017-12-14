#This file is part systemlogics_modula module for Tryton.
#The COPYRIGHT file at the top level of this repository contains
#the full copyright notices and license terms.
from trytond.pool import Pool
from . import systemlogics
from . import location
from . import product
from . import stock
from . import configuration

def register():
    Pool.register(
        systemlogics.SystemLogicsModula,
        systemlogics.SystemLogicsModulaEXPOrdiniFile,
        location.Location,
        product.Product,
        stock.ShipmentIn,
        stock.ShipmentOut,
        stock.ShipmentOutReturn,
        stock.ShipmentOutSystemlogicsModulaExportStart,
        stock.ShipmentOutSystemlogicsModulaCheckStart,
        stock.ShipmentInternal,
        product.SystemlogicsModulaArticoliResult,
        configuration.Configuration,
        module='systemlogics_modula', type_='model')
    Pool.register(
        stock.ShipmentOutSystemlogicsModulaExport,
        stock.ShipmentOutSystemlogicsModulaCheck,
        product.SystemlogicsModulaArticoli,
        module='systemlogics_modula', type_='wizard')
