# -*- coding: utf-8 -*-
from odoo import http, _
from odoo import fields as odoo_fields
from odoo.http import request
from odoo.addons.portal.controllers.portal import get_records_pager, CustomerPortal, pager as portal_pager

class CustomerPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        values['activity_count'] = len(request.env.user.partner_id.activity_ids)
        return values

    def _get_archive__activity_groups(self, model, domain=None, fields=None, groupby="create_date", order="create_date desc"):
        if not model:
            return []
        if domain is None:
            domain = []
        if fields is None:
            fields = ['name', 'create_date']
        groups = []
        for group in request.env[model].sudo()._read_group_raw(domain, fields=fields, groupby=groupby, orderby=order):
            dates, label = group[groupby]
            date_begin, date_end = dates.split('/')
            groups.append({
                'date_begin': odoo_fields.Date.to_string(odoo_fields.Date.from_string(date_begin)),
                'date_end': odoo_fields.Date.to_string(odoo_fields.Date.from_string(date_end)),
                'name': label,
                'item_count': group[groupby + '_count']
            })
        return groups

    @http.route(['/my/activities', '/my/activities/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_activities(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        Activity = request.env['mail.activity']
        activity_ids = request.env.user.partner_id.activity_ids.ids
        domain = [('id', 'in', activity_ids)]

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'summary': {'label': _('Name'), 'order': 'summary'},
            'date_deadline': {'label': _('Due Date'), 'order': 'date_deadline'},
        }
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        # archive groups - Default Group By 'create_date'
        archive_groups = self._get_archive__activity_groups('mail.activity', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]
        # activitys count
        activity_count = Activity.sudo().search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/activities",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=activity_count,
            page=page,
            step=self._items_per_page
        )

        activities = Activity.sudo().search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_activities_history'] = activities.ids[:100]

        values.update({
            'date': date_begin,
            'date_end': date_end,
            'activities': activities,
            'page_name': 'activities',
            'archive_groups': archive_groups,
            'default_url': '/my/activities',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby
        })
        return request.render("crm_attooh.portal_my_activities", values)

    def has_activity_access(self, activity_id):
        activities = request.env.user.partner_id.activity_ids
        return activity_id in activities.ids and True or False

    @http.route(['/my/activity/<int:activity_id>'], type='http', auth="user", website=True)
    def portal_my_activity(self, activity_id=None, **kw):
        if self.has_activity_access(activity_id):
            activity = request.env['mail.activity'].sudo().browse(activity_id)
            vals = {'activity': activity}
            history = request.session.get('my_activities_history', [])
            vals.update(get_records_pager(history, activity))
            return request.render("crm_attooh.portal_my_activity", vals)
        return request.redirect('/my')
    
    @http.route('/mark_as_done', type='http', auth="public", website=True)
    def mark_as_done(self, **post):
        if post.get('activity_id'):
            activity_id = request.env['mail.activity'].browse(int(post.get('activity_id')))
            activity_id.action_done()
        return request.redirect('/my/activities')
