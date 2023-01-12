from odoo import models, api, _

class ReportGeneralLedger(models.AbstractModel):
    _inherit = "account.general.ledger"
    
    def _get_reports_buttons(self):
        """ Add new button for General Ledger view buttons: 'Print Summary' """
        result = super()._get_reports_buttons()
        result.append({'name': _('Print Summary'), 'sequence': 8, 'action': 'print_report_summary'})
        return result

    def print_report_summary(self, options):
        """ Generate lines of summarized general ledger data
            @param options: report options
            @return action of printing the report by its XML ID
            with summary_lines and other needed variables as data of the report action (used in report xml template)
        """
        data = {}
        summary_lines = []
        
        # unfold all lines in order to get initial balance lines
        options['unfold_all'] = True
        line_ids = self._get_general_ledger_lines(options, line_id=None)
        
        # define dictionary for initial balance values for each account
        initial_balances_dict = {}
        initial_balance_lines = list(filter(lambda l: l.get('az_line_name') == 'initial_balance_line', line_ids))
        for line in initial_balance_lines:
            initial_balances_dict[line.get('account_id').id] = {'initial_balance': line.get('initial_balance', 0),
                                                                'initial_credit': line.get('initial_credit', 0),
                                                                'initial_debit': line.get('initial_debit', 0)
                                                                }
        
        account_lines = list(filter(lambda l: l.get('az_line_name') == 'account_line', line_ids))
        for account_line in account_lines:
            account = account_line.get('account_id')
            initial_balance = initial_balances_dict.get(account.id)
            # logic:
            # 1- if the account line is unfoldable this means no current balance for it
            #    ==> the data belongs to previous period (initial balance), so the current credit and debit are 0 and total balance = initial balance
            #    (line is unfoldable means the initial_balance variable is None (no initial balance line))
            # 2- account_line contains total credit and total debit (with initial balance values) so current credit = credit - initial credit, same for debit
            summary_lines.append({'account_number': account.code,
                                  'account_name': account.name,
                                  'balance': account_line.get('balance', 0),
                                  'initial_balance': initial_balance.get('initial_balance', 0) if initial_balance != None else account_line.get('balance', 0),
                                  'credit': account_line.get('credit', 0) - initial_balance.get('initial_credit') if initial_balance != None else 0,
                                  'debit': account_line.get('debit', 0) - initial_balance.get('initial_debit') if initial_balance != None else 0,
                                  }) 
        
        data['summary_lines'] = summary_lines
        data['options'] = options
        data['totals'] = {
                            'balance': sum([sl.get('balance') for sl in summary_lines]),
                            'initial_balance': sum([sl.get('initial_balance') for sl in summary_lines]),
                            'credit': sum([sl.get('credit') for sl in summary_lines]),
                            'debit': sum([sl.get('debit') for sl in summary_lines]),
                        }
        return self.env.ref('azk_general_ledger_summary_report.action_report_general_ledger_summary').report_action(self, data=data)

    @api.model
    def _get_account_title_line(self, options, account, amount_currency, debit, credit, balance, has_lines):
        """ Add some new values to the result dictionary to be used in summary report """
        result_dict = super()._get_account_title_line(options, account, amount_currency, debit, credit, balance, has_lines)
        result_dict.update({'az_line_name': 'account_line',
                            'account_id': account,
                            'balance': balance,
                            'credit': credit,
                            'debit': debit
                            })
        return result_dict

    @api.model
    def _get_initial_balance_line(self, options, account, amount_currency, debit, credit, balance):
        """ Add some new values to the result dictionary to be used in summary report """
        result_dict = super()._get_initial_balance_line(options, account, amount_currency, debit, credit, balance)
        result_dict.update({'az_line_name': 'initial_balance_line',
                            'account_id': account,
                            'initial_balance': balance,
                            'initial_credit': credit,
                            'initial_debit': debit
                            })
        return result_dict