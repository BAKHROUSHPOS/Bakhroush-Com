# -*- coding: utf-8 -*-

from odoo import models, api, fields, _



class ReportAccountPartnerLedger(models.AbstractModel):
    _inherit = "account.partner.ledger"
    
    
    def get_pdf(self, options, minimal_layout=True):
        options['az_print_mode'] = True
        return super().get_pdf(options, True)
    
    def get_html(self, options, line_id=None, additional_context=None):
        if self.env.context.get('print_mode'):
            if additional_context:
                additional_context.update({'az_print_mode': True})
            else:
                additional_context = {'az_print_mode': True}

        return super().get_html(options, line_id, additional_context)