# -*- coding: utf-8 -*-
from AccessControl import getSecurityManager
from Products.Five import BrowserView
from zope.component import (
    getAdapters,
    getUtility,
)
from bda.plone.finder.interfaces import (
    IUidProvider,
    IColumnProvider,
)


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


PLONE_DEFAULT_TYPES = [
    'Document',
    'Event',
    'Folder',
    'Link',
    'News Item',
    'Topic',
    'Image',
    'File',
]


def default_type_css(portal_type):
    if portal_type in PLONE_DEFAULT_TYPES:
        type = portal_type.lower().replace(' ', '-')
        return 'contenttype-%s' % type
    return None


def nav_item(uid,
             icon,
             title,
             folderish=False,
             selected=False,
             state=None,
             cut=False,
             contenttype=None):
    if not isinstance(title, unicode):
        title = title.decode('utf-8')
    tooltip = title
    if len(title) > 19:
        title = u'%s...%s' % (title[:8], title[-8:])
    return {
        'uid': uid,
        'icon': icon,
        'title': title,
        'tooltip': tooltip,
        'is_folderish': folderish,
        'selected': selected,
        'state': state,
        'cut': cut,
        'contenttype': contenttype,
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
        if self.request.get('uid'):
            return self.request['uid']
        uid_provider = getUtility(IUidProvider, name=self.flavor)
        return uid_provider.uid(self.context, self.request)

    @property
    def pobj(self):
        return self.context.portal_url.getPortalObject()


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


class AjaxUtils(BrowserView, ExecutionInfo):

    def review_state(self):
        if anon():
            return
        uid = self.request.get('uid')
        brains = self.context.portal_catalog(UID=uid)
        if not brains:
            return
        return uid + ':' + brains[0].review_state

    def base_url(self):
        if anon():
            return
        uid = self.request.get('uid')
        brains = self.context.portal_catalog(UID=uid)
        if not brains:
            return self.pobj.absolute_url()
        return brains[0].getObject().absolute_url()
