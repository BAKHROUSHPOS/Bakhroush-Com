from odoo import models, fields

class CreditLimitWizard(models.TransientModel):
    _name = "credit.limit.wizard"
    _description = "Credit Limit Validation Wizard"
    
    message = fields.Char()
    can_validate = fields.Boolean("Can Validate Transfer", compute='_compute_can_validate',
                                  help="Can Validate a transfer even if the customer has no Credit in case the user has the access right for it.")
    picking_id = fields.Many2one("stock.picking", string="Transfer", help="Transfer that been Validated")

    def _compute_can_validate(self):
        for record in self:
            can_validate = False
            if self.env.user.has_group('bakhroush_custom_report.group_allow_validate_transer') \
                or self.env.user.has_group('account.group_account_manager'):
                can_validate = True
            record.can_validate = can_validate
    
    
    def validate_transfer(self):
        return self.picking_id.with_context(bypass_credit_validation=True).button_validate()