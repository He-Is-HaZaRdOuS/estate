{
    'name': "Real Estate",
    'version': '1.0',
    'depends': ['base', 'mail'],
    'author': "Ballzagna0x0a",
    'application': True,
    'installable': True,
    'license': 'LGPL-3',
    'category': 'Real Estate/Brokerage',
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'report/estate_email_template.xml',
        'report/estate_pdf_template.xml',
        'report/estate_action_report.xml',
        'data/ir_cron.xml',
        'data/estate_property_type.xml',
        'views/estate_property_views.xml',
        'views/estate_property_wizard_views.xml',
        'views/estate_property_offer_views.xml',
        'views/estate_property_type_views.xml',
        'views/estate_property_tag_views.xml',
        'views/estate_menus.xml',
        'views/res_users_views.xml'
    ],
    'demo': [
        'demo/estate_property_demo_data.xml',
        'demo/estate_property_offer_demo_data.xml',
    ]
}
