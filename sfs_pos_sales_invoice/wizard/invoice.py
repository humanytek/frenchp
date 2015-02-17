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
import time
from datetime import datetime
from tools.translate import _

class invoice_sale(osv.osv_memory):
    _name = 'invoice.sale'
    _columns = {
        'name': fields.many2one('res.partner', 'Customer', required=True),
        'pos_order_ids': fields.many2many('pos.order', 'customer_order_rel', 'customer_id', 'order_id', 'Pos Order'),
        'journal_id': fields.many2one('account.journal', 'Journal', required=True),
        'currency_id': fields.many2one('res.currency', 'Currency'),
    }
    
    def _get_currency(self, cr, uid, ctx):
        comp = self.pool.get('res.users').browse(cr, uid, uid).company_id
        if not comp:
            comp_id = self.pool.get('res.company').search(cr, uid, [])[0]
            comp = self.pool.get('res.company').browse(cr, uid, comp_id)
        return comp.currency_id.id
    
    _defaults = {
        'currency_id': _get_currency
    }
    
    def invoice(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService("workflow")
        inv_ref = self.pool.get('account.invoice')
        inv_line_ref = self.pool.get('account.invoice.line')
        product_obj = self.pool.get('product.product')
        data = self.browse(cr, uid, ids[0], context=context)
        inv_ids = []
        for invoice in self.browse(cr, uid, ids, context=context):
            acc = invoice.name.property_account_receivable.id
            inv = {
            'name': 'Pos Invoice-'+time.strftime('%Y-%m-%d'),
            'origin': '',
            'account_id': acc or False,
            'journal_id': invoice.journal_id.id,
            'type': 'out_invoice',
            'reference': 'Pos Invoice-'+time.strftime('%Y-%m-%d'),
            'partner_id': invoice.name.id , 
            'comment': '', 
            'currency_id': invoice.currency_id.id,
            'direct_pay': True
            }
            inv.update(inv_ref.onchange_partner_id(cr, uid, [], 'out_invoice', invoice.name.id)['value'])
            if not inv.get('account_id', None):
                inv['account_id'] = acc
            inv_id = inv_ref.create(cr, uid, inv, context=context)
            comment=""
            raise_error = True
            for order in invoice.pos_order_ids:
                comment+= order.name + '\n'
                inv_line = {}
                for line in order.lines:
                    if line.price_unit !=0:
                        raise_error = False
                        inv_line = {
                        'invoice_id': inv_id,
                        'product_id': line.product_id.id,
                        'quantity': line.qty,
                                    }
                        inv_name = product_obj.name_get(cr, uid, [line.product_id.id], context=context)[0][1]
                        inv_line.update(inv_line_ref.product_id_change(cr, uid, [],
                                                                   line.product_id.id,
                                                                   line.product_id.uom_id.id,
                                                                   line.qty, partner_id = invoice.name.id ,
                                                                   fposition_id = invoice.name.property_account_position.id )['value'])
                        if line.product_id.description_sale:
                            inv_line['note'] = line.product_id.description_sale
                        inv_line['price_unit'] = line.price_unit
                        inv_line['discount'] = order.discount_percentage
                        inv_line['name'] = inv_name
                        inv_line['invoice_line_tax_id'] = ('invoice_line_tax_id' in inv_line)\
                            and [(6, 0, inv_line['invoice_line_tax_id'])] or []
                        inv_line_ref.create(cr, uid, inv_line, context=context)
                inv_ref.button_reset_taxes(cr, uid, [inv_id], context=context)
                inv_ref.write(cr, uid, inv_id, {'comment':comment}, context=context)
                if inv_line:
                    self.pool.get('pos.order').write(cr, uid, [order.id], {'invoice_id': inv_id, 'state': 'invoiced'}, context=context)
            if raise_error:
                raise osv.except_osv(_('Error'), _('No order with unit price greater than 0 selected'))
            wf_service.trg_validate(uid, 'pos.order', order.id, 'invoice', cr)
        if not inv_id: return {}
        mod_obj = self.pool.get('ir.model.data')
        res = mod_obj.get_object_reference(cr, uid, 'account', 'invoice_form')
        res_id = res and res[1] or False
        return {
            'name': ('Customer Invoice'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': [res_id],
            'res_model': 'account.invoice',
            'context': "{'type':'out_invoice'}",
            'type': 'ir.actions.act_window',
            'nodestroy': False,
            'target': 'current',
            'res_id': inv_id or False,
        }
 
invoice_sale()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: