from odoo import api, fields, models


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
        selection=[('new', 'New'), ('offer_received', 'Offer Received'), ('offer_accepted', 'Offer Accepted'), ('sold', 'Sold'), ('canceled', 'Canceled')],
        copy=False, default='new', required=True
    )
    active = fields.Boolean(default=True)
    property_type_id = fields.Many2one('estate.property.type', string="Type")
    seller = fields.Many2one('res.users', string="Salesman", index=True, default=lambda self: self.env.user)
    buyer = fields.Many2one('res.partner', string="Buyer", index=True, copy=False)
    tag_ids = fields.Many2many('estate.property.tag', string="Tag")
    offer_ids = fields.One2many('estate.property.offer', 'property_id', string="Offers")
    best_offer = fields.Float(compute="_compute_best_offer")

    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends("offer_ids.price")
    def _compute_best_offer(self):
        for record in self:
            record.best_offer = max(record.mapped('offer_ids.price'))
