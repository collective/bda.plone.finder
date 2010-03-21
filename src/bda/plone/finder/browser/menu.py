# -*- coding: utf-8 -*-
from zope.component import getUtility
from zope.app.publisher.interfaces.browser import IBrowserMenu
from Acquisition import aq_inner
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone import PloneMessageFactory as _
from plone.app.contentmenu.interfaces import IContentMenuItem
from bda.plone.finder.browser.dispatcher import AjaxContext

class AddItemsMenu(AjaxContext):
    
    __call__ = ViewPageTemplateFile(u'templates/dropdown.pt')
    
    @property
    def noitems(self):
        return _('Nothing to add')
    
    @property
    def items(self):
        menu = getUtility(IBrowserMenu, name=u'plone_contentmenu_factory')
        ret = list()
        for item in menu.getMenuItems(self.current_context, self.request):
            ret.append({
                'title': item['title'],
                'url': item['action'],
                'style': 'background:url(\'' + item['icon'] + '\') no-repeat;',
            })
        return ret