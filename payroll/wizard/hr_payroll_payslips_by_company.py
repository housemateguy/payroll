from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class HrPayslipCompany(models.TransientModel):
    _name = "hr.payslip.company"
    _description = "Generate payslips for all employees in selected timeframe"

    company_id = fields.Many2one('res.company', string='Company', required=True)
    date_from = fields.Date(string='Start Date', required=True)
    date_to = fields.Date(string='End Date', required=True)

    def generate_payslips(self):
        payslip_obj = self.env['hr.payslip']
        employees = self.env['hr.employee'].search([('company_id', '=', self.company_id.id)])
        for employee in employees:
            contract = self.env['hr.contract'].search([('employee_id', '=', employee.id), ('date_end', '>=', self.date_from), ('date_start', '<=', self.date_to)], limit=1)
            if contract:
                payslip = payslip_obj.search([('employee_id', '=', employee.id), ('date_from', '=', self.date_from), ('date_to', '=', self.date_to)])
                if not payslip:
                    payslip_obj.create({
                        'employee_id': employee.id,
                        'date_from': self.date_from,
                        'date_to': self.date_to,
                        'contract_id': contract.id,
                        'struct_id': contract.struct_id.id,
                        'state': 'draft',
                        'company_id': self.company_id.id,
                    })
            else:
                raise ValidationError(_('No contract found for employee %s') % employee.name)
            payslip.compute_sheet()


