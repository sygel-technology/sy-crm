.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
	:target: http://www.gnu.org/licenses/agpl
	:alt: License: AGPL-3

==============
CRM Autoassign
==============

This module allows to automatically assign opportunities to team members.


Installation
============

To install this module, you need to:

#. Only install

IMPORTANT NOTE: 

Installing this module hides all Odoo's default options for Leads autoassignment.


Configuration
=============

To configure this module, you need to:

#. Create a stage that allows automatic assignment of opportunities by checking the option 'Allow autoassign'.

#. Allow automatic assignment of team members by selecting the option 'Autoassign Opportunities'. This option can only be selected by members who are not teamleders.

#. Configure the number of days and the number of opportunities that can be assigned to each member.

#. Configure the domain of opportunities that can be assigned to a team member.

#. Optionally, from the sales team you can select a stage to which the opportunity will be transferred after being autoassigned.


Usage
=====

To use this module, you need to:

* The assignment of opportunities will be done automatically every 30 minutes.

* It can be done manually per sales team by clicking on 'Assign opportunities' from the sales team view.


ROADMAP
=======

Some of the tests are disabled because auto_commit cannot be tested in test mode. 
In future releases we will consider improving the tests so that all cases can be covered.


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
