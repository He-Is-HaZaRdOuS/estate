from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare
import logging
_logger = logging.getLogger(__name__)


def _check_offer_exists(record):
    return bool(record.offer_ids.filtered(lambda offer: offer.state == "accepted"))


def _check_buyer_exists(record):
    return bool(record.buyer)


def _check_sold(record):
    return record.state == 'sold'


def _check_cancelled(record):
    return record.state == 'cancelled'


class EstateProperty(models.Model):
    _name = 'estate.property'
    _inherit = ['mail.thread']
    _description = 'Real Estate Property'
    _order = 'id desc'

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
        selection=[('new', 'NEW'), ('offer_received', 'OFFER RECEIVED'), ('offer_accepted', 'OFFER ACCEPTED'),
                   ('sold', 'SOLD'), ('cancelled', 'CANCELLED')],
        copy=False, default='new', required=True
    )
    active = fields.Boolean(default=True)
    property_type_id = fields.Many2one('estate.property.type', string="Type")
    seller = fields.Many2one('res.users', string="Salesman", index=True, default=lambda self: self.env.user)
    buyer = fields.Many2one('res.partner', string="Buyer", index=True, copy=False)
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company)
    tag_ids = fields.Many2many('estate.property.tag', string="Tag")
    offer_ids = fields.One2many('estate.property.offer', 'property_id', string="Offers")
    best_offer = fields.Float(compute="_compute_best_offer")

    _sql_constraints = [
        ('check_expected_price', 'CHECK(expected_price > 0)', 'The property expected price must be positive'),
        ('check_selling_price', 'CHECK(selling_price >= 0)', 'The property selling price must be positive or zero'),
    ]

    @api.model
    def cron_send_reminder(self):
        _logger.debug('Cron job executed (Estate Property Reminder)')

        # Get today's date and the deadline threshold (2 days from now)
        today = fields.Date.context_today(self)
        deadline_threshold = fields.Date.add(today, days=2)

        # Search for properties with deadlines within the range
        properties = self.search([
            ('state', '=', 'offer_received'),
            ('offer_ids', '!=', False),
            ('offer_ids.date_deadline', '<=', deadline_threshold),
            ('offer_ids.date_deadline', '>=', today),
            ('offer_ids.state', 'not in', ['rejected', 'accepted'])
        ])

        if not properties:
            _logger.debug('No properties found with upcoming deadlines.')
            return

        # Fetch the email template
        template_id = self.env.ref('real_estate.email_template_property_reminder', raise_if_not_found=False)

        if not template_id:
            _logger.warning("Email template for reminders not found.")
            return

        # Send email for each property
        for prop in properties:
            template = self.env['mail.template'].browse(template_id.id)
            template.send_mail(prop.id, force_send=True)
            _logger.debug('Reminder sent for property: %s', prop.name)

        _logger.debug('Sent reminders for %d properties', len(properties))

    @api.ondelete(at_uninstall=False)
    def _block_unlink(self):
        if self.state not in ['new', 'cancelled']:
            raise UserError("You cannot delete a property that is not new or cancelled")
            return False

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
            if record.offer_ids and float_compare(record.expected_price * 0.9, record.selling_price,
                                                  precision_digits=2) > 0:
                raise ValidationError("The selling price cannot be lower than 90% of the expected price")

    def action_sell(self):
        for record in self:
            if _check_cancelled(record):
                raise UserError("Cannot sell a cancelled property")
            if not _check_buyer_exists(record):
                raise UserError("Cannot sell a property without having a buyer")
            if _check_sold(record):
                raise UserError("Property is already sold!")
            if not _check_offer_exists(record):
                raise UserError("Cannot sell a property without having an accepted offer")

            record.state = "sold"
        return True

    def action_cancel(self):
        for record in self:
            if record.state == "sold":
                raise UserError("Cannot cancel a sold property")
                return False
            if record.state == "cancelled":
                raise UserError("Property is already cancelled!")
                return False
            record.state = "cancelled"
            return True

    def reset_state(self):
        for record in self:
            if not record.offer_ids:
                record.set_state("new")

    def set_state(self, state):
        for record in self:
            record.state = state
