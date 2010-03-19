# -*- coding: utf-8 -*-
from zope.component import getMultiAdapter
from Acquisition import aq_inner
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.icons.interfaces import IContentIcon
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.utils import typesToList
from batch import Batch
from utils import (
    col_id,
    item_id,
    nav_item,
)

class Column(BrowserView):
    
    __call__ = ViewPageTemplateFile('templates/column.pt')
    
    slicesize = 20
    
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
        for brain in brains:
            icon = getMultiAdapter((context, self.request, brain), IContentIcon)
            uid = brain.UID
            cut = self.request.cookies.get('__fct') == uid
            ret.append(nav_item(item_id(uid),
                                icon.url,
                                brain.Title,
                                brain.is_folderish, 
                                self._item_selected(brain.getURL()),
                                brain.review_state,
                                cut))
        self._items = ret
        return ret
    
    @property
    def itemslice(self):
        cur = int(self.request.get('b', 0))
        slicesize = self.slicesize
        return self.items[cur * slicesize:cur * slicesize + slicesize]
    
    @property
    def batch(self):
        b = Batch(aq_inner(self.context), self.request)
        if not hasattr(self, '_batch_vocab'):
            self._batch_vocab = self.batchvocab
        b.vocab = self._batch_vocab
        return b
    
    @property
    def batchvocab(self):
        items = self.items
        count = len(items)
        if count <= self.slicesize:
            return list()
        pagecount = count / self.slicesize
        if count % self.slicesize != 0:
            pagecount += 1
        url = u'?b=%i'
        cur = int(self.request.get('b', 0))
        vocab = list()
        for i in range(pagecount):
            vocab.append({
                'page': str(i + 1),
                'current': cur == i and True or False,
                'visible': True,
                'url': url % i,
            })
        return vocab
    
    def _item_selected(self, url):
        if self.request.get('_skip_selection_check', False):
            return False
        requested = self.request.getURL()[:-17]
        return requested.startswith(url)
    
    def strip_title(self, title):
        if len(title) > 24:
            return '%s...%s' % (title[:10], title[-10:])
        return title

class FolderColumn(Column): pass

class PloneRoot(Column):
    
    @property
    def uid(self):
        return col_id('plone_root')
    
    @property
    def items(self):
        uid = self.request.get('uid', 'plone_root')
        ret = list()
        if self.request.getURL()[:-17] != self.context.absolute_url():
            uid = 'plone_content'
        for id, title, icon in [
                ('plone_content', _('Content'), 'logoIcon.gif'),
                ('plone_control_panel', _('Control Panel'), 'site_icon.gif'),
                ('plone_addons', _('Addon Configuration'), 'product_icon.gif')]:
            ret.append(nav_item(item_id(id),
                                icon,
                                title,
                                True,
                                uid == id and True or False))
        return ret

class PloneContent(Column):
    
    @property
    def uid(self):
        return col_id('plone_content')

class ControlPanelColumn(Column):
    
    def items_by_configlets(self, group):
        ret = list()
        context = self.context
        pu = context.plone_utils
        configlets = context.portal_controlpanel.enumConfiglets(group=group)
        for item in configlets:
            if not item['available'] or not item['allowed']:
                continue
            ret.append(nav_item(item_id(item['id']),
                                pu.getIconFor('controlpanel', item['id']),
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