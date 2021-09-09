from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    branch_id = fields.Many2many('company.branch', string="Branch", required=True)

    @api.onchange('branch_id')
    def onchange_branch_ids(self):
        return {'domain': {
            'branch_id': [('id', 'in', self.env.user.branch_ids.ids)]}}