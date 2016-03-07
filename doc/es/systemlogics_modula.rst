===================
Systemlogics Modula
===================

Systemlogics Modula permite la integración/comunicación de los datos del ERP con el SGA.

.. inheritref:: systemlogics_modula/systemlogics_modula:section:productos

---------
Productos
---------

Para exportar productos a Systemlogics Modula:

* Al crear un producto nuevo, se genera un fichero
* Al modificar un producto, se genera un fichero
* Mediante la acción "Exportar productos a Systemlogics", se genera un fichero por cada producto seleccionado.

.. inheritref:: systemlogics_modula/systemlogics_modula:section:albaranes_de_cliente

--------------------
Albaranes de cliente
--------------------

Se genera un fichero para Systemlogics cada vez que un albarán pase por el estado "Reserva".

.. important:: se genera el fichero cada vez que el albarán pasa por el estado "Reserva", por tanto,
               si el albarán se decide passar de empaquetado a reserva y volver a procesarlo,
               se generará un nuevo fichero con las modificaciones realizadas.

.. inheritref:: systemlogics_modula/systemlogics_modula:section:albaranes_de_proveedor

----------------------
Albaranes de proveedor
----------------------

Se genera un fichero para Systemlogics cada vez que un albarán se accione el botón "Modula" para que genere el fichero.

.. inheritref:: systemlogics_modula/systemlogics_modula:section:configuracion

-------------
Configuración
-------------

A |menu_systemlogics_modula_configuration| configuraremos los directorios de importación/exportación de los ficheros

Estos directorios deberán tener permisos de escritura y serán los directorios que Systemlogics tendrá montados.

En la configuración seleccionaremos el tipo de fichero a generar, que por defecto, es XML.

.. |menu_systemlogics_modula_configuration| tryref:: systemlogics_modula.menu_systemlogics_modula_configuration/complete_name
