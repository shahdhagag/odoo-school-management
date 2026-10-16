from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SchoolClassroom(models.Model):
    _name = 'school.classroom'
    _description = 'School Classroom'
    _rec_name = 'name'
    _order = 'grade_level, name'

    teacher_id = fields.Many2one(
        comodel_name='school.teacher',
        string='Class Teacher',
        ondelete='set null',
    )

    # Classroom Information
    name = fields.Char(
        string='Classroom Name',
        required=True
    )

    code = fields.Char(
        string='Classroom Code',
        required=True,
        copy=False
    )

    grade_level = fields.Selection(
        [
            ('kg', 'Kindergarten'),
            ('primary', 'Primary'),
            ('preparatory', 'Preparatory'),
            ('secondary', 'Secondary'),
        ],
        string='Grade Level',
        required=True
    )

    academic_year_id = fields.Many2one(
        comodel_name='school.academic.year',
        string='Academic Year',
        ondelete='restrict',
    )

    # Capacity
    capacity = fields.Integer(
        string='Maximum Capacity',
        required=True,
        default=30
    )

    # Student Relations
    student_ids = fields.One2many(
        comodel_name='school.student',
        inverse_name='classroom_id',
        string='Students'
    )

    student_count = fields.Integer(
        string='Student Count',
        compute='_compute_student_count',
        store=True
    )

    available_seats = fields.Integer(
        string='Available Seats',
        compute='_compute_available_seats',
        store=True
    )

    # Record Status
    active = fields.Boolean(
        string='Active',
        default=True
    )
    # Attendance Statistics
    attendance_ids = fields.One2many(
        comodel_name='school.attendance',
        inverse_name='classroom_id',
        string='Attendance Records',
    )

    total_attendance_records = fields.Integer(
        string='Total Attendance Records',
        compute='_compute_attendance_statistics',
    )

    present_days = fields.Integer(
        string='Present',
        compute='_compute_attendance_statistics',
    )

    late_days = fields.Integer(
        string='Late',
        compute='_compute_attendance_statistics',
    )

    absent_days = fields.Integer(
        string='Absent',
        compute='_compute_attendance_statistics',
    )

    excused_days = fields.Integer(
        string='Excused',
        compute='_compute_attendance_statistics',
    )

    attendance_rate = fields.Float(
        string='Attendance Rate (%)',
        compute='_compute_attendance_statistics',
        digits=(5, 2),
    )
    _sql_constraints = [
        (
            'classroom_code_unique',
            'UNIQUE(code)',
            'Classroom Code must be unique!'
        ),
    ]

    # Computed Fields
    @api.depends('student_ids.active')
    def _compute_student_count(self):
        for classroom in self:
            classroom.student_count = len(
                classroom.student_ids.filtered('active')
            )

    @api.depends('capacity', 'student_count')
    def _compute_available_seats(self):
        for classroom in self:
            classroom.available_seats = (
                classroom.capacity - classroom.student_count
            )

    # Constraints
    @api.constrains('code')
    def _check_unique_code(self):
        for classroom in self:
            duplicate = self.search([
                ('code', '=', classroom.code),
                ('id', '!=', classroom.id),
            ], limit=1)

            if duplicate:
                raise ValidationError(
                    'Classroom Code must be unique!'
                )

    @api.constrains('capacity')
    def _check_capacity(self):
        for classroom in self:
            if classroom.capacity <= 0:
                raise ValidationError(
                    'Classroom capacity must be greater than zero.'
                )
            enrolled_count = self.env['school.student'].search_count([
                ('classroom_id', '=', classroom.id),
                ('active', '=', True),
            ])
            if enrolled_count > classroom.capacity:
                raise ValidationError(
                    'Classroom capacity cannot be lower than its '
                    'current number of active students.'
                )
    # Compute Attendance Statistics
    @api.depends('attendance_ids.status')
    def _compute_attendance_statistics(self):
        for classroom in self:
            records = classroom.attendance_ids

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

            classroom.total_attendance_records = total
            classroom.present_days = present
            classroom.late_days = late
            classroom.absent_days = absent
            classroom.excused_days = excused

            classroom.attendance_rate = (
                (present + late) / total
                if total else 0.0
            )