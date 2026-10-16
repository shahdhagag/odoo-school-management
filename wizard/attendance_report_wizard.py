from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SchoolAttendanceReportWizard(models.TransientModel):
    _name = 'school.attendance.report.wizard'
    _description = 'Attendance Report Wizard'

    classroom_id = fields.Many2one(
        comodel_name='school.classroom',
        string='Classroom',
        required=True,
    )

    date_from = fields.Date(
        string='Start Date',
        required=True,
        default=fields.Date.context_today,
    )

    date_to = fields.Date(
        string='End Date',
        required=True,
        default=fields.Date.context_today,
    )

    total_records = fields.Integer(
        string='Total Attendance Records',
        readonly=True,
    )

    present_count = fields.Integer(
        string='Present',
        readonly=True,
    )

    late_count = fields.Integer(
        string='Late',
        readonly=True,
    )

    absent_count = fields.Integer(
        string='Absent',
        readonly=True,
    )

    excused_count = fields.Integer(
        string='Excused',
        readonly=True,
    )

    attendance_rate = fields.Float(
        string='Attendance Rate (%)',
        digits=(5, 2),
        readonly=True,
    )

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for wizard in self:
            if (
                wizard.date_from
                and wizard.date_to
                and wizard.date_from > wizard.date_to
            ):
                raise ValidationError(
                    'Start Date cannot be later than End Date.'
                )

    def action_generate_report(self):
        self.ensure_one()

        if self.date_from > self.date_to:
            raise ValidationError(
                'Start Date cannot be later than End Date.'
            )

        records = self.env['school.attendance'].search([
            ('classroom_id', '=', self.classroom_id.id),
            ('attendance_date', '>=', self.date_from),
            ('attendance_date', '<=', self.date_to),
        ])

        total = len(records)
        present = len(records.filtered(
            lambda record: record.status == 'present'
        ))
        late = len(records.filtered(
            lambda record: record.status == 'late'
        ))
        absent = len(records.filtered(
            lambda record: record.status == 'absent'
        ))
        excused = len(records.filtered(
            lambda record: record.status == 'excused'
        ))

        self.write({
            'total_records': total,
            'present_count': present,
            'late_count': late,
            'absent_count': absent,
            'excused_count': excused,
            'attendance_rate': (
                (present + late) / total
                if total else 0.0
            ),
        })

        return {
            'type': 'ir.actions.act_window',
            'name': 'Attendance Report',
            'res_model': 'school.attendance.report.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }
