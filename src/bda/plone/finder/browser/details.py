# -*- coding: utf-8 -*-
from zope.interface import implements
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.memoize.instance import memoize
from AccessControl import Unauthorized
from Products.CMFPlone import PloneMessageFactory as _
from bda.plone.finder.interfaces import IColumn
from bda.plone.finder.browser.utils import (
    col_id,
    anon,
    ControlPanelItems,
)

DETAILS = """
<div id="%(id)s"
     class="finder_column">
  %(details)s
</div>
"""

DETAILS_CONTENT = """
<ul>
  <li>
    <strong>%(text)s</strong>
  </li>
</ul>
"""

class Details(BrowserView):
    """Details base. Used as fallback.
    """
    
    implements(IColumn)
    
    def __call__(self):
        if anon():
            raise Unauthorized, u'Not authenticated'
        return DETAILS % {
            'id': self.uid,
            'details': self.details(),
        }
    
    @property
    def uid(self):
        return col_id(self.request.get('uid'))
    
    def details(self):
        return DETAILS_CONTENT % {
            'text': _(u'No Details.'),
        }
    
    @memoize
    def toLocalizedTime(self, time, long_format=None, time_only = None):
        util = self.context.translation_service
        try:
            return util.ulocalized_time(time,
                                        long_format,
                                        time_only,
                                        self.context,
                                        domain='plonelocales')
        except TypeError, e:
            return util.ulocalized_time(time,
                                        long_format,
                                        self.context,
                                        domain='plonelocales')

class DefaultDetails(Details):
    
    details = ViewPageTemplateFile('templates/default_details.pt')
    preview_template = None
    
    @property
    def uid(self):
        return col_id(self.context.UID())
    
    @property
    def type(self):
        return _(self.context.portal_type)
    
    @property
    def size(self):
        return self.context.getObjSize()
    
    @property
    def state(self):
        catalog = self.context.portal_catalog
        return _(catalog(UID=self.context.UID())[0].review_state)
    
    @property
    def created(self):
        return self._date(self.context.created())
    
    @property
    def modified(self):
        return self.toLocalizedTime(self.context.ModificationDate(),
                                   long_format=1)
    
    @property
    def effective(self):
        return self._date(self.context.effective())
    
    @property
    def expires(self):
        return self._date(self.context.expires())
    
    @property
    def author(self):
        return self.context.Creator()
    
    @property
    def preview(self):
        if self.preview_template is None:
            return u''
        return self.preview_template()
    
    def _date(self, date):
        if date.year() < 1900 or date.year() > 2400:
            return _(u'undefined')
        return self.toLocalizedTime(date, long_format=1)

class ATImageDetails(DefaultDetails):
    
    preview_template = ViewPageTemplateFile('templates/image_preview.pt')

class ATEventDetails(DefaultDetails):
    
    preview_template = ViewPageTemplateFile('templates/event_preview.pt')
    
    @property
    def startDate(self):
        return self._date(self.context.start())
    
    @property
    def endDate(self):
        return self._date(self.context.end())
    
    @property
    def location(self):
        return self.context.getLocation()
    
    @property
    def attendees(self):
        return self.context.getAttendees()
    
    @property
    def eventUrl(self):
        return self.context.event_url()
    
    @property
    def contactName(self):
        return self.context.contact_name()
    
    @property
    def contactEmail(self):
        return self.context.contact_email()
    
    @property
    def contactPhone(self):
        return self.context.contact_phone()

class PloneDetails(Details):
    
    details = ViewPageTemplateFile('templates/plone_details.pt')
    
    @property
    def title(self):
        return self._pprop('title')
    
    @property
    def description(self):
        return self._pobj.Description()
        
    @property
    def link(self):
        return self._url()
    
    @property
    def _pobj(self):
        if not hasattr(self, '_pobj_'):
            self._pobj_ = self.context.portal_url.getPortalObject()
        return self._pobj_
    
    def _url(self, resource=None):
        if resource:
            return u'%s/%s' % (self._pobj.absolute_url(), resource)
        return self._pobj.absolute_url()
    
    def _pprop(self, name):
        return getattr(self._pobj, name, None)

class ContentDetails(PloneDetails): pass

class ControlPanelDetails(PloneDetails):
    
    @property
    def title(self):
        return _(u'Website-Configuration')
    
    @property
    def description(self):
        return _(u'Configuration Area for Plone')
        
    @property
    def link(self):
        return self._url(resource=u'plone_control_panel')
    
class AddOnDetails(PloneDetails):
    
    @property
    def title(self):
        return _(u'Add-On-Configuration')
    
    @property
    def description(self):
        return _(u'Configuration Area for Add-On Products')
        
    @property
    def link(self):
        return self._url(resource=u'plone_control_panel')

class PloneConfigItem(PloneDetails):
    
    @property
    def title(self):
        self._action
        return self._action['title']
    
    @property
    def description(self):
        return self._action['description']
        
    @property
    def link(self):
        return self._action['url']
    
    @property
    def _raw_uid(self):
        return self.uid[14:]
    
    @property
    def _action(self):
        cp_items = ControlPanelItems(self.context)
        return cp_items.item_by_id(self._raw_uid, groups=[self._group])
    
    @property
    def _group(self):
        if self._raw_uid in self._cp_actions:
            return 'Plone'
        if self._raw_uid in self._ac_actions:
            return 'Products'
        raise ValueError(_(u'unknown UID'))
    
    @property
    def _cp_actions(self):
        cp_items = ControlPanelItems(self.context)
        return [i['id'] for i in cp_items.items_by_group('Plone')]
    
    @property
    def _ac_actions(self):
        cp_items = ControlPanelItems(self.context)
        return [i['id'] for i in cp_items.items_by_group('Products')]