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

class pos_order(osv.osv):
    _inherit = "pos.order"
    _columns = {
        'refund': fields.boolean('Refund'),
    }
    
    _defaults = {
        'refund': False
    }
    
    def refund(self, cr, uid, ids, context=None):
        res = super(pos_order,self).refund(cr, uid, ids, context=context)
        for rec in self.browse(cr, uid, ids, context=context) :
            if rec.refund :
                refund = False
            else :
                refund= True
            self.write(cr, uid, rec.id, {'refund' : refund}, context=context)
        if 'res_id' in res :
            self.write(cr, uid, res['res_id'], {'refund' : refund}, context=context)
        return res
    
pos_order()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: