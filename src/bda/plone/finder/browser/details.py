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

class ATDetails(Details):
    
    details = ViewPageTemplateFile('templates/at_details.pt')
    
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
        return u''
    
    def _date(self, date):
        if date.year() < 1900 or date.year() > 2400:
            return _(u'undefined')
        return self.toLocalizedTime(date, long_format=1)

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

class ActionDetails(PloneDetails):
    
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
    def _action(self):
        return self._action_by_id(self._group, self.uid[14:])
    
    @property
    def _group(self):
        if self.uid[14:] in self._cp_actions:
            return 'Plone'
        if self.uid[14:] in self._ac_actions:
            return 'Products'
        raise ValueError(_(u'unknown UID'))
    
    @property
    def _cp_actions(self):
        return [i['id'] for i in self._actions_by_group('Plone')]
    
    @property
    def _ac_actions(self):
        return [i['id'] for i in self._actions_by_group('Products')]
    
    def _action_by_id(self, group, id):
        for item in self._actions_by_group(group):
            if item['id'] == id:
                return item
    
    def _actions_by_group(self, group):
        context = self.context
        return context.portal_controlpanel.enumConfiglets(group=group)