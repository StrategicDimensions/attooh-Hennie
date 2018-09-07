# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.http import request

from odoo.addons.portal.controllers.portal import get_records_pager, CustomerPortal, pager as portal_pager

class CustomerPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        Event = request.env['calendar.event']
        values['meeting_count'] = Event.sudo().search_count([('user_id', '=', request.env.user.id)])
        return values

    @http.route(['/my/meetings', '/my/meetings/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_meetings(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        Event = request.env['calendar.event']
        domain = [('user_id', '=', request.env.user.id)]

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'name'},
        }
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        # archive groups - Default Group By 'create_date'
        archive_groups = self._get_archive_groups('calendar.event', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]
        # meetings count
        meeting_count = Event.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/meetings",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=meeting_count,
            page=page,
            step=self._items_per_page
        )

        # TODO: TurboG(me) can we remove sodo and handle it with access rule ??
        meetings = Event.sudo().search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_meeting_history'] = meetings.ids[:100]

        values.update({
            'date': date_begin,
            'date_end': date_end,
            'meetings': meetings,
            'page_name': 'meetings',
            'archive_groups': archive_groups,
            'default_url': '/my/meetings',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby
        })
        return request.render("crm_attooh.portal_my_meetings", values)

    def has_meeting_access(self, meeting_id):
        meetings = request.env['calendar.event'].sudo().search([('user_id', '=', request.env.user.id)])
        return meeting_id in meetings.ids and True or False

    @http.route(['/my/meeting/<int:meeting_id>'], type='http', auth="user", website=True)
    def portal_my_meeting(self, meeting_id=None, **kw):
        if self.has_meeting_access(meeting_id):
            meeting = request.env['calendar.event'].sudo().browse(meeting_id)
            vals = {'meeting': meeting}
            history = request.session.get('my_meeting_history', [])
            vals.update(get_records_pager(history, meeting))
            return request.render("crm_attooh.portal_my_meeting", vals)
        return request.redirect('/my')
