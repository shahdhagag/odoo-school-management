from odoo import models, fields, api


class SchoolSubject(models.Model):
    _name = 'school.subject'
    _description = 'School Subject'
    _rec_name = 'name'
    _order = 'name'

    name = fields.Char(
        string='Subject Name',
        required=True,
    )

    code = fields.Char(
        string='Subject Code',
        required=True,
        copy=False,
    )

    description = fields.Text(
        string='Description',
    )

    grade_level = fields.Selection(
        [
            ('grade_1', 'Grade 1'),
            ('grade_2', 'Grade 2'),
            ('grade_3', 'Grade 3'),
            ('grade_4', 'Grade 4'),
            ('grade_5', 'Grade 5'),
            ('grade_6', 'Grade 6'),
            ('grade_7', 'Grade 7'),
            ('grade_8', 'Grade 8'),
            ('grade_9', 'Grade 9'),
            ('grade_10', 'Grade 10'),
            ('grade_11', 'Grade 11'),
            ('grade_12', 'Grade 12'),
        ],
        string='Grade Level',
    )

    active = fields.Boolean(
        string='Active',
        default=True,
    )

    _sql_constraints = [
        (
            'subject_code_unique',
            'unique(code)',
            'Subject code must be unique!',
        ),
    ]