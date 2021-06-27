# -*- coding: utf-8 -*-

import logging
from datetime import date, datetime

from odoo import _, api, fields, models
from odoo import tools
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    building_no = fields.Char('Building No')
    district = fields.Char('District')
    additional_no = fields.Char('Additional No')
