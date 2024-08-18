from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Real Estate Property Offer"
    _order = "price desc"

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
    property_type_id = fields.Many2one(related="property_id.property_type_id", string="Property Type", store=True)

    _sql_constraints = [
        ('check_price', 'CHECK(price > 0)', 'The offer price must be positive'),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        # Call super constructor in batch
        offers = super(EstatePropertyOffer, self).create(vals_list)

        # Update property status for each offer
        for offer in offers:
            if offer.property_id:
                max_offer = 0 # Keep track of highest offer for its respective property
                for prop_offer in offer.property_id.offer_ids:
                    if prop_offer.price > max_offer:
                        max_offer = prop_offer.price
                if offer.price < max_offer:
                    raise UserError("Cannot create an offer with a lower amount than existing offer")
                    return False
                offer.property_id.state = 'offer_received'

        # Return the created offers
        return offers

    @api.model
    def unlink(self):
        properties = self.mapped("property_id")
        # Call super deconstructor
        result = super(EstatePropertyOffer, self).unlink()

        # Update property state
        properties.reset_status()
        return result

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
            if record.property_id.state == "offer_accepted":
                raise UserError("An offer has already been accepted")
                return False

            record.status = "accepted"
            record.property_id.buyer = record.partner_id
            record.property_id.selling_price = record.price
            record.property_id.state = "offer_accepted"
            print(record.property_id.state)
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
