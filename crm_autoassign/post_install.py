# Copyright 2023 Ángel García de la Chica <angel.garcia@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import SUPERUSER_ID, api


def post_init_hook(cr, registry):
    """ After installing the module the following actions will be done:
        1.  Set the odoo base variable 'assignment_optout' to True to disable 
        all Odoo auto-assignment functions.
        2.  Set the assignment date to the conversion date between initiative
        and opportunity or the creation date if the conversion date does not 
        exist.If this is not done, the assignment date of all opportunities 
        created before installing the module will be the installation date. 
        This is because the assignment date field is a computed field.  
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    env["crm.team.member"].search([]).write({
        'assignment_optout': True
    })
    for lead in env["crm.lead"].search([('user_id', '!=', None)]):
        lead.assignment_date = lead.date_conversion if lead.date_conversion \
            else lead.create_date
    return
