from odoo import api, fields, models
from odoo.exceptions import UserError


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Real Estate Property Offer"
    _order = "price"

    price = fields.Float()
    status = fields.Selection(
        string="Status",
        selection=[('accepted', 'Accepted'), ('rejected', 'Rejected')],
        copy=False, default=False
    )
    validity = fields.Integer(string="Validity (in days)", default=7)
    date_deadline = fields.Date(string="Deadline", compute="_compute_date_deadline", inverse="_inverse_date_deadline")
    partner_id = fields.Many2one('res.partner', string="Buyer", required=True)
    property_id = fields.Many2one('estate.property', string="Property", required=True)

    @api.depends("validity")
    def _compute_date_deadline(self):
        for record in self:
            if record.create_date is False:
                record.date_deadline = fields.Date.add(fields.Date.today(), days=record.validity)
            else:
                record.date_deadline = fields.Date.add(record.create_date, days=record.validity)

    def _inverse_date_deadline(self):
        for record in self:
            record.validity = (record.date_deadline - fields.Date.today()).days

    def action_accept(self):
        for record in self:
            if record.status == "rejected":
                raise UserError("Cannot accept a rejected offer")
                return False
            if record.property_id.state == "accepted":
                raise UserError("An offer has already been accepted")
                return False
            record.status = "accepted"
            record.property_id.buyer = record.partner_id
            record.property_id.selling_price = record.price
            return True


    def action_reject(self):
        for record in self:
            if record.status == "accepted":
                raise UserError("Cannot reject an accepted offer")
                return False
            if record.status == "rejected":
                raise UserError("Offer has already been rejected")
                return False
            record.status = "rejected"
            return True
