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
from datetime import datetime
from osv import osv, fields
from tools import DEFAULT_SERVER_DATETIME_FORMAT
import pytz
import time

class pos_details(osv.osv_memory):
    _inherit = 'pos.details'
    
    def convert_from_local_datetime(self, cr, uid, date, hour, context=None):
        user_obj = self.pool.get('res.users').browse(cr, uid, uid, context)
        usr_zone = user_obj.context_tz or 'America/Hermosillo'
        zone = pytz.timezone(usr_zone)
        date_original = datetime.strptime(date + ' '+ hour, DEFAULT_SERVER_DATETIME_FORMAT)
        src_dt = zone.localize(date_original)
        date_local = src_dt.astimezone(pytz.utc)
        return date_local.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

    def print_report(self, cr, uid, ids, context=None):
        """
         To get the date and print the report
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param context: A standard dictionary
         @return : retrun report
        """
        res = super(pos_details, self).print_report(cr, uid, ids, context=context)
        date_start = res['datas']['form'].get('date_start', False)
        date_end = res['datas']['form'].get('date_end', False)
        if date_start and date_end:
             res['datas']['form'].update({
                'date_start1': self.convert_from_local_datetime(cr, uid, date_start, '00:00:00'),
                'date_end1': self.convert_from_local_datetime(cr, uid, date_end, '23:59:59')
            })
             res['report_name'] = 'pos.details_inherit'
        return res

pos_details()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: