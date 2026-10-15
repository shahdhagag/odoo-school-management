from odoo import models, fields, api


class SchoolStudent(models.Model):
    _name = 'school.student'
    _description = 'School Student'
    _rec_name = 'name'
    _order = 'student_number'

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

    email = fields.Char(
        string='Email'
    )

    phone = fields.Char(
        string='Phone'
    )

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
        required=True
    )

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