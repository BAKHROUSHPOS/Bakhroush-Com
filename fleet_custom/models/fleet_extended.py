# See LICENSE file for full copyright and licensing details.
"""Multi Image model."""

import logging
from datetime import date, datetime

from odoo import _, api, fields, models
from odoo import tools
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

class FleetOperations(models.Model):
    _inherit = 'fleet.vehicle'

    serial_number = fields.Char(string='Serial Number')
    vehicle_type = fields.Many2one('fleet.vehicle.type',string='Vehicle Type')
    registration_type = fields.Many2one('fleet.registration.type',string='Registration Type')
    insurance_expiry = fields.Date('Insurance Expiry')
    registration_expiry = fields.Date('Registration Expiry')
    code = fields.Char('Code')
    map_link = fields.Char('Map Link')
    employee_driver = fields.Many2one('hr.employee','Driver')

    @api.onchange('employee_driver')
    def _onchange_employee_driver(self):
        if self.employee_driver and not self.employee_driver.address_home_id:
            raise ValidationError('Please add Address in Employee form to link with partner account.')
        self.driver_id = self.employee_driver.address_home_id.id

class VehicleType(models.Model):
    _name = 'fleet.vehicle.type'

    name = fields.Char('Type')
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('fleet_vehicle_type_name_unique', 'unique(name)', 'Error! Name Already Exist!')
    ]

class RegistrationType(models.Model):
    _name = 'fleet.registration.type'

    name = fields.Char('Type')
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('fleet_registration_type_name_unique', 'unique(name)', 'Error! Name Already Exist!')
    ]


class AccountAsset(models.Model):
    _inherit = 'account.asset'

    model_date = fields.Char('Model Date')
    branch_id = fields.Many2one('company.branch', string='Branch',
                                default=lambda self: self.env.user.branch_id)
    code = fields.Char('Code')
    market_value = fields.Float('Market Value')
    purchased_date = fields.Date('Purchased Date')
    purchased_value = fields.Date('Purchased Value')

class CompanyBranch(models.Model):
    _inherit = 'company.branch'

    code = fields.Char('Code')
    map_link = fields.Char('Map Link')

class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    branch_id = fields.Many2one('company.branch', 'Branch')