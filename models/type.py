from odoo import fields, models


class EstatePropertyType(models.Model):
    _name = 'estate.property.type'
    _description = 'Real Estate Property Type'
    _order = 'name'

    name = fields.Char(string='Name', required=True)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'Type name already exists!'),
    ]
