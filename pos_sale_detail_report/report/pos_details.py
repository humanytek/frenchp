# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2013 SF Soluciones.
#    (sfsoluciones.com)
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
import time
from report import report_sxw
from addons.point_of_sale.report.pos_details import pos_details

class pos_details_inherit(pos_details):
    def _pos_sales_details(self, form):
        #res = super(pos_details_inherit, self)._pos_sales_details(form)
        pos_obj = self.pool.get('pos.order')
        user_obj = self.pool.get('res.users')
        data = []
        result = {}
        user_ids = form['user_ids'] or self._get_all_users()
        company_id = user_obj.browse(self.cr, self.uid, self.uid).company_id.id
        pos_ids = pos_obj.search(self.cr, self.uid, [('date_order','>=',form['date_start1']),('date_order','<=',form['date_end1']),('user_id','in',user_ids),('state','in',['done','paid','invoiced']),('company_id','=',company_id)])
        for pos in pos_obj.browse(self.cr, self.uid, pos_ids):
            for pol in pos.lines:
                result = {
                    'code': pol.product_id.default_code,
                    'name': pol.product_id.name,
                    'invoice_id': pos.invoice_id.id, 
                    'price_unit': pol.price_unit, 
                    'qty': pol.qty, 
                    'discount': pol.discount, 
                    'total': (pol.price_unit * pol.qty * (1 - (pol.discount) / 100.0)), 
                    'date_order': pos.date_order, 
                    'pos_name': pos.name, 
                    'uom': pol.product_id.uom_id.name
                }
                data.append(result)
                self.total += result['total']
                self.qty += result['qty']
                self.discount += result['discount']
        if data:
            return data
        else:
            return {}
    
    def _get_sum_invoice_2(self,form):
        pos_obj = self.pool.get('pos.order')
        user_obj = self.pool.get('res.users')
        user_ids = form['user_ids'] or self._get_all_users()
        company_id = user_obj.browse(self.cr, self.uid, self.uid).company_id.id
        pos_ids = pos_obj.search(self.cr, self.uid, [('date_order','>=',form['date_start1']),('date_order','<=',form['date_end1']),('user_id','in',user_ids),('company_id','=',company_id),('invoice_id','<>',False)])
        for pos in pos_obj.browse(self.cr, self.uid, pos_ids):
            for pol in pos.lines:
                self.total_invoiced += (pol.price_unit * pol.qty * (1 - (pol.discount) / 100.0))
        return self.total_invoiced or False
    
    def _get_payments(self, form):
        statement_line_obj = self.pool.get("account.bank.statement.line")
        pos_order_obj = self.pool.get("pos.order")
        user_ids = form['user_ids'] or self._get_all_users()
        pos_ids = pos_order_obj.search(self.cr, self.uid, [('date_order','>=',form['date_start1']),('date_order','<=',form['date_end1']),('state','in',['paid','invoiced','done']),('user_id','in',user_ids)])
        data={}
        if pos_ids:
            st_line_ids = statement_line_obj.search(self.cr, self.uid, [('pos_statement_id', 'in', pos_ids)])
            if st_line_ids:
                st_id = statement_line_obj.browse(self.cr, self.uid, st_line_ids)
                a_l=[]
                for r in st_id:
                    a_l.append(r['id'])
                self.cr.execute("select aj.name,sum(amount) from account_bank_statement_line as absl,account_bank_statement as abs,account_journal as aj " \
                                "where absl.statement_id = abs.id and abs.journal_id = aj.id  and absl.id IN %s " \
                                "group by aj.name ",(tuple(a_l),))

                data = self.cr.dictfetchall()
                return data
        else:
            return {}
        
    def _get_tax_amount(self, form):
        res = {}
        temp = {}
        list_ids = []
        temp2 = 0.0
        user_ids = form['user_ids'] or self._get_all_users()
        pos_order_obj = self.pool.get('pos.order')
        pos_ids = pos_order_obj.search(self.cr, self.uid, [('date_order','>=',form['date_start1']),('date_order','<=',form['date_end1']),('state','in',['paid','invoiced','done']),('user_id','in',user_ids)])
        temp.update({'name': ''})
        for order in pos_order_obj.browse(self.cr, self.uid, pos_ids):
            temp2 += order.amount_tax
            for line in order.lines:
                if len(line.product_id.taxes_id):
                    tax = line.product_id.taxes_id[0]
                    res[tax.name] = (line.price_unit * line.qty * (1-(line.discount or 0.0) / 100.0)) + (tax.id in list_ids and res[tax.name] or 0)
                    list_ids.append(tax.id)
                    temp.update({'name': tax.name})
        temp.update({'amount': temp2})
        return [temp] or False
report_sxw.report_sxw('report.pos.details_inherit', 'pos.order', 'addons/point_of_sale_singer/report/pos_details.rml', parser=pos_details_inherit, header='internal')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: