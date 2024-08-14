from odoo import fields, models


class EstatePropertyTag(models.Model):
    _name = 'estate.property.tag'
    _description = 'Real Estate Property Tag'
    _order = 'name'

    name = fields.Char(string='Name', required=True)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'Tag name already exists!'),
    ]
