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
import decimal_precision as dp

class account_bank_statement(osv.osv):
    _inherit = 'account.bank.statement'
    _columns = {
                'curr_rate': fields.related('journal_id', 'curr_rate', type="float"),
                'comp_curr_rate': fields.related('journal_id', 'comp_curr_rate', type="float")
                }
account_bank_statement()

class acount_bank_statement_line(osv.osv):
    _inherit = 'account.bank.statement.line'
    _columns = {
                'amount': fields.float('Amount'),
#                'amount': fields.float('Amount', digits_compute=dp.get_precision('Account')),
                }
    
account_bank_statement()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: