from dateutil import relativedelta
from datetime import date
from odoo import api, fields, models
from odoo.exceptions import UserError

class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = 'Предложения'
    _order = "price desc"

    price = fields.Float("Цена")
    status = fields.Selection(
        string="Статус",
        selection=[('Accepted', 'ОК'), ('Refused', 'отказ')],
        copy=False
    )
    partner_id = fields.Many2one("res.partner", string="Партнер", required=True)
    property_id = fields.Many2one("estate.property", string="Недвижимость", required=True)
    validity = fields.Integer("Срок действия", default=7)
    date_deadline = fields.Date("Deadline", compute="_compute_date_deadline", inverse="_inverse_date_deadline")
    property_type_id = fields.Many2one("estate.property.type", string="Тип", related="property_id.property_type_id", store=True)

    _sql_constraints = [
        ('check_offer_price', 'CHECK(price >  0)', 'Цена должна быть > 0')
    ]

    def currd(self, record):
        if record.create_date:
            dt = record.create_date.date()
        else:
            dt = date.today()
        return dt

    @api.depends("create_date", "validity")
    def _compute_date_deadline(self):
        for record in self:
            record.date_deadline = self.currd(record) + relativedelta.relativedelta(days=record.validity)

    def _inverse_date_deadline(self):
        for record in self:
            if record.date_deadline:
                record.validity = (record.date_deadline - self.currd(record)).days

    def action_accept(self):
        self.ensure_one()
        has_accepted = self.property_id.has_accepted_offers()
        if has_accepted:
            raise UserError('Больше одного низзя!!!')
        else:
            self.status = 'Accepted'
            self.property_id.buyer_id = self.partner_id
            self.property_id.selling_price = self.price

    def action_refuse(self):
        self.ensure_one()
        self.status = 'Refused'
        if not self.property_id.has_accepted_offers():
            self.property_id.buyer_id = None
            self.property_id.selling_price = None

    @api.model
    def create(self, vals_list):
        pid = vals_list['property_id']
        price = vals_list['price']
        if not pid:
            raise UserError('Не задан property_id для offer')
        if (not price) or (price<=0):
            raise UserError('Цена не задана или не положительная')
        prp = self.env['estate.property'].browse(pid)
        if (prp.offer_ids) and (price<max(prp.offer_ids.mapped("price"))):
            raise UserError('Цена меньше ранее предложенной')
        if prp.state=='new':
            prp.state = 'offer_received'
        return super().create(vals_list)



