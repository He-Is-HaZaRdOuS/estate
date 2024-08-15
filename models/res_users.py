from odoo import fields, models


class UsersInherited(models.Model):
    _inherit = "res.users"

    property_ids = fields.One2many("estate.property", "seller", string="Properties", domain=['|', ('state', '=', 'new'), ('state', '=', 'offer_received')])
