# See LICENSE file for full copyright and licensing details.
"""Multi Image model."""

import logging
from datetime import date, datetime

from odoo import _, api, fields, models
from odoo import tools
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

class AccountAsset(models.Model):
    _inherit = 'account.asset'

    model_date = fields.Char('Model Date')
    branch_id = fields.Many2one('company.branch', string='Branch',
                                default=lambda self: self.env.user.branch_id)
    code = fields.Char('Code')
    market_value = fields.Float('Market Value')
    purchased_date = fields.Date('Purchased Date')
    purchased_value = fields.Float('Purchased Value')

