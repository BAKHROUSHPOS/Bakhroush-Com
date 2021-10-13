from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    branch_id = fields.Many2many('company.branch', string="Branch", required=True)
    # allowed_user_ids = fields.Many2many('res.users', compute='_compute_allowed_users',store=True)

    @api.onchange('branch_id')
    def onchange_branch_ids(self):
        return {'domain': {
            'branch_id': [('id', 'in', self.env.user.branch_ids.ids)]}}

    @api.depends('branch_id','name')
    def _compute_allowed_users(self):
        users = self.env['res.users'].search(
                    [('branch_ids', 'in', self.branch_id.ids)])
        self.allowed_user_ids = users