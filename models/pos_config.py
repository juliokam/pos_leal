# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _
import logging
from odoo.exceptions import UserError
import requests
import datetime

class PosConfig(models.Model):
    _inherit = 'pos.config'

    leal = fields.Boolean('Leal')
    user_leal = fields.Char('Usuario leal')
    pass_leal = fields.Char('Contraseña leal')
    id_comercio = fields.Char('ID Comercio')
    login_token = fields.Char('Token')
    test_leal = fields.Boolean('Prueba leal')

    def generar_token(self):
        pos_config_ids = self.env['pos.config'].search([('user_leal','!=',False),('id_comercio','!=',False),('pass_leal','!=',False)])
        # logging.warn(pos_config_ids)
        if pos_config_ids:
            for pos in pos_config_ids:

                url_login = 'https://api.puntosleal.com/api/com_usuarios/login'
                if pos.test_leal:
                    url_login = 'https://testapi.puntosleal.com/api/com_usuarios/login'

                json = {
                    "usuario": str(pos.user_leal),
                    "contrasena": str(pos.pass_leal)
                    }
                headers = {"content-type": "application/json"}
                response_login = requests.post(url_login, json = json, headers = headers)
                respone_json=response_login.json()
                # logging.warn(respone_json)
                token = False
                if 'code' in respone_json:
                    if respone_json['code'] == 100:
                        if 'token' in respone_json:
                            token = str(respone_json['token'])
                            pos.login_token = token
                    else:
                        respone_json['POS'] = pos.name
                        raise UserError(str(respone_json))
                else:
                    respone_json['POS'] = pos.name
                    raise UserError(str(respone_json))
        return True
