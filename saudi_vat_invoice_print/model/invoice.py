# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
from num2words import num2words


class AccountMove(models.Model):
    _inherit = 'account.move'

    amount_text = fields.Char(string='Amount In Words', compute='amount_to_words')
    amount_in_ar = fields.Char(string='Amount In Words', compute='amount_to_words')
    attention = fields.Many2one('res.partner', 'Attention')
    approved_by = fields.Many2one('res.partner', 'Approved By')
    vat_text = fields.Char('Vat Text',compute='_get_vat_text')
    vat_arabic_text = fields.Char('Vat Text(Arabic)',compute='_get_vat_text')

    @api.depends('invoice_line_ids','amount_total')
    def _get_vat_text(self):
        vat = ''
        arab = ''
        for tax in self.mapped('invoice_line_ids.tax_ids'):
            vat += str(tax.amount) + '%,'
            arab += str(tax.amount_in_arabic) + '%,'
        self.vat_text = vat[:-1]
        self.vat_arabic_text = arab[:-1]


    def amount_to_words(self):
        amount_in_eng = num2words(self.amount_total, to='currency',
                                  lang='en')

        amount_in_eng = amount_in_eng.replace('euro', 'riyals')
        amount_in_eng = amount_in_eng.replace('cents', 'halala')
        self.amount_text = amount_in_eng
        self.amount_in_ar = num2words(self.amount_total, to='currency',
                                      lang='ar')

    def invoice_validate(self):
        analytic = self.invoice_line_ids.mapped('account_analytic_id')
        if len(analytic) != 1:
            analytic = False
        if self.default_analytic:
            analytic = self.default_analytic
        if analytic is not False:
            for line in self.move_id.line_ids:
                if line.account_id.id == self.account_id.id:
                    line.write({'analytic_account_id': analytic.id, 'partner_id': self.partner_id.id})
        return super(AccountMove, self).invoice_validate()

    def invoice_print(self):
        self.ensure_one()
        self.sent = True
        return self.env['report'].get_action(self, 'custom_azmi_holding.report_azmi_invoicerishi_format_pdt')

class AccountTax(models.Model):
    _inherit = 'account.tax'

    amount_in_arabic = fields.Float('Amount in Arabic')
