from dateutil import relativedelta
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_utils

class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Real Estate Property"
    _order = "id desc"

    name = fields.Char('Наименование', required=True)
    description = fields.Text("Описание")
    property_type_id = fields.Many2one("estate.property.type", string="Тип недвижимости")
    postcode = fields.Char("Почтовый индекс")
    date_availability = fields.Date("Cрок доступности", default=lambda self: fields.Date.today() + relativedelta.relativedelta(months=3)) # '
    expected_price = fields.Float("Ожидаемая цена", required=True)
    selling_price = fields.Float("Цена продажи")
    bedrooms = fields.Integer("Кол-во спален", default=2)
    living_area = fields.Integer("Жилая площадь")
    facades = fields.Integer("Фасады", default=1)
    garage = fields.Boolean("Гараж")
    garden = fields.Boolean("Сад")
    garden_area = fields.Integer("Площадь сада")
    garden_orientation = fields.Selection(
        string="Ориентация сада",
        selection=[('north', 'Север'), ('south', 'Юг'), ('east', 'Восток'), ('west', 'Запад')]
    )
    state = fields.Selection(
        string="Состояние",
        selection=[('new', 'New'), ('offer_received', 'Offer received'), ('offer_accepted', 'Offer accepted'), ('sold', 'Sold'), ('rejected', 'Rejected')],
        default='new')
    salesman_id = fields.Many2one('res.users', string='Продаван', index=True, tracking=True, default=lambda self: self.env.user)
    buyer_id = fields.Many2one('res.partner', string='Покупец')
    property_tag_ids = fields.Many2many("estate.property.tag", string="Тэги")
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Предложения")
    active = fields.Boolean("Active", default=True)
    total_area = fields.Integer("Общая площадь", compute="_compute_total_area")
    best_price = fields.Float("Лучшая цена", compute="_compute_best_price")

    _sql_constraints = [
        ('check_expected_price', 'CHECK(expected_price > 0 or expected_price is null)', 'Ожидаемая цена должна быть > 0'),
        ('check_selling_price', 'CHECK(selling_price >= 0 or selling_price is null)', 'Цена продажи должна быть >= 0')
    ]

    @api.onchange("garden")
    def _onchange_garden(self):
        if (self.garden):
            self.garden_area = 10
            self.garden_orientation = 'west'
        else:
            self.garden_area = 0
            self.garden_orientation = None

    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.garden_area + record.living_area

    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for record in self:
            if record.offer_ids:
                record.best_price = max(record.offer_ids.mapped("price"))
            else:
                record.best_price = None

    @api.constrains('state', 'expected_price', 'selling_price')
    def _check_price_90(self):
        for record in self:
            if record.state== 'sold' and record.selling_price <= record.expected_price * 0.9:
                raise ValidationError("selling_price <= expected_price * 0.9")

    def action_property_sold(self):
        for record in self:
            if (record.state=='rejected'):
                raise UserError('Невозможно перевести отмененный заказ в состояние Продан')
            record.state = 'sold'

    def action_property_cancelled(self):
        for record in self:
            if (record.state=='sold'):
                raise UserError('Невозможно перевести проданный заказ в состояние Отменен')
            record.state = 'rejected'

    def has_accepted_offers(self):
        self.ensure_one()
        has_accepted = False
        for offer in self.offer_ids:
            if offer.status == 'Accepted':
                has_accepted = True
        return has_accepted

    @api.ondelete(at_uninstall=False)
    def _unlink_except_used_as_rule_base(self):
        for record in self:
            if (not (record.state=='new' or record.state=='rejected')):
                raise UserError('Заказ в данном состоянии не может быть удален')



