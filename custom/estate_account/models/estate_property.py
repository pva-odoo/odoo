from odoo import models, Command


class EstateProperty(models.Model):
    _inherit = 'estate.property'

    def action_property_sold(self):
        self.ensure_one()
        print("action_property_sold inherited")
        super().action_property_sold()

        invoice_vals = {
            'partner_id': self.buyer_id.id,
            'move_type': 'out_invoice',
            'invoice_line_ids':
                [
                    Command.create({
                        'name': '6%',
                        'quantity': 1,
                        'price_unit': self.selling_price*0.06
                    }),
                    Command.create({
                        'name': 'Adimistrative fee',
                        'quantity': 1,
                        'price_unit': 100
                    })
                ]
        }

        for record in self:
            account_move = self.env['account.move'].create(invoice_vals)
