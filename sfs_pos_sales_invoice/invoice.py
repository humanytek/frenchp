# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2013 SF Soluciones.
#    (http://www.sfsoluciones.com)
#    contacto@sfsoluciones.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv, fields

import netsvc
import amount_to_text_es_MX

class account_invoice(osv.osv):
    _inherit = 'account.invoice'
    
    def convert(self, cr, uid, ids, amount, currency_obj, context=None):
        amt = ''
        amount = float(amount)
        currency_name = currency_obj.name
        sub_currency = currency_obj.sub_currency
        if currency_name == 'USD':
            currency_name = 'DOLARES'
        amt = amount_to_text_es_MX.get_amount_to_text(self, amount, 'es_cheque', currency_name)
        return amt
    
    def _get_amount_to_text(self, cr, uid, ids, field_names=None, arg=False, context={}):
       if not context:
           context={}
       res = {}
       for invoice in self.browse(cr, uid, ids, context=context):
           amount_to_text = self.convert(cr, uid, ids, invoice.amount_total, invoice.currency_id, context=context)
           res[invoice.id] = amount_to_text
       return res
    
    _columns = {
                'amount_to_text':  fields.function(_get_amount_to_text, method=True, type='char', size=256, 
                                                   string='Amount to Text', store=True),
                'direct_pay': fields.boolean('Direct Pay')
                }
    
    def validate_invoice(self, cr, uid, ids, context=None):
        res = True
        obj_model = self.pool.get('ir.model.data')
        wf_service = netsvc.LocalService("workflow")
        for invoice_obj in self.browse(cr, uid, ids, context=context):
            wf_service.trg_validate(uid, 'account.invoice', invoice_obj.id, 'invoice_open', cr)
            if invoice_obj.direct_pay:
                model_data_ids = obj_model.search(cr,uid,[('model','=','ir.ui.view'),
                                                          ('name','=','view_invoice_journal_select_form')])
                resource_id = obj_model.read(cr, uid, model_data_ids, fields=['res_id'])[0]['res_id']
                context['invoice_id'] = invoice_obj.id
                res = {
                       'name': 'Select Journal',
                       'view_type': 'form',
                       'view_mode': 'form',
                       'res_model': 'account.journal.select',
                       'views': [(resource_id,'form')],
                       'type': 'ir.actions.act_window',
                       'context': context,
                       'target': 'new',
                       'nodestroy': True,
                       }
        return res

account_invoice()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
