odoo.define('pos_leal.pos_leal', function (require) {
"use strict";


var screens = require('point_of_sale.screens');
var models = require('point_of_sale.models');
var db = require('point_of_sale.DB');
var rpc = require('web.rpc');
var gui = require('point_of_sale.gui');
var core = require('web.core');
var PopupWidget = require('point_of_sale.popups');
var PosBaseWidget = require('point_of_sale.BaseWidget');
var chrome = require('point_of_sale.chrome');
var QWeb = core.qweb;
var _t = core._t;

// models.load_fields('res.partner','usuario_leal');

models.PosModel = models.PosModel.extend({
    get_usuario_leal: function(){
        return this.get('usuario_leal');
    },
    set_usuario_leal: function(usuario_leal){
        this.set('usuario_leal', usuario_leal);
    }
})

var _super_order = models.Order.prototype;
models.Order = models.Order.extend({
    export_as_JSON: function() {
        var json = _super_order.export_as_JSON.apply(this,arguments);
        if (this.pos.get_usuario_leal()){
            json.usuario_leal = this.pos.get_usuario_leal();
        }else{
            json.usuario_leal = false;
        }
        console.log(json)
        return json;
    },
    init_from_JSON: function(json) {
        _super_order.init_from_JSON.apply(this,arguments);
        this.usuario_leal = this.pos.get_usuario_leal() || false;
    },

})

screens.ActionpadWidget.include({
  renderElement: function(){
      PosBaseWidget.prototype.renderElement.call(this);
      var self = this;
      this._super();
      this.$('.pay').click(function(){
          self.gui.show_screen('products');
          self.gui.show_popup('textinput',{
              'title': 'Ingrese usuario leal',
              'confirm': function(usuario_leal) {
                    self.pos.set_usuario_leal(usuario_leal);
                    self.gui.show_screen('payment');
              },
          });

      });

  },

});

});
