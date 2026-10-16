from odoo import models, fields, api


class SchoolTeacher(models.Model):
    _name = 'school.teacher'
    _description = 'School Teacher'
    _rec_name = 'name'
    _order = 'name'

    subject_ids = fields.Many2many(
        comodel_name='school.subject',
        relation='school_teacher_subject_rel',
        column1='teacher_id',
        column2='subject_id',
        string='Subjects',
    )
    classroom_ids = fields.One2many(
        comodel_name='school.classroom',
        inverse_name='teacher_id',
        string='Classrooms',
    )

    classroom_count = fields.Integer(
        string='Classroom Count',
        compute='_compute_classroom_count',
    )

    @api.depends('classroom_ids')
    def _compute_classroom_count(self):
        for teacher in self:
            teacher.classroom_count = len(teacher.classroom_ids)
    name = fields.Char(
        string='Teacher Name',
        required=True,
    )

    teacher_number = fields.Char(
        string='Teacher Number',
        required=True,
        copy=False,
        readonly=True,
        default='New',
    )

    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone')

    hire_date = fields.Date(
        string='Hire Date',
        default=fields.Date.context_today,
    )

    gender = fields.Selection(
        [
            ('male', 'Male'),
            ('female', 'Female'),
        ],
        string='Gender',
    )

    active = fields.Boolean(default=True)

    _sql_constraints = [
        (
            'teacher_number_unique',
            'UNIQUE(teacher_number)',
            'Teacher number must be unique.'
        ),
    ]

    @api.model
    def create(self, vals):
        if vals.get('teacher_number', 'New') == 'New':
            vals['teacher_number'] = self.env['ir.sequence'].next_by_code(
                'school.teacher'
            ) or 'New'

        return super(SchoolTeacher, self).create(vals)