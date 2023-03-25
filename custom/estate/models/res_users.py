from odoo import api, fields, models

class Users(models.Model):
    _inherit = 'res.users'
    property_ids = fields.One2many("estate.property", "salesman_id", string="Объекты",
                                   domain=[('state', 'in', ('new', 'offer_received', 'offer_accepted'))])
