from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SchoolAttendanceWizard(models.TransientModel):
    _name = 'school.attendance.wizard'
    _description = 'Bulk Attendance Registration Wizard'

    classroom_id = fields.Many2one(
        comodel_name='school.classroom',
        string='Classroom',
        required=True
    )

    attendance_date = fields.Date(
        string='Attendance Date',
        required=True,
        default=fields.Date.context_today
    )

    line_ids = fields.One2many(
        comodel_name='school.attendance.wizard.line',
        inverse_name='wizard_id',
        string='Students'
    )


    @api.onchange('classroom_id', 'attendance_date')
    def _onchange_classroom_id(self):
        self.line_ids = [(5, 0, 0)]

        if not self.classroom_id:
            return

        students = self.env['school.student'].search([
            ('classroom_id', '=', self.classroom_id.id),
            ('state', '=', 'active'),
            ('active', '=', True),
        ])

        lines = []

        for student in students:
            existing_attendance = self.env['school.attendance'].search([
                ('student_id', '=', student.id),
                ('attendance_date', '=', self.attendance_date or fields.Date.context_today(self)),
            ], limit=1)

            lines.append((0, 0, {
                'student_id': student.id,
                'status': (
                    existing_attendance.status
                    if existing_attendance
                    else 'present'
                ),
                'already_recorded': bool(existing_attendance),
            }))

        self.line_ids = lines
    def action_confirm_attendance(self):
        self.ensure_one()

        if not self.line_ids:
            raise ValidationError(
                "There are no students in the selected classroom."
            )

        Attendance = self.env['school.attendance']

        for line in self.line_ids:
            existing_attendance = Attendance.search([
                ('student_id', '=', line.student_id.id),
                ('attendance_date', '=', self.attendance_date),
            ], limit=1)

            if existing_attendance:
                # Update the existing record instead of creating a duplicate.
                existing_attendance.write({
                    'classroom_id': self.classroom_id.id,
                    'status': line.status,
                })
            else:
                Attendance.create({
                    'student_id': line.student_id.id,
                    'classroom_id': self.classroom_id.id,
                    'attendance_date': self.attendance_date,
                    'status': line.status,
                })

        return {'type': 'ir.actions.act_window_close'}


class SchoolAttendanceWizardLine(models.TransientModel):
    _name = 'school.attendance.wizard.line'
    _description = 'Bulk Attendance Wizard Line'

    wizard_id = fields.Many2one(
        comodel_name='school.attendance.wizard',
        string='Wizard',
        required=True,
        ondelete='cascade'
    )

    student_id = fields.Many2one(
        comodel_name='school.student',
        string='Student',
        required=True,
        readonly=True
    )

    status = fields.Selection(
        [
            ('present', 'Present'),
            ('absent', 'Absent'),
            ('late', 'Late'),
            ('excused', 'Excused'),
        ],
        string='Status',
        required=True,
        default='present'
    )

    already_recorded = fields.Boolean(
        string='Already Recorded',
        readonly=True
    )