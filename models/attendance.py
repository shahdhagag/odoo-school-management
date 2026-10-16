from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SchoolAttendance(models.Model):
    _name = 'school.attendance'
    _description = 'School Attendance'
    _rec_name = 'student_id'
    _order = 'attendance_date desc, student_id'

    # Attendance Information
    student_id = fields.Many2one(
        comodel_name='school.student',
        string='Student',
        required=True,
        ondelete='restrict'
    )

    classroom_id = fields.Many2one(
        comodel_name='school.classroom',
        string='Classroom',
        required=True,
        ondelete='restrict'
    )

    attendance_date = fields.Date(
        string='Attendance Date',
        required=True,
        default=fields.Date.context_today
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

    notes = fields.Text(
        string='Notes'
    )

    # Automatically select the student's classroom
    @api.onchange('student_id')
    def _onchange_student_id(self):
        if self.student_id:
            self.classroom_id = self.student_id.classroom_id
        else:
            self.classroom_id = False

    # Validate that the student belongs to the selected classroom
    @api.constrains('student_id', 'classroom_id')
    def _check_student_classroom(self):
        for attendance in self:
            if (
                attendance.student_id
                and attendance.classroom_id
                and attendance.student_id.classroom_id
                != attendance.classroom_id
            ):
                raise ValidationError(
                    "The selected classroom must match "
                    "the student's current classroom."
                )

    @api.constrains('student_id', 'classroom_id')
    def _check_active_enrollment(self):
        for attendance in self:
            if (
                attendance.student_id
                and (
                    not attendance.student_id.active
                    or attendance.student_id.state != 'active'
                )
            ):
                raise ValidationError(
                    "Attendance can only be recorded for active students."
                )
            if attendance.classroom_id and not attendance.classroom_id.active:
                raise ValidationError(
                    "Attendance can only be recorded for active classrooms."
                )

    # Prevent duplicate attendance for the same student on the same date
    _sql_constraints = [
        (
            'unique_student_attendance_date',
            'UNIQUE(student_id, attendance_date)',
            'Attendance has already been recorded for this student on this date.'
        ),
    ]