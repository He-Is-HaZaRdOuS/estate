from odoo import api, fields, models, exceptions

class EstatePropertyWizard(models.TransientModel):
    _name = "estate.property.wizard"
    _description = "Send Notifications to Property Followers"

    property_ids = fields.Many2many("estate.property", string="Properties")
    message_subject = fields.Char()
    message_body = fields.Html()

    @api.model
    def default_get(self, fields_list):
        defaults_dict = super().default_get(fields_list)
        property_ids = self.env.context.get("active_ids", [])
        defaults_dict["property_ids"] = [(6, 0, property_ids)]
        return defaults_dict

    def action_send_notice(self):
        self.ensure_one()
        if not self.property_ids:
            raise exceptions.UserError("No Properties were selected.")
        if not self.message_body:
            raise exceptions.UserError("A message body is required")

        for prop in self.property_ids:
            prop.message_post(
                body=self.message_body,
                subject=self.message_subject,
                message_type='comment',
            )
        return True
