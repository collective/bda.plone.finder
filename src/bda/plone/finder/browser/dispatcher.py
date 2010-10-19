# -*- coding: utf-8 -*-
from zope.interface import (
    directlyProvides,
    noLongerProvides,
)
from Acquisition import aq_inner
from Products.Five import BrowserView
from Products.CMFPlone import PloneMessageFactory as _
from bda.plone.finder.interfaces import (
    IPloneRoot,
    IPloneContent,
    IPloneControlPanel,
    IPloneAddons,
    IPloneAction,
)
from bda.plone.finder.browser.folderish import FolderColumn

class AjaxContext(BrowserView):
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
    
    @property
    def current_context(self):
        uid = self.request.get('uid')
        for name in ['plone_content', 'plone_control_panel', 'plone_addons']:
            if uid == name:
                context = self.context.portal_url.getPortalObject()
                return aq_inner(context)
        if uid in self._cp_actions + self._ac_actions:
            context = self.context.portal_url.getPortalObject()
            return aq_inner(context)
        brains = self.context.portal_catalog(UID=uid)
        if not brains:
            return aq_inner(self.context)
        return aq_inner(brains[0].getObject())
    
    @property
    def _cp_actions(self):
        return self._actions_by_group('Plone')
    
    @property
    def _ac_actions(self):
        return self._actions_by_group('Products')
    
    def _actions_by_group(self, group):
        context = self.context
        configlets = context.portal_controlpanel.enumConfiglets(group=group)
        return [item['id'] for item in configlets]

class AjaxColumn(AjaxContext):
    """Class to render a navigation or details column by uid via XML HTTP
    request.
    """
    
    def expandColumn(self):
        self.request['_skip_selection_check'] = True
        return self._render('finder_column')
    
    def detailsColumn(self):
        return self._render('finder_details')
    
    def _render(self, view):
        uid = self.request.get('uid')
        context = self.current_context
        for name, iface in [('plone_content', IPloneContent),
                            ('plone_control_panel', IPloneControlPanel),
                            ('plone_addons', IPloneAddons)]:
            if uid == name:
                return self._render_marked(context, iface, view)
        if uid in self._cp_actions + self._ac_actions:
            return self._render_marked(context, IPloneAction, view)
        if not context:
            return u'<div class="finder_column"></div>'
        return context.restrictedTraverse(view)()
    
    def _render_marked(self, context, iface, view):
        directlyProvides(context, iface)
        rendered = context.restrictedTraverse(view)()
        noLongerProvides(context, iface)
        return rendered

class PloneColumn(FolderColumn):
    """Dispatcher view for IPloneSiteRoot.
    """
    
    def __call__(self):
        uid = self.request.get('uid', 'plone_root')
        for name, iface in [('plone_root', IPloneRoot),
                            ('plone_content', IPloneContent),
                            ('plone_control_panel', IPloneControlPanel),
                            ('plone_addons', IPloneAddons)]:
            if uid == name:
                context = aq_inner(self.context)
                directlyProvides(context, iface)
                rendered = context.restrictedTraverse('finder_column')()
                noLongerProvides(context, iface)
                return rendered
        return u'<div class="finder_column"></div>'