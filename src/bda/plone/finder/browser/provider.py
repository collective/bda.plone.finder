from Acquisition import (
    aq_inner,
    aq_parent,
)
from zope.interface import (
    implements,
    directlyProvides,
    noLongerProvides,
)
from zope.component import getMultiAdapter
from Products.Archetypes.interfaces import IBaseContent
from bda.plone.finder.interfaces import (
    IColumnProvider,
    IPloneRoot,
    IPloneContent,
    IPloneControlPanel,
    IPloneAddons,
    IPloneConfigItem,
    IFinderRoot,
)
from bda.plone.finder.browser.utils import ControlPanelItems

class ColumnProvider(object):
    """Abstract column provider.
    """
    implements(IColumnProvider)
    
    flavor = 'default'
    
    def __init__(self, context):
        self.context = context
    
    def provides(self, uid):
        raise NotImplementedError(u'Abstract FinderContext does not ',
                                  u'implement ``provides``.')
    
    def get(self, uid):
        raise NotImplementedError(u'Abstract FinderContext does not ',
                                  u'implement ``get``.')
    
    def render(self, uid, view):
        raise NotImplementedError(u'Abstract FinderContext does not ',
                                  u'implement ``render``.')
    
    def rendered_columns(self, uid):
        raise NotImplementedError(u'Abstract FinderContext does not ',
                                  u'implement ``rendered_columns``.')

class RootProvider(ColumnProvider):
    """Handle finder context for plone root.
    """
    PROVIDED = [
        ('root', IPloneRoot),
        ('plone_content', IPloneContent),
        ('plone_control_panel', IPloneControlPanel),
        ('plone_addons', IPloneAddons),
    ]
    
    def provides(self, uid):
        for name, iface in self.PROVIDED:
            if uid == name:
                return True
        return False
    
    def get(self, uid):
        if self.provides(uid):
            return self.context.portal_url.getPortalObject()
        return None
    
    def render(self, uid, view):
        for name, iface in self.PROVIDED:
            if uid == name:
                context = self.get(uid)
                directlyProvides(context, iface)
                rendered = context.restrictedTraverse(view)()
                noLongerProvides(context, iface)
                return rendered
        return None
    
    def rendered_columns(self, uid):
        ret = list()
        if uid == 'root':
            ret.append(self.render('root', 'finder_column'))
            ret.append(self.render('plone_content', 'finder_column'))
            return ret
        for name, iface in self.PROVIDED:
            if uid == name:
                ret.append(self.render('root', 'finder_column'))
                ret.append(self.render(uid, 'finder_column'))
                break
        return ret

class ControlPanelProvider(ColumnProvider):
    """Handle finder control panel context.
    """
    CONFIGLET_GROUPS = ['Plone']
    PARENT_UID = 'plone_control_panel'
    
    def provides(self, uid):
        cp_items = ControlPanelItems(self.context)
        cp_item = cp_items.item_by_id(uid, groups=self.CONFIGLET_GROUPS)
        if cp_item:
            return True
        return False
    
    def get(self, uid):
        if self.provides(uid):
            return self.context.portal_url.getPortalObject()
        return None
    
    def render(self, uid, view):
        if self.provides(uid):
            context = self.get(uid)
            directlyProvides(context, IPloneConfigItem)
            rendered = context.restrictedTraverse(view)()
            noLongerProvides(context, IPloneConfigItem)
            return rendered
        return None
    
    def rendered_columns(self, uid):
        return [
            RootProvider(self.context).render(self.PARENT_UID,
                                              'finder_column'),
            self.render(uid, 'finder_details'),
        ]

class AddonsProvider(ControlPanelProvider):
    """Handle finder addon configuration context.
    """
    CONFIGLET_GROUPS = ['Products']
    PARENT_UID = 'plone_addons'

class CatalogProvider(ColumnProvider):
    """Handle finder context from portal catalog
    """
    
    def provides(self, uid):
        if len(self.context.portal_catalog(UID=uid)) == 1:
            return True
        return False
    
    def get(self, uid):
        brains = self.context.portal_catalog(UID=uid)
        if brains:
            return brains[0].getObject()
        return None
    
    def render(self, uid, view):
        context = self.get(uid)
        if context is not None:
            return context.restrictedTraverse(view)()
    
    def _render(self, context):
        try:
            ret = context.restrictedTraverse('finder_column')()
        except AttributeError, e:
            ret = context.restrictedTraverse('finder_details')()
        except Exception, e:
            ret = u'<div class="finder_column">%s</div>' % unicode(e)
        return ret
    
    def rendered_columns(self, uid):
        ret = list()
        context = aq_inner(self.get(uid))
        while context is not None and not IFinderRoot.providedBy(context):
            toadapt = (context, context.REQUEST) # XXX REQUEST
            state = getMultiAdapter(toadapt, name=u'plone_context_state')
            if state.is_default_page():
                context = aq_parent(context)
            ret.append(self._render(context))
            child = context
            context = aq_parent(context)
            if IFinderRoot.providedBy(context) \
              and IBaseContent.providedBy(child):
                root = RootProvider(context)
                ret.append(root.render('plone_content', 'finder_column'))
                ret.append(root.render('root', 'finder_column'))
        ret.reverse()
        return ret