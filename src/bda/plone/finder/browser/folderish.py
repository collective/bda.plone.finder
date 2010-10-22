# -*- coding: utf-8 -*-
from zope.interface import implements
from zope.component import getMultiAdapter
from Acquisition import aq_inner
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.icons.interfaces import IContentIcon
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.utils import typesToList
from bda.plone.finder.interfaces import IFolderishColumn
from bda.plone.finder.browser.utils import (
    col_id,
    item_id,
    nav_item,
    has_permission,
    ControlPanelItems,
)

PLONE_DEFAULT_TYPES = [
    'Document',
    'Event',
    'Folder',
    'Link',
    'News Item',
    'Topic',
]

class FolderColumn(BrowserView):
    
    implements(IFolderishColumn)
    
    __call__ = ViewPageTemplateFile('templates/column.pt')
    
    @property
    def uid(self):
        return col_id(self.context.UID())
    
    @property
    def items(self):
        if hasattr(self, '_items'):
            return self._items
        ret = list()
        context = aq_inner(self.context)
        brains = self.context.portal_catalog({
            'portal_type': typesToList(self.context),
            'sort_on': 'getObjPositionInParent',
            'path': {
                'query': '/'.join(self.context.getPhysicalPath()),
                'depth': 1,
            },
        })
        layout = getMultiAdapter((context, self.request), name=u'plone_layout')
        for brain in brains:
            icon = layout.getIcon(brain)
            uid = brain.UID
            cut = self.request.cookies.get('__fct') == uid
            contenttype = None
            if brain.portal_type in PLONE_DEFAULT_TYPES:
                type = brain.portal_type.lower().replace(' ', '-')
                contenttype = 'contenttype-%s' % type
            ret.append(nav_item(item_id(uid),
                                icon.url,
                                brain.Title and brain.Title or brain.id,
                                brain.is_folderish, 
                                self._item_selected(brain.getURL()),
                                brain.review_state,
                                cut,
                                contenttype))
        self._items = ret
        return ret
    
    @property
    def filtereditems(self):
        if hasattr(self, '_filtereditems'):
            return self._filtereditems
        items = self.items
        filter = self.request.get('f', '').lower()
        if not filter:
            return items
        filtered = list()
        for item in items:
            if item['title'].lower().startswith(filter):
                filtered.append(item)
        self._filtereditems = filtered
        return filtered
    
    def _item_selected(self, url):
        if self.request.get('_skip_selection_check', False):
            return False
        requested = self.request.getURL()[:-17]
        return requested.startswith(url)
    
    def strip_title(self, title):
        if len(title) > 24:
            return '%s...%s' % (title[:10], title[-10:])
        return title

class PloneRoot(FolderColumn):
    
    @property
    def uid(self):
        return col_id('root')
    
    @property
    def items(self):
        uid = self.request.get('uid', 'plone_content')
        ret = list()
        if self.request.getURL()[:-17] != self.context.absolute_url():
            uid = 'plone_content'
        items = [
            ('plone_content', _('Content'), 'logoIcon.gif'),
        ]
        if has_permission('Manage portal', self.context):
            items += [
                ('plone_control_panel', _('Control Panel'), 'site_icon.gif'),
                ('plone_addons', _('Addon Configuration'), 'product_icon.gif'),
            ]
        for id, title, icon in items:
            ret.append(nav_item(item_id(id),
                                icon,
                                title,
                                True,
                                uid == id and True or False))
        return ret

class PloneContent(FolderColumn):
    
    @property
    def uid(self):
        return col_id('plone_content')

class ControlPanelColumn(FolderColumn):
    
    def items_by_configlets(self, group):
        ret = list()
        pu = self.context.plone_utils
        cp_items = ControlPanelItems(self.context)
        configlets = cp_items.items_by_group(group)
        for item in configlets:
            if not item['available'] or not item['allowed']:
                continue
            try:
                icon = pu.getIconFor('controlpanel', item['id'])
            except KeyError, e:
                icon = ''
            ret.append(nav_item(item_id(item['id']),
                                icon,
                                item['title'],
                                False,
                                False)) # XXX selected.
        return ret

class PloneControlPanel(ControlPanelColumn):
    
    @property
    def uid(self):
        return col_id('plone_control_panel')
    
    @property
    def items(self):
        return self.items_by_configlets('Plone')

class PloneAddons(ControlPanelColumn):
    
    @property
    def uid(self):
        return col_id('plone_addons')
    
    @property
    def items(self):
        return self.items_by_configlets('Products')