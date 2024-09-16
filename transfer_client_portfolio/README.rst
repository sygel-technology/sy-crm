.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
	:target: http://www.gnu.org/licenses/agpl
	:alt: License: AGPL-3

=========================
Transfer Client Portfolio
=========================

This module allows to transfer contacts and opportunities from one user to another.

Installation
============

To install this module, you need to:

#. Only install


Configuration
=============

To configure the stages of the opportunities that can be transferred, you need to:

#. Go to CRM -> Configuration -> Stages
#. Enter the stages that you want to be transferable between users and check the box "Allow transfer at this stage".


Usage
=====

To use this module, you need to:

#. Open the CRM application and then 
#. Go to Sales and click on 'Transfer Customer Portfolio'.
#. In the wizard select if you want to update the salesperson on the contacts, the Current Salesperson' and the new Salesperson.
#. Click on review and select the contacts/opportunities you want to transfer and click on transfer.

Once they have been transferred you can view the record in the 'Transfer Clients Portfolios' Reports section.
In addition, you can see the previous business in the client's file and in the opportunity.

To use it with server action, you need to:

#. Open the CRM application and then
#. Select the desired opportunities in list mode and click on "Action" button and select "Transfer selected opportunities".
#. In the wizard select if you want to update the salesperson on the contacts too and the new Salesperson.
#. Select the contacts/opportunities you want to transfer and click on transfer.

One they have been transferred you can view the Record and see the previous salesperson in the 'Transfer Clients Portfolios'.



Bug Tracker
===========

Bugs and errors are managed in `issues of GitHub <https://github.com/sygel/REPOSITORY/issues>`_.
In case of problems, please check if your problem has already been
reported. If you are the first to discover it, help us solving it by indicating
a detailed description `here <https://github.com/sygel/REPOSITORY/issues/new>`_.

Do not contact contributors directly about support or help with technical issues.


Credits
=======

Authors
~~~~~~~

* Sygel, Odoo Community Association (OCA)


Contributors
~~~~~~~~~~~~

* Ángel García de la Chica Herrera <angel.garcia@sygel.es>
* Alberto Martínez Rodríguez <alberto.martinez@sygel.es>



Maintainer
~~~~~~~~~~

This module is maintained by Sygel.

.. image:: https://www.sygel.es/logo.png
   :alt: Sygel
   :target: https://www.sygel.es

This module is part of the `Sygel/REPOSITORY <https://github.com/sygel/repository>`_.

To contribute to this module, please visit https://github.com/sygel.
