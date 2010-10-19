# -*- coding: utf-8 -*-
from zope.interface import (
    implements,
    directlyProvides,
    noLongerProvides,
)
from zope.component import getMultiAdapter
from AccessControl import getSecurityManager
from Acquisition import (
    aq_inner,
    aq_parent,
)
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.Archetypes.interfaces import IBaseContent
from bda.plone.finder.interfaces import IPloneContent
from bda.plone.finder.interfaces import IFinder

class OverlayViewlet(ViewletBase):
    
    render = ViewPageTemplateFile('templates/overlay.pt')
    
    def update(self):
        user = getSecurityManager().getUser()
        self.show = not user.has_role('Anonymous')
    
    @property
    def base_url(self):
        return self.context.absolute_url()

class Finder(BrowserView):
    
    implements(IFinder)
    
    __call__ = ViewPageTemplateFile('templates/finder.pt')
    
    @property
    def columns(self):
        ret = list()
        for obj in self._next_parent:
            try:
                ret.append(obj.restrictedTraverse('finder_column')())
            except AttributeError, e:
                ret.append(obj.restrictedTraverse('finder_details')())
        ret.reverse()
        if len(ret) == 1:
            self.request['uid'] = 'plone_content'
            ret.append(obj.restrictedTraverse('finder_column')())
        while len(ret) < 4:
            ret.append('<div class="finder_column">&nbsp;</div>')
        return ret
    
    @property
    def _next_parent(self):
        context = aq_inner(self.context)
        while not IPloneSiteRoot.providedBy(context):
            toadapt = (context, self.request)
            state = getMultiAdapter(toadapt, name=u'plone_context_state')
            if state.is_default_page():
                context = aq_parent(context)
            yield context
            child = context
            context = aq_parent(aq_inner(context))
            if IPloneSiteRoot.providedBy(context) \
              and IBaseContent.providedBy(child):
                directlyProvides(context, IPloneContent)
                yield context
                noLongerProvides(context, IPloneContent)
        yield context