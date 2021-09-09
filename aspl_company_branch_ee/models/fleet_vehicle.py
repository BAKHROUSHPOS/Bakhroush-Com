# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

from odoo import models, fields,api


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    branch_id = fields.Many2one('company.branch', string="Branch",
                                default=lambda self: self.env.user.branch_id)

    @api.onchange('branch_id')
    def onchange_branch_ids(self):
        return {'domain': {
            'branch_id': [('company_id', '=', self.company_id.id), ('id', 'in', self.env.user.branch_ids.ids)]}}


class FleetVehicleLogContract(models.Model):
    _inherit = 'fleet.vehicle.log.contract'

    branch_id = fields.Many2one('company.branch', string="Branch",
                                default=lambda self: self.env.user.branch_id)

    @api.onchange('branch_id')
    def onchange_branch_ids(self):
        return {'domain': {
            'branch_id': [('id', 'in', self.env.user.branch_ids.ids)]}}

class FleetVehicleLogServices(models.Model):
    _inherit = 'fleet.vehicle.log.services'

    branch_id = fields.Many2one('company.branch', string="Branch",
                                default=lambda self: self.env.user.branch_id)

    @api.onchange('branch_id')
    def onchange_branch_ids(self):
        return {'domain': {
            'branch_id': [('id', 'in', self.env.user.branch_ids.ids)]}}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
