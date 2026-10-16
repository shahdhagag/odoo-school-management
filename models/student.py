from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SchoolStudent(models.Model):
    _name = 'school.student'
    _description = 'School Student'
    _rec_name = 'name'
    _order = 'student_number'
    classroom_id = fields.Many2one(
        comodel_name='school.classroom',
        string='Classroom',
        ondelete='restrict'
    )
    attendance_ids = fields.One2many(
        comodel_name='school.attendance',
        inverse_name='student_id',
        string='Attendance Records',
    )
    total_attendance_records = fields.Integer(
        string='Total Attendance Records',
        compute='_compute_attendance_statistics',
    )

    present_days = fields.Integer(
        string='Present Days',
        compute='_compute_attendance_statistics',
    )

    late_days = fields.Integer(
        string='Late Days',
        compute='_compute_attendance_statistics',
    )

    absent_days = fields.Integer(
        string='Absent Days',
        compute='_compute_attendance_statistics',
    )

    excused_days = fields.Integer(
        string='Excused Days',
        compute='_compute_attendance_statistics',
    )

    attendance_rate = fields.Float(
        string='Attendance Rate (%)',
        compute='_compute_attendance_statistics',
        digits=(5, 2),
    )
    # Student Information
    name = fields.Char(
        string='Full Name',
        required=True
    )

    student_number = fields.Char(
        string='Student Number',
        readonly=True,
        copy=False,
        default='New'
    )

    date_of_birth = fields.Date(
        string='Date of Birth'
    )

    age = fields.Integer(
        string='Age',
        compute='_compute_age'
    )

    gender = fields.Selection(
        [
            ('male', 'Male'),
            ('female', 'Female'),
        ],
        string='Gender'
    )

    # Contact Information
    email = fields.Char(
        string='Email'
    )

    phone = fields.Char(
        string='Phone'
    )

    # Record Information
    active = fields.Boolean(
        string='Active',
        default=True
    )

    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('active', 'Active'),
            ('graduated', 'Graduated'),
            ('cancelled', 'Cancelled'),
        ],
        string='Status',
        default='draft',
        required=True,
        copy=False
    )

    _sql_constraints = [
        (
            'student_number_unique',
            'UNIQUE(student_number)',
            'Student number must be unique.'
        ),
    ]

    @api.depends('attendance_ids.status')
    def _compute_attendance_statistics(self):
        for student in self:
            records = student.attendance_ids

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

            student.total_attendance_records = total
            student.present_days = present
            student.late_days = late
            student.absent_days = absent
            student.excused_days = excused

            student.attendance_rate = (
                (present + late) / total
                if total else 0.0
            )
    # Calculate Student Age
    @api.depends('date_of_birth')
    def _compute_age(self):
        today = fields.Date.today()

        for student in self:
            if student.date_of_birth:
                birthday = student.date_of_birth

                student.age = (
                    today.year
                    - birthday.year
                    - (
                        (today.month, today.day)
                        < (birthday.month, birthday.day)
                    )
                )
            else:
                student.age = 0

    # Validate Date of Birth
    @api.constrains('date_of_birth')
    def _check_date_of_birth(self):
        today = fields.Date.today()

        for student in self:
            if (
                student.date_of_birth
                and student.date_of_birth > today
            ):
                raise ValidationError(
                    "Date of Birth cannot be in the future."
                )

    @api.constrains('classroom_id', 'active')
    def _check_classroom_capacity(self):
        for student in self:
            if not student.classroom_id or not student.active:
                continue

            enrolled_count = self.search_count([
                ('classroom_id', '=', student.classroom_id.id),
                ('active', '=', True),
            ])
            if enrolled_count > student.classroom_id.capacity:
                raise ValidationError(
                    "The classroom capacity has been exceeded."
                )

    # Generate Student Number Automatically
    @api.model
    def create(self, vals):
        if vals.get('student_number', 'New') == 'New':
            vals['student_number'] = (
                self.env['ir.sequence'].next_by_code(
                    'school.student.sequence'
                ) or 'New'
            )

        return super(SchoolStudent, self).create(vals)

    # Student Workflow Actions
    def action_activate(self):
        for student in self:
            if student.state == 'draft':
                student.state = 'active'

    def action_graduate(self):
        for student in self:
            if student.state == 'active':
                student.state = 'graduated'

    def action_cancel(self):
        for student in self:
            if student.state in ('draft', 'active'):
                student.state = 'cancelled'