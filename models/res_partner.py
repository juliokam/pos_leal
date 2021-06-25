# -*- encoding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import UserError, ValidationError
import logging

class ResPartner(models.Model):
    _inherit = "res.partner"

    usuario_leal = fields.Char(string="Usuario leal")
