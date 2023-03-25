from dateutil import relativedelta
from odoo import api, fields, models

class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Estate Property Type"
    _order = "sequence asc, name asc"


    _sql_constraints = [
        ('check_unique_estate_property_type', 'unique(name)', 'Имя уже существует')
    ]

    name = fields.Char('Наименование', required=True)
    property_ids = fields.One2many("estate.property", "property_type_id", "Properties", readonly=True)
    offer_ids = fields.One2many("estate.property.offer", "property_type_id", "Offers", readonly=True)
    offer_count = fields.Integer("Кол-во предложений", compute="_compute_offer_count")
    sequence = fields.Integer("Порядок", default = 1)

    @api.depends("offer_ids")
    def _compute_offer_count(self):
        for record in self:
            if record.offer_ids:
                record.offer_count = len(record.offer_ids)
            else:
                record.offer_count = 0