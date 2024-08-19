{
    'name': "Real Estate",
    'version': '1.0',
    'depends': ['base'],
    'author': "Ballzagna0x0a",
    'application': True,
    'installable': True,
    'license': 'LGPL-3',
    'category': 'Brokerage',
    'data': [
        'security/ir.model.access.csv',
        'data/estate_property_type.xml',
        'views/estate_property_views.xml',
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
