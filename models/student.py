from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SchoolStudent(models.Model):
    _name = 'school.student'
    _description = 'School Student'
    _rec_name = 'name'
    _order = 'student_number'

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