# -*- coding: utf-8 -*-
import simplejson as json
from zope.interface import (
    implements,
    directlyProvides,
    noLongerProvides,
)
from zope.component import (
    getAdapter,
    getMultiAdapter,
)
from zope.component.interfaces import ComponentLookupError
from ZODB.POSException import ConflictError
from OFS.CopySupport import CopyError
from AccessControl import (
    getSecurityManager,
    Unauthorized,
)
from Acquisition import (
    aq_inner,
    aq_parent,
)
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.memoize.instance import memoize
from plone.app.layout.viewlets.common import ViewletBase
from plone.app.layout.icons.interfaces import IContentIcon
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFPlone.utils import (
    typesToList,
    transaction_note,
    safe_unicode,
)
from Products.Archetypes.interfaces import IBaseFolder
from bda.plone.finder.interfaces import (
    IPloneRoot,
    IPloneContent,
    IPloneControlPanel,
    IPloneAddons,
    IPloneAction,
    IActionExecution,
)

class OverlayViewlet(ViewletBase):
    
    render = ViewPageTemplateFile('templates/overlay.pt')
    
    def update(self):
        user = getSecurityManager().getUser()
        self.show = not user.has_role('Anonymous')

class Finder(BrowserView):
    
    __call__ = ViewPageTemplateFile('templates/finder.pt')
    
    @property
    def columns(self):
        ret = list()
        for obj in self._next_parent:
            ret.append(obj.restrictedTraverse('finder_column'))
        ret.reverse()
        while len(ret) < 4:
            ret.append('<div>&nbsp;</div>')
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
              and IBaseFolder.providedBy(child):
                directlyProvides(context, IPloneContent)
                yield context
                noLongerProvides(context, IPloneContent)
        yield context