# -*- coding: utf-8 -*-
from zope.interface import implements
from zope.component import getAdapters
from Acquisition import (
    aq_inner,
    aq_parent,
)
from AccessControl import getSecurityManager
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from plone.app.layout.navigation.defaultpage import isDefaultPage
from bda.plone.finder.interfaces import (
    IFinder,
    IAction,
)
from bda.plone.finder.browser.utils import (
    anon,
    get_provider,
    ExecutionInfo,
)

class TriggerViewlet(ViewletBase):
    
    render = ViewPageTemplateFile('templates/trigger.pt')
    
    @property
    def show(self):
        sm = getSecurityManager()
        return sm.checkPermission('bda.plone.finder: Trigger Finder',
                                  self.context)

class PathViewlet(ViewletBase, ExecutionInfo):
    
    render = ViewPageTemplateFile('templates/basepath.pt')
    
    def update(self):
        self.show = not anon()
    
    @property
    def base_url(self):
        context = aq_inner(self.context)
        parent = aq_parent(context)
        request_url = self.request['ACTUAL_URL']
        context_url = context.absolute_url()
        if isDefaultPage(parent, context) \
          and not request_url.startswith(context_url):
            context = parent
        return context.absolute_url()

class Finder(BrowserView, ExecutionInfo):
    
    implements(IFinder)
    
    __call__ = ViewPageTemplateFile('templates/finder.pt')
    
    @property
    def show(self):
        return not anon()
    
    @property
    def actions(self):
        flavor = self.flavor
        groups = dict()
        actions = list(getAdapters((self.context, self.request), IAction))
        for id, action in actions:
            if flavor != action.flavor:
                continue
            if not groups.get(action.group):
                groups[action.group] = list()
            groups[action.group].append({
                'id': id,
                'title': action.title,
                'order': action.order,
                'dropdown': action.dropdown,
            })
        ret = list()
        for key in sorted(groups.keys()):
            ret.append(sorted(groups[key],
                        cmp=lambda x, y: x['order'] > y['order'] and 1 or -1))
        return ret
    
    @property
    def columns(self):
        ret = list()
        uid = self.uid
        provider = get_provider(self.context, self.flavor, uid)
        if provider is not None:
            ret = provider.rendered_columns(uid)
        while len(ret) < 4:
            ret.append('<div class="finder_column">&nbsp;</div>')
        return ret