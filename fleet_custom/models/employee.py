# -*- coding: utf-8 -*-

import logging
from datetime import date, datetime

from odoo import _, api, fields, models
from odoo import tools
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

class Employee(models.Model):
    _inherit = 'hr.employee'

    branch_id = fields.Many2one('company.branch', 'Branch')
