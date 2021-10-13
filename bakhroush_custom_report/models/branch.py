# -*- coding: utf-8 -*-

from odoo import fields, models , api, _

class Branch(models.Model):
    _inherit = 'company.branch'

    allowed_user_ids = fields.Many2many('res.users',string='Allowed Users')

class Users(models.Model):
    _inherit = 'res.users'

    @api.onchange('branch_id','branch_ids')
    def _compute_allowed_users(self):
        for branch in self.env['company.branch'].search([]):
            users = self.env['res.users'].search(
                [('branch_ids', 'in', branch.id)])
            print(users)
            branch.allowed_user_ids = users