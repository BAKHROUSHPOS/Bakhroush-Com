# -*- coding: utf-8 -*-

from odoo import models, fields, api
import base64
import xlwt
from datetime import datetime, date
# from StringIO import StringIO
from io import BytesIO
import string
import math


class WizardAssetAssetHistory(models.TransientModel):
    _name = 'wizard.asset.asset.history'

    name = fields.Char('Report Name')
    report_file = fields.Binary('File')
    xlsx_date_from = fields.Date('Date From')
    xlsx_date_to = fields.Date('Date To')
    visible = fields.Boolean(default=True)  # To hide the button and payslip_batch field after excel is created.

    def export_asset_xls(self):
        workbook = xlwt.Workbook()
        fl = BytesIO()
        style0 = xlwt.easyxf('font: name Verdana, color-index red, bold on;  align: horiz center,vertical center;', num_format_str='#,##0.00')

        worksheet = workbook.add_sheet('Assets Report')
        font = xlwt.Font()

        font.bold = True

        for_center = xlwt.easyxf(
            "font: name  Verdana, color black,  height 200; align: horiz center,vertical center; borders: top thin, bottom thin, left thin, right thin; pattern: pattern solid, fore_color %s;" % '100')

        for_center_header = xlwt.easyxf(
            "font: name  Verdana, color black,  height 200; align: horiz center,vertical center; borders: top thin, bottom thin, left thin, right thin; pattern: pattern solid, fore_color gray_ega;")

        for_center_header_0 = xlwt.easyxf(
            "font: name  Verdana, color black,  height 200; align: horiz center,vertical center; borders: top thin, bottom thin, left thin, right thin; pattern: pattern solid, fore_color pale_blue;")

        for_string = xlwt.easyxf(
            "font: name  Verdana, color black,  height 200; align: horiz left,vertical center; borders: top thin, bottom thin, left thin, right thin; pattern: pattern solid, fore_color %s;" % '100')


        alignment = xlwt.Alignment()  # Create Alignment
        alignment.horz = xlwt.Alignment.HORZ_RIGHT
        style = xlwt.easyxf('align: wrap yes; borders: top thin, bottom thin, left thin, right thin;')
        style.num_format_str = '#,##0.00'

        style_net_sal = xlwt.easyxf(
            'font:bold 1; align: wrap yes; borders: top medium, bottom medium, left medium, right medium;')
        style_net_sal.num_format_str = '#,##0.00'

        for limit in range(1, 65536):
            worksheet.row(limit).height = 400

        worksheet.row(0).height = 5000
        worksheet.col(1).width = 10000
        worksheet.col(2).width = 7000
        worksheet.col(3).width = 7000
        worksheet.col(4).width = 7000
        worksheet.col(5).width = 7000
        worksheet.col(6).width = 7000
        worksheet.col(7).width = 7000
        worksheet.col(8).width = 7500
        worksheet.col(9).width = 7000
        worksheet.col(10).width = 7000
        worksheet.col(11).width = 7000
        worksheet.col(12).width = 7000


        borders = xlwt.Borders()
        borders.bottom = xlwt.Borders.MEDIUM
        border_style = xlwt.XFStyle()  # Create Style
        border_style.borders = borders


        worksheet.write_merge(0, 0, 0, 10, self.env.user.company_id.name, style0)
        worksheet.write_merge(1, 1, 0, 10, 'Fixed Assets Register', style0)
        worksheet.write_merge(2, 2, 0, 10, 'Report', style0)
        worksheet.write_merge(3, 3, 0, 10,
                              'For the Period (' + datetime.strptime(str(self.xlsx_date_from), '%Y-%m-%d').strftime(
                                  '%m/%d/%y') + '--' + datetime.strptime(str(self.xlsx_date_to),
                                                                         '%Y-%m-%d').strftime('%m/%d/%y') + ')',
                              style0)

        worksheet.write_merge(5, 5, 0, 2, 'Assets Details / بيان الأصل', for_center_header_0)
        worksheet.write_merge(5, 5, 3, 6, 'Assets Value / قيمة الأصل', for_center_header_0)
        worksheet.write_merge(5, 5, 7, 11, 'Asset Accumulated Depreciation / مجمع استهلاك الأصل', for_center_header_0)

        inv_name_row = 6

        worksheet.write(inv_name_row, 0, 'الكود', for_center_header)
        worksheet.write(inv_name_row, 1, 'إسم الأصل', for_center_header)
        worksheet.write(inv_name_row, 2, 'تاريخ الشراء', for_center_header)

        worksheet.write(inv_name_row, 3, 'تاريخ الشراء', for_center_header)
        worksheet.write(inv_name_row, 4, 'الإضافات', for_center_header)
        worksheet.write(inv_name_row, 5, 'الاستبعادات', for_center_header)
        worksheet.write(inv_name_row, 6, 'الإجمالي', for_center_header)

        worksheet.write(inv_name_row, 7, '% اك الاستھل', for_center_header)
        worksheet.write(inv_name_row, 8, 'العام المجمع بدایة', for_center_header)
        worksheet.write(inv_name_row, 9, 'الحالي استھلاك العام', for_center_header)
        worksheet.write(inv_name_row, 10, 'الاستبعادات ', for_center_header)
        worksheet.write(inv_name_row, 11, 'الاستھلاك مجمع', for_center_header)

        worksheet.write(inv_name_row, 12, 'الدفتریة صافي القیمة', for_center_header)

        inv_name_row += 1

        worksheet.write(inv_name_row, 0, 'Asset Code', for_center_header)
        worksheet.write(inv_name_row, 1, 'Asset Name', for_center_header)
        worksheet.write(inv_name_row, 2, 'Date of Purchase', for_center_header)

        worksheet.write(inv_name_row, 3, 'Start Year Value', for_center_header)
        worksheet.write(inv_name_row, 4, 'Addition', for_center_header)
        worksheet.write(inv_name_row, 5, 'Selling Value', for_center_header)
        worksheet.write(inv_name_row, 6, 'Total', for_center_header)

        worksheet.write(inv_name_row, 7, 'Percentage %', for_center_header)
        worksheet.write(inv_name_row, 8, 'Start Year Accumulated', for_center_header)
        worksheet.write(inv_name_row, 9, 'Depreciation Charge During Period', for_center_header)
        worksheet.write(inv_name_row, 10, 'Selling Value', for_center_header)
        worksheet.write(inv_name_row, 11, 'Total', for_center_header)

        worksheet.write(inv_name_row, 12, 'Net Book', for_center_header)

        inv_name_row3 = 8
        asset_ids = self.env['account.asset'].search([])

        for item in asset_ids:

            opening_balance_cost = item.purchased_value if item.acquisition_date < self.xlsx_date_from and item.state == 'open' else 0

            addition_cost = item.purchased_value if item.acquisition_date >= self.xlsx_date_from and item.acquisition_date <= self.xlsx_date_to and item.state in (
            'open', 'close') else 0

            disposal_cost = item.purchased_value if item.acquisition_date >= self.xlsx_date_from and item.acquisition_date <= self.xlsx_date_to and item.state == 'close' else 0

            opening_balance_accumulated_depreciation = sum(line.amount_total for line in item.depreciation_move_ids if
                                                           line.date < self.xlsx_date_from and line.asset_id.state == 'open')

            depreciation_accumulated_depreciation = sum(item.depreciation_move_ids.filtered(
                lambda l: l.date >= self.xlsx_date_from and l.date <= self.xlsx_date_to and l.asset_id.state == 'open').mapped('amount_total'))

            disposal_accumulated_depreciation = sum(line.amount_total for line in item.depreciation_move_ids if
                                                    line.date >= self.xlsx_date_from and line.date <= self.xlsx_date_to and line.asset_id.state == 'close')

            item_closing_balance_cost = float(opening_balance_cost) + float(addition_cost) - float(disposal_cost)

            item_closing_balance_accumulated_depreciation = float(
                opening_balance_accumulated_depreciation) + float(
                depreciation_accumulated_depreciation) - float(disposal_accumulated_depreciation)

            item_net_book = item_closing_balance_cost - item_closing_balance_accumulated_depreciation

            worksheet.write(inv_name_row3, 0, item.code, for_center)
            worksheet.write(inv_name_row3, 1, item.name, for_string)
            worksheet.write(inv_name_row3, 2, item.purchased_date, for_center)

            worksheet.write(inv_name_row3, 3, opening_balance_cost, for_center)
            worksheet.write(inv_name_row3, 4, addition_cost, for_center)
            worksheet.write(inv_name_row3, 5, disposal_cost, for_center)
            worksheet.write(inv_name_row3, 6, item_closing_balance_cost, for_center)

            worksheet.write(inv_name_row3, 7, item.method_progress_factor, for_center)

            worksheet.write(inv_name_row3, 8, opening_balance_accumulated_depreciation, for_center)
            worksheet.write(inv_name_row3, 9, depreciation_accumulated_depreciation, for_center)
            worksheet.write(inv_name_row3, 10, disposal_accumulated_depreciation, for_center)
            worksheet.write(inv_name_row3, 11, item_closing_balance_accumulated_depreciation, for_center)

            worksheet.write(inv_name_row3, 12, item_net_book, for_center)

            inv_name_row3 += 1

        workbook.save(fl)
        fl.seek(0)
        self.write({
            'report_file': base64.encodestring(fl.getvalue()),
            'name': 'Assets.xls'})
        self.visible = False
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'wizard.asset.asset.history',
            'target': 'new',
            'res_id': self.id,
        }
