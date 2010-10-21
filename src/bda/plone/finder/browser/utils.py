# -*- coding: utf-8 -*-
from AccessControl import getSecurityManager
from zope.component import getAdapters
from bda.plone.finder.interfaces import IColumnProvider

def anon():
    user = getSecurityManager().getUser()
    return user.has_role('Anonymous')

def has_permission(permission, context):
    mtool = context.portal_membership
    if not mtool.checkPermission(permission, context):
        return False
    return True

def col_id(id):
    return 'finder_column_%s' % id

def item_id(id):
    return 'finder_nav_item_%s' % id

def nav_item(uid,
             icon,
             title,
             folderish=False,
             selected=False,
             state=None,
             cut=False):
    if len(title) > 29:
        title = title.decode('utf-8')
        title = '%s...%s' % (title[:12], title[-12:])
    return {
        'uid': uid,
        'icon': icon,
        'title': title,
        'is_folderish': folderish,
        'selected': selected,
        'state': state,
        'cut': cut,
    }

def get_provider(context, flavor, uid):
    ret = list()
    for name, provider in getAdapters((context, ), IColumnProvider):
        if flavor != provider.flavor:
            continue
        if provider.provides(uid):
            return provider
    return None

class ExecutionInfo(object):
    
    @property
    def flavor(self):
        return self.request.get('flavor', 'default')
    
    @property
    def uid(self):
        return self.request.get('uid')

class ControlPanelItems(object):
    
    def __init__(self, context):
        self.context = context
    
    def item_by_id(self, id, groups=['Plone', 'Products']):
        for group in groups:
            for item in self.items_by_group(group):
                if item['id'] == id:
                    return item
    
    def items_by_group(self, group):
        """Group 'Plone' or 'Products'
        """
        return self.context.portal_controlpanel.enumConfiglets(group=group)