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