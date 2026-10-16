from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SchoolAcademicYear(models.Model):
    _name = 'school.academic.year'
    _description = 'School Academic Year'
    _order = 'start_date desc'

    name = fields.Char(
        string='Academic Year',
        required=True,
        copy=False,
    )

    start_date = fields.Date(
        string='Start Date',
        required=True,
    )

    end_date = fields.Date(
        string='End Date',
        required=True,
    )

    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('active', 'Active'),
            ('closed', 'Closed'),
        ],
        string='Status',
        default='draft',
        required=True,
    )

    term_ids = fields.One2many(
        'school.academic.term',
        'academic_year_id',
        string='Semesters',
    )

    _sql_constraints = [
        (
            'academic_year_name_unique',
            'UNIQUE(name)',
            'Academic year name must be unique.',
        ),
    ]

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for record in self:
            if record.start_date and record.end_date:
                if record.end_date <= record.start_date:
                    raise ValidationError(
                        'The end date must be after the start date.'
                    )

    @api.constrains('start_date', 'end_date')
    def _check_overlapping_years(self):
        for record in self:
            if not record.start_date or not record.end_date:
                continue

            overlapping_year = self.search([
                ('id', '!=', record.id),
                ('start_date', '<=', record.end_date),
                ('end_date', '>=', record.start_date),
            ], limit=1)

            if overlapping_year:
                raise ValidationError(
                    'Academic years cannot overlap.'
                )

    def action_activate(self):
        for record in self:
            record.state = 'active'

    def action_close(self):
        for record in self:
            record.state = 'closed'


class SchoolAcademicTerm(models.Model):
    _name = 'school.academic.term'
    _description = 'School Academic Semester'
    _order = 'start_date'

    name = fields.Selection(
        [
            ('semester_1', 'First Semester'),
            ('semester_2', 'Second Semester'),
        ],
        string='Semester',
        required=True,
    )

    academic_year_id = fields.Many2one(
        'school.academic.year',
        string='Academic Year',
        required=True,
        ondelete='cascade',
    )

    start_date = fields.Date(
        string='Start Date',
        required=True,
    )

    end_date = fields.Date(
        string='End Date',
        required=True,
    )

    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('active', 'Active'),
            ('closed', 'Closed'),
        ],
        string='Status',
        default='draft',
        required=True,
    )

    _sql_constraints = [
        (
            'academic_term_unique',
            'UNIQUE(academic_year_id, name)',
            'Each semester can only be created once per academic year.',
        ),
    ]

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for record in self:
            if record.start_date and record.end_date:
                if record.end_date <= record.start_date:
                    raise ValidationError(
                        'The semester end date must be after its start date.'
                    )

    @api.constrains(
        'start_date',
        'end_date',
        'academic_year_id',
    )
    def _check_academic_year_dates(self):
        for record in self:
            year = record.academic_year_id

            if not year or not record.start_date or not record.end_date:
                continue

            if (
                record.start_date < year.start_date
                or record.end_date > year.end_date
            ):
                raise ValidationError(
                    'Semester dates must fall within the academic year.'
                )

    @api.constrains(
        'start_date',
        'end_date',
        'academic_year_id',
    )
    def _check_overlapping_terms(self):
        for record in self:
            overlapping_term = self.search([
                ('id', '!=', record.id),
                ('academic_year_id', '=', record.academic_year_id.id),
                ('start_date', '<=', record.end_date),
                ('end_date', '>=', record.start_date),
            ], limit=1)

            if overlapping_term:
                raise ValidationError(
                    'Semesters in the same academic year cannot overlap.'
                )
