# See LICENSE file for full copyright and licensing details.
"""Multi Image model."""

import logging
from datetime import date, datetime

from odoo import _, api, fields, models
from odoo import tools
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

class CompanyBranch(models.Model):
    _inherit = 'company.branch'

    code = fields.Char('Code')
    map_link = fields.Char('Map Link')
