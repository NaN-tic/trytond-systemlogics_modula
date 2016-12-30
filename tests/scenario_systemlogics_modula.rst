============================
Systemlogics Modula Scenario
============================

Imports::

    >>> import datetime
    >>> from dateutil.relativedelta import relativedelta
    >>> from decimal import Decimal
    >>> from proteus import config, Model, Wizard
    >>> from trytond.modules.company.tests.tools import create_company, \
    ...     get_company
    >>> today = datetime.date.today()
    >>> yesterday = today - relativedelta(days=1)

Create database::

    >>> config = config.set_trytond()
    >>> config.pool.test = True

Install stock Module::

    >>> Module = Model.get('ir.module')
    >>> module, = Module.find([('name', '=', 'systemlogics_modula')])
    >>> module.click('install')
    >>> Wizard('ir.module.install_upgrade').execute('upgrade')

Create company::

    >>> _ = create_company()
    >>> company = get_company()

Reload the context::

    >>> User = Model.get('res.user')
    >>> config._context = User.get_preferences(True, config.context)

Create customer::

    >>> Party = Model.get('party.party')
    >>> customer = Party(name='Customer')
    >>> customer.save()
    >>> supplier = Party(name='Supplier')
    >>> supplier.save()

Create category::

    >>> ProductCategory = Model.get('product.category')
    >>> category = ProductCategory(name='Category')
    >>> category.save()

Create product::

    >>> ProductUom = Model.get('product.uom')
    >>> ProductTemplate = Model.get('product.template')
    >>> Product = Model.get('product.product')
    >>> unit, = ProductUom.find([('name', '=', 'Unit')])
    >>> product = Product()
    >>> template = ProductTemplate()
    >>> template.name = 'Product'
    >>> template.category = category
    >>> template.default_uom = unit
    >>> template.type = 'goods'
    >>> template.list_price = Decimal('20')
    >>> template.cost_price = Decimal('8')
    >>> template.save()
    >>> product.template = template
    >>> product.save()
    >>> product.code = 'PROD'
    >>> product.save()

Get stock locations::

    >>> Location = Model.get('stock.location')
    >>> warehouse_loc, = Location.find([('code', '=', 'WH')])
    >>> supplier_loc, = Location.find([('code', '=', 'SUP')])
    >>> customer_loc, = Location.find([('code', '=', 'CUS')])
    >>> output_loc, = Location.find([('code', '=', 'OUT')])
    >>> storage_loc, = Location.find([('code', '=', 'STO')])
    >>> lost_found_loc, = Location.find([('name', '=', 'Lost and Found')])

Create Systemlogics Modula and mark storage location to modula location::

    >>> SystemLogicsModula = Model.get('systemlogics.modula')
    >>> modula = SystemLogicsModula()
    >>> modula.name = 'IMP_ORDINI'
    >>> modula.dbhost = 'xml'
    >>> modula.warehouse = warehouse_loc
    >>> modula.save()

    >>> modula2 = SystemLogicsModula()
    >>> modula2.name = 'EXP_ORDINI'
    >>> modula2.dbhost = 'xml'
    >>> modula2.warehouse = warehouse_loc
    >>> modula2.save()

    >>> modula3 = SystemLogicsModula()
    >>> modula3.name = 'IMP_ARTICOLI'
    >>> modula3.dbhost = 'xml'
    >>> modula3.warehouse = warehouse_loc
    >>> modula3.save()

    >>> storage_loc.systemlogics_modula = True
    >>> storage_loc.save()

Create Shipment In::

    >>> StockMove = Model.get('stock.move')
    >>> ShipmentIn = Model.get('stock.shipment.in')
    >>> shipment_in = ShipmentIn()
    >>> shipment_in.planned_date = today
    >>> shipment_in.supplier = supplier
    >>> shipment_in.warehouse = warehouse_loc
    >>> shipment_in.company = company
    >>> move = StockMove()
    >>> shipment_in.incoming_moves.append(move)
    >>> move.product = product
    >>> move.uom = unit
    >>> move.quantity = 10
    >>> move.from_location = supplier_loc
    >>> move.to_location = shipment_in.warehouse.input_location
    >>> move.company = company
    >>> move.unit_price = Decimal('1')
    >>> move.currency = company.currency
    >>> shipment_in.save()
    >>> shipment_in.click('receive')
    >>> shipment_in.click('done')
    >>> shipment_in.click('do_systemlogics_modula')
    >>> bool(shipment_in.systemlogics_modula)
    True

Create Shipment Out::

    >>> ShipmentOut = Model.get('stock.shipment.out')
    >>> shipment_out = ShipmentOut()
    >>> shipment_out.planned_date = today
    >>> shipment_out.customer = customer
    >>> shipment_out.warehouse = warehouse_loc
    >>> shipment_out.company = company
    >>> move = StockMove()
    >>> shipment_out.outgoing_moves.append(move)
    >>> move.product = product
    >>> move.uom = unit
    >>> move.quantity = 1
    >>> move.from_location = output_loc
    >>> move.to_location = customer_loc
    >>> move.company = company
    >>> move.unit_price = Decimal('1')
    >>> move.currency = company.currency
    >>> shipment_out.save()
    >>> shipment_out.click('wait')
    >>> shipment_out.click('assign_try')
    True
    >>> bool(shipment_out.systemlogics_modula)
    True
    >>> bool(shipment_out.systemlogics_modula_completed)
    True

Create Shipment Internal::

    >>> ShipmentInternal = Model.get('stock.shipment.internal')
    >>> shipment_internal = ShipmentInternal()
    >>> shipment_internal.planned_date = today
    >>> shipment_internal.warehouse = warehouse_loc
    >>> shipment_internal.from_location = lost_found_loc
    >>> shipment_internal.to_location = storage_loc
    >>> shipment_internal.company = company
    >>> move = StockMove()
    >>> shipment_internal.moves.append(move)
    >>> move.product = product
    >>> move.uom = unit
    >>> move.quantity = 1
    >>> move.from_location = lost_found_loc
    >>> move.to_location = storage_loc
    >>> move.company = company
    >>> move.unit_price = Decimal('1')
    >>> move.currency = company.currency
    >>> shipment_internal.save()
    >>> shipment_internal.click('wait')
    >>> shipment_internal.click('assign_try')
    True
    >>> shipment_internal.click('done')
    >>> bool(shipment_internal.systemlogics_modula)
    True
