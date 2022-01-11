# -*- coding: utf-8 -*-

from odoo import api, fields, models, _



class InventoryLine(models.Model):
    _inherit = "stock.inventory.line"

    def _check_no_duplicate_line(self):
        return []