# -*- coding: utf-8 -*-

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
    return {
        'uid': uid,
        'icon': icon,
        'title': title,
        'is_folderish': folderish,
        'selected': selected,
        'state': state,
        'cut': cut,
    }