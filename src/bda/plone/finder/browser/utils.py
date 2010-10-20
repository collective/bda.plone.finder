# -*- coding: utf-8 -*-
from AccessControl import getSecurityManager

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