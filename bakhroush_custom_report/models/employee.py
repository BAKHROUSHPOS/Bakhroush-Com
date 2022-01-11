# -*- coding: utf-8 -*-

from odoo import fields, models , api, _

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.model
    def create(self, vals):
        employee = super(HrEmployee, self).create(vals)
        partner = self.env['res.partner'].create({'name': employee.name,'is_employee':True})
        employee['address_home_id'] = partner
        return employee