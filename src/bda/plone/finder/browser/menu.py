# -*- coding: utf-8 -*-
from zope.interface import implementer
from zope.component import getUtility
from zope.browsermenu.interfaces import IBrowserMenu
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bda.plone.finder.interfaces import IDropdown
from bda.plone.finder.browser.utils import (
    anon,
    get_provider,
    ExecutionInfo,
    default_type_css,
)


@implementer(IDropdown)
class FinderDropdown(BrowserView, ExecutionInfo):
    __call__ = ViewPageTemplateFile(u'templates/dropdown.pt')

    @property
    def show(self):
        return not anon()

    @property
    def noitems(self):
        raise NotImplementedError(u'Abstract FinderDropdown does not ',
                                  u'implement ``noitems``.')

    @property
    def items(self):
        raise NotImplementedError(u'Abstract FinderDropdown does not ',
                                  u'implement ``items``.')


class AddItemsMenu(FinderDropdown):

    @property
    def noitems(self):
        return u'Nothing to add'

    @property
    def items(self):
        ret = list()
        uid = self.uid
        provider = get_provider(self.context, self.flavor, uid)
        if provider is None:
            return ret
        menu = getUtility(IBrowserMenu, name=u'plone_contentmenu_factory')
        for item in menu.getMenuItems(provider.get(uid), self.request):
            css = default_type_css(item.get('id', ''))
            icon = item['icon']
            if icon:
                icon = 'background:url(\'' + icon + '\') no-repeat;'
            else:
                if not css:
                    icon = 'background:none;'
                else:
                    icon = None
            ret.append({
                'title': item['title'],
                'url': item['action'],
                'style': icon,
                'css': css,
            })
        return ret


class TransitionsMenu(FinderDropdown):

    @property
    def noitems(self):
        return u'No transitions available'

    @property
    def items(self):
        ret = list()
        uid = self.uid
        provider = get_provider(self.context, self.flavor, uid)
        if provider is None:
            return ret
        pactions = self.context.portal_actions
        actions = pactions.listFilteredActionsFor(provider.get(uid))
        for transition in actions['workflow']:
            ret.append({
                'title': transition['title'],
                'url': transition['url'],
                'style': 'background:none;',
                'css': None,
            })
        return ret
