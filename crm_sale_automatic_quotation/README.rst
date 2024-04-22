.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
	:target: http://www.gnu.org/licenses/agpl
	:alt: License: AGPL-3

============================
CRM Sale Automatic Quotation
============================

This module allows you to generate quotations with quotation templates from an opportunity.
It also adds a wizard to massively do it from list view.

Installation
============

To install this module, you need to:

#. Only install


Configuration
=============

To configure this module, you need to:

#. Go to Sales -> Configuration -> Settings
#. Activate the 'Quotation Templates' option and go to Quotation templates to create or edit one.
#. Activate the 'CRM Automatic Quotation' field and edit a domain for oprtunities if you want. You can also exclude the template from the wizard

To configure the default mail template in the wizard, you need to:

#. Activate the developer mode
#. Go to Settings -> Technical -> System Parameters
#. Search crm_sale_automatic_quotation.crm_sale_automatic_quotation_wizard_email key
#. Introduce its value by the external identifier of your desired mail template


Usage
=====

To use this module, you need to:

#. Go to a CRM module opportunity.
#. Click on 'Automatic Quotation' button.
#. All quotations that satisfy the template domain will be created. 


To use the wizard, you need to:

#. Go to a the CRM opportunity list view
#. Select the opportunities you want to create quotations for
#. Click the "action" button and then the "Create automatic quotations" button
#. Review and/or modify the configuration Parameters
#. Click the "Create Quotations" button
#. If an error was detected on a opportunity, it will be shown and you will have the chance to correct it and click again in the "Create Quotations" button

Bug Tracker
===========

Bugs and errors are managed in `issues of GitHub <https://github.com/sygel-technology/sy-crm/issues>`_.
In case of problems, please check if your problem has already been
reported. If you are the first to discover it, help us solving it by indicating
a detailed description `here <https://github.com/sygel-technology/sy-crm/issues/new>`_.

Do not contact contributors directly about support or help with technical issues.


Credits
=======

Authors
~~~~~~~

* Sygel, Odoo Community Association (OCA)

Contributors
~~~~~~~~~~~~

* Ángel García de la Chica Herrera <angel.garcia@sygel.es>

Maintainer
~~~~~~~~~~

This module is maintained by Sygel.

.. image:: https://www.sygel.es/logo.png
   :alt: Sygel
   :target: https://www.sygel.es

This module is part of the `Sygel/sy-crm <https://github.com/sygel-technology/sy-crm>`_.

To contribute to this module, please visit https://github.com/sygel-technology.
