# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import requests
import logging
import datetime

class PosOrder(models.Model):
    _inherit = 'pos.order'

    usuario_leal = fields.Char('Usuario leal')

    @api.model
    def _order_fields(self, ui_order):
        res = super(PosOrder, self)._order_fields(ui_order)
        sesion = self.env['pos.session'].search([('id', '=', res['session_id'])], limit=1)
        logging.warn(res)
        if sesion.config_id.leal and ui_order['usuario_leal']:
            res['usuario_leal'] = ui_order['usuario_leal'] or False
        return res

    @api.model
    def create_from_ui(self, orders):
        res = super(PosOrder, self).create_from_ui(orders)
        if res:
            orden = self.env['pos.order'].search([('id', '=', res[0])], limit=1)
            if res and orden and orden.usuario_leal:
                self.post_pos_leal(orden,orden.invoice_id)
        return res

    def fecha_hora_factura(self, fecha):
        fecha_convertida = datetime.datetime.strptime(str(fecha), '%Y-%m-%d %H:%M:%S.%f').date().strftime('%Y-%m-%d')
        hora = datetime.datetime.strftime(fields.Datetime.context_timestamp(self, datetime.datetime.now()), "%H:%M:%S")
        fecha_hora_emision = str(fecha_convertida)+'T'+str(hora)
        return str(fecha_hora_emision)

    def post_pos_leal(self,orden,factura):
        if orden.session_id and orden.session_id.config_id.user_leal and orden.session_id.config_id.pass_leal and orden.session_id.config_id.id_comercio:

            token = str(orden.session_id.config_id.login_token)
            id_comercio = str(orden.session_id.config_id.id_comercio)

            # VERIFICAMOS USUARIO
            url_search = 'https://api.puntosleal.com/api/usu_usuarios/buscar_usuario/'+str(id_comercio)+'/'+str(orden.usuario_leal)
            if orden.session_id.config_id.test_leal:
                url_search = 'https://testapi.puntosleal.com/api/usu_usuarios/buscar_usuario/'+str(id_comercio)+'/'+str(orden.usuario_leal)

            headers_usuario = {"Authorization": "Bearer %s" %token}
            response_search = requests.get(url_search, headers = headers_usuario)
            response_search_json=response_search.json()

            if 'code' in response_search_json:
                if response_search_json['code'] != 100:
                    raise UserError(str(response_search_json['message']))

            # POST Cargar factura
            url_cargar_factura = 'https://api.puntosleal.com/api/usu_historial_puntos/cargar_factura/'+str(id_comercio)
            if orden.session_id.config_id.test_leal:
                url_cargar_factura = 'https://testapi.puntosleal.com/api/usu_historial_puntos/cargar_factura/'+str(id_comercio)

            logging.warn(factura)
            logging.warn(factura.state)
            formas_pago_lista = []
            for linea_pago in orden.statement_ids:
                formas_pago_lista.append(linea_pago.journal_id.name)

            formas_pago_string = ', '.join(formas_pago_lista)
            fecha = self.fecha_hora_factura(orden.date_order)
            logging.warn(factura.number)
            items = []
            for linea in factura.invoice_line_ids:
                impuesto_unidad = 0
                tipo_impuesto = ''
                if linea.invoice_line_tax_ids:
                    impuesto_unidad = (linea.price_total - linea.price_subtotal) /  linea.quantity
                    precio_unidad = linea.price_unit - impuesto_unidad
                    tipo_impuesto = linea.invoice_line_tax_ids[0].name
                dic_linea = {

                    "idLinea": str(linea.id),
                    "codigoItem": linea.product_id.default_code,
                    "descripcion": linea.product_id.name,
                    "descripcionAdicional": linea.name,
                    "cantidad": linea.quantity,
                    "precioTotal": round(linea.price_total, 2),
                    "precioUnidad": round(precio_unidad, 2),
                    "impuestoUnidad": round(impuesto_unidad, 2),
                    "tipoImpuesto": str(tipo_impuesto),
                }
                items.append(dic_linea)

            transaccion_dic = {
                "clave": str(factura.number),
                "noFactura": str(factura.number),
                "fecha": fecha,
                "fechaApertura": fecha,
                "fechaCierre": fecha,
                "totalPersonas": 1,
                "formaPago": str(formas_pago_string),
                "codVendedor": str(factura.user_id.name),
                "subTotal": round(factura.amount_untaxed,2),
                "propina": 0,
                "impuestoTotal": round(factura.amount_tax,2),
                "descuentoTotal": 0,
                'items': items,

            }

            json_cargar_factura = {
                "id_externo":"",
                "criterio": orden.usuario_leal,
                "totalAcum": round(orden.amount_total,2),
                "transaccion": transaccion_dic,

            }
            logging.warn(json_cargar_factura)
            headers_cargar_factura = {"Authorization": "Bearer %s" %token,"content-type": "application/json; charset=utf-8"}
            request_cargar_factura = requests.post(url_cargar_factura,json= json_cargar_factura,headers=headers_cargar_factura)
            request_cargar_factura_json = request_cargar_factura.json()

            logging.warn(request_cargar_factura_json)

            if 'code' in request_cargar_factura_json:
                if request_cargar_factura_json['code'] == 100:
                    continue
                else:
                    raise UserError(str(request_cargar_factura_json['message']))
            else:
                raise UserError(str('ERROR AL CONECTARSE CON LEAL'))

        return True
