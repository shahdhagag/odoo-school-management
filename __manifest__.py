{
    'name': 'School Management System',
    'version': '15.0.1.0.0',
    'summary': 'Manage students, teachers, classes, and school operations',
    'description': """
        School Management System
        ========================
        Manage:
        - Students
        - Teachers
        - Classrooms
        - Subjects
        - Attendance
        - Exams and Grades
        - School Fees
    """,
    'author': 'Shahd Ahmed Youssef',
    'category': 'Education',
    'license': 'LGPL-3',
    'depends': ['base'],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'data/student_sequence.xml',
        'data/teacher_sequence.xml',
        'views/student_views.xml',
        'views/classroom_views.xml',
        'views/teacher_views.xml',
        'views/subject_views.xml',
        'views/attendance_views.xml',
        'wizard/attendance_wizard_views.xml',
        'wizard/attendance_report_wizard_views.xml',
        'views/academic_year_views.xml',
    ],
    'installable': True,
    'application': True,
}