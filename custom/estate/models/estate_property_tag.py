from odoo import fields, models

class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Тэг"
    _order = "name asc"

    _sql_constraints = [
        ('check_unique_estate_tag', 'unique(name)', 'Имя уже существует')
    ]

    name = fields.Char("Наименование", required=True)
    color = fields.Integer("Цвет")
