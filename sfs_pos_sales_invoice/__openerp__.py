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

{
    'name': 'Point Of Sale- Invoice',
    'version': '2.0',
    'category': 'Point Of Sale',
    'description': """This module generates a single invoice for multiple pos sale orders for a selected customer. """,
    'author': 'SF Soluciones',
    'website': 'sfsoluciones.com',
    'images': [],
    'depends': ['point_of_sale', 'sfs_pos_customization'],
    'init_xml': [],
    'update_xml': [
        'wizard/invoice_view.xml',
        'wizard/invoice_journal_select_view.xml',
        'security/ir.model.access.csv',
        'point_of_sale_view.xml',
        'invoice_view.xml'
                ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
