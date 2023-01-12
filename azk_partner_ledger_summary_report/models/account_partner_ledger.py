from odoo import models, api, _


class ReportPartnerLedger(models.AbstractModel):
    _inherit = "account.partner.ledger"
    
    def _get_reports_buttons(self):
        """ Add new button for Partner Ledger view buttons: 'Print Customers Summary' """
        result = super()._get_reports_buttons()
        result.append({'name': _('Print Customers Summary'), 'sequence': 8, 'action': 'print_partner_report_summary'})
        return result

    def print_partner_report_summary(self, options):
        """ Generate lines of summarized partner ledger data
            @param options: report options
            @return action of printing the report by its XML ID
            with summary_lines and other needed variables as data of the report action (used in report xml template)
        """
        data = {}
        
        self = self.with_context(report_summary=True)
        # reset unfolded_lines in order to get only partner lines (without journal items)
        options['unfolded_lines'] = []
        line_ids = super()._get_partner_ledger_lines(options, line_id=None)
        
        partner_lines = list(filter(lambda l: l.get('az_line_name') == 'partner_line', line_ids))
        partner_ids = [line.get('partner_id') for line in partner_lines]
        customer_partner_ids = self.env['res.partner'].search([('id', 'in', partner_ids), ('customer_rank', '>', 0)])
        
        customer_lines = list(filter(lambda l: l.get('partner_id') in customer_partner_ids.ids, partner_lines))
        
        # format lines after compute of totals
        totals = {'balance': 0, 'initial_balance': 0, 'credit': 0, 'debit': 0}
        for line in customer_lines:
            to_format = ['balance', 'initial_balance', 'credit', 'debit']
            for key in to_format:
                totals[key] += line.get(key, 0)
                line[key] = self.format_value(line.get(key, 0))
            
        data['summary_lines'] = customer_lines
        data['totals'] = {
                            'balance': self.format_value(totals.get('balance')),
                            'initial_balance': self.format_value(totals.get('initial_balance')),
                            'credit': self.format_value(totals.get('credit')),
                            'debit': self.format_value(totals.get('debit')),
                        }
        data['options'] = options
        return self.env.ref('azk_partner_ledger_summary_report.action_report_partner_ledger_summary').report_action(self, data=data)


    @api.model
    def _get_report_line_partner(self, options, partner, initial_balance, debit, credit, balance):
        """ Add some new values to the result dictionary to be used in summary report """
        result_dict = super()._get_report_line_partner(options, partner, initial_balance, debit, credit, balance)
        result_dict.update({'az_line_name': 'partner_line',
                            'initial_balance': initial_balance,
                            'debit': debit,
                            'credit': credit,
                            'balance': balance,
                            })
        return result_dict

    def format_value(self, amount, currency=False, blank_if_zero=False):
        if self._context.get('report_summary'):
            return "{0}{1:,.2f}{2}".format('(', abs(amount), ')') if amount < 0 else "{:,.2f}".format(amount)
        else:
            return super().format_value(amount, currency=False, blank_if_zero=False)
