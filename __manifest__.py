# -*- coding: utf-8 -*-

{
    'name': 'Puntos leal',
    'version': '1.0',
    'category': 'Custom',
    'summary': 'Puntos leal',
    'description': """ Registro de puntos leal in POS """,
    'website': '',
    'author': 'JS',
    'depends': ['base','point_of_sale'],
    'data': [
        'views/res_partner_view.xml',
        'views/pos_config_view.xml',
        'views/templates.xml',
        'data/ir_cron_data.xml',
    ],
    'qweb': [
        'static/src/xml/pos.xml',
    ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
