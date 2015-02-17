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
from datetime import datetime

class account_journal_select(osv.osv_memory):
    _name = 'account.journal.select'
    _description = 'wizard to select the invoice'
    _columns = {
                'journal_id': fields.many2one('account.journal', 'Journal', required=True)
                }
    
    def make_pay(self, cr, uid, ids, context=None):
        invoice_pool = self.pool.get('account.invoice')
        voucher_pool = self.pool.get('account.voucher')
        journal_pool = self.pool.get('account.journal')
        data = self.read(cr, uid, ids, [])[0]
        journal_id = data['journal_id'][0]
        invoice_id = context.get('invoice_id', False)
        wf_service = netsvc.LocalService("workflow")
        voucher_ids = []
        now = datetime.now()
        today = now.strftime('%Y-%m-%d')
        journal_obj = journal_pool.browse(cr, uid, journal_id, context=context)
        company_id = self.pool.get('res.company')._company_default_get(cr, uid, 'account.voucher',
                                                                       context=context)
        if invoice_id:
            invoice_obj = invoice_pool.browse(cr, uid, invoice_id, context=context)
            type = invoice_obj.type in ('out_invoice','out_refund') and 'receipt' or 'payment'
            ctx = {
                   'close_after_process': True,
                   'invoice_type':invoice_obj.type,
                   'invoice_id':invoice_obj.id,
                   'default_type': invoice_obj.type in ('out_invoice','out_refund') and 'receipt' or 'payment',
                   'type': type,
                   'journal_id': journal_id
                   }
            context.update(ctx)
            vals = {
                    'partner_id': invoice_obj.partner_id.id,
                    'amount': invoice_obj.residual,
                    'name':invoice_obj.name,
                    'journal_id': journal_id
                    }
            tax_id = voucher_pool._get_tax(cr, uid, context=context)
            onchange_journal_id = voucher_pool.onchange_journal(cr, uid, ids, journal_id, [], tax_id, invoice_obj.partner_id.id,
                                                                today, invoice_obj.residual, type, company_id,
                                                                context=context)
            res = onchange_journal_id['value']
            new_line_data = []
            for line_data in res.get('line_cr_ids', []):
                new_line_data.append((0, 0, line_data))
            res['line_cr_ids'] = new_line_data
            new_line_data = []
            for line_data in res.get('line_dr_ids', []):
                new_line_data.append((0, 0, line_data))
            res['line_dr_ids'] = new_line_data
            vals.update(res)
            voucher_id = voucher_pool.create(cr, uid, vals, context=context)
            test = wf_service.trg_validate(uid, 'account.voucher', voucher_id, 'proforma_voucher', cr)
            voucher_ids.append(voucher_id)
        return {'type': 'ir.actions.act_window_close'}
    
account_journal_select()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: