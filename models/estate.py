from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare


class EstateProperty(models.Model):
    _name = 'estate.property'
    _description = 'Real Estate Property'
    _order = 'id'

    name = fields.Char(string='Title', required=True)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(copy=False, default=fields.Date.add(fields.Date.today(), days=30))
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(
        string='Garden orientation',
        selection=[('north', 'North'), ('south', 'South'), ('east', 'East'), ('west', 'West')],
        help='Garden orientation'
    )
    total_area = fields.Integer(compute="_compute_total_area")
    state = fields.Selection(
        string='Status',
        selection=[('new', 'New'), ('offer_received', 'Offer received'), ('offer_accepted', 'Offer Accepted'), ('sold', 'Sold'), ('cancelled', 'Cancelled')],
        copy=False, default='new', required=True
    )
    active = fields.Boolean(default=True)
    property_type_id = fields.Many2one('estate.property.type', string="Type")
    seller = fields.Many2one('res.users', string="Salesman", index=True, default=lambda self: self.env.user)
    buyer = fields.Many2one('res.partner', string="Buyer", index=True, copy=False)
    tag_ids = fields.Many2many('estate.property.tag', string="Tag")
    offer_ids = fields.One2many('estate.property.offer', 'property_id', string="Offers")
    best_offer = fields.Float(compute="_compute_best_offer")

    _sql_constraints = [
        ('check_expected_price', 'CHECK(expected_price > 0)', 'The property expected price must be positive'),
        ('check_selling_price', 'CHECK(selling_price >= 0)', 'The property selling price must be positive or zero'),
    ]

    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends("offer_ids.price")
    def _compute_best_offer(self):
        for record in self:
            prices = record.mapped('offer_ids.price')
            if prices:
                record.best_offer = max(prices)
            else:
                record.best_offer = 0

    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden is True:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = False

    @api.onchange("selling_price", "expected_price")
    @api.constrains("selling_price")
    def _check_selling_price(self):
        for record in self:
            if record.offer_ids and float_compare(record.expected_price * 0.9, record.selling_price, precision_digits=2) > 0:
                raise ValidationError("The selling price cannot be lower than 90% of the expected price")

    # WIP
    # @api.depends("offer_ids")
    # def _compute_offers(self):
    #     if self.offer_ids:
    #         has_pending_offer = False
    #         for offer in self.offer_ids:
    #             if offer.status not in ['rejected', 'accepted']:
    #                 has_pending_offer = True
    #                 break
    #         else:
    #             self.state = "new"

    #         if has_pending_offer:
    #             self.state = "offer_received"
    #     self.state = "new"

    def action_sell(self):
        for record in self:
            if record.state == "cancelled":
                raise UserError("Cannot sell a cancelled property")
                return False
            if not record.buyer:
                raise UserError("Cannot sell a property without having a buyer")
                return False
            if record.state == "sold":
                raise UserError("Property is already sold!")
                return False
            record.state = "sold"
            return True

    def action_cancel(self):
        for record in self:
            print(record.state)
            if record.state == "sold":
                raise UserError("Cannot cancel a sold property")
                return False
            if record.state == "cancelled":
                raise UserError("Property is already cancelled!")
                return False
            record.state = "cancelled"
            return True

    def reset_status(self):
        for record in self:
            if not record.offer_ids:
                record.state = "new"
