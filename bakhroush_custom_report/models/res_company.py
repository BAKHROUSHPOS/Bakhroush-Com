# -*- coding: utf-8 -*-
from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    header_img = fields.Binary("Header Image")
    footer_img = fields.Binary("Footer Image")
