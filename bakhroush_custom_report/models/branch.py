# -*- coding: utf-8 -*-

from odoo import fields, models , api, _

class Branch(models.Model):
    _inherit = 'company.branch'

    allowed_user_ids = fields.Many2many('res.users', compute='_compute_allowed_users',store=True)

    @api.depends('name')
    def _compute_allowed_users(self):
        users = self.env['res.users'].search(
            [('branch_ids', 'in', self.id)])
        print(users)
        self.allowed_user_ids = users