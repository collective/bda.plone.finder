# -*- coding: utf-8 -*-
from zope.component import getUtility
from zope.app.publisher.interfaces.browser import IBrowserMenu
from Acquisition import aq_inner
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone import PloneMessageFactory as _
from plone.app.contentmenu.interfaces import IContentMenuItem
from bda.plone.finder.browser.dispatcher import AjaxContext
from bda.plone.finder.browser.utils import anon

class AddItemsMenu(AjaxContext):
    
    __call__ = ViewPageTemplateFile(u'templates/dropdown.pt')
    
    @property
    def show(self):
        return not anon()
    
    @property
    def noitems(self):
        return u'Nothing to add'
    
    @property
    def items(self):
        menu = getUtility(IBrowserMenu, name=u'plone_contentmenu_factory')
        ret = list()
        for item in menu.getMenuItems(self.current_context, self.request):
            icon = item['icon']
            if icon:
                icon = 'background:url(\'' + icon + '\') no-repeat;'
            else:
                icon = 'background:none;'
            ret.append({
                'title': item['title'],
                'url': item['action'],
                'style': icon,
            })
        return ret

class TransitionsMenu(AjaxContext):
    
    __call__ = ViewPageTemplateFile(u'templates/dropdown.pt')
    
    @property
    def show(self):
        return not anon()
    
    @property
    def noitems(self):
        return u'No transitions available'
    
    @property
    def items(self):
        pactions = self.context.portal_actions
        actions = pactions.listFilteredActionsFor(self.current_context)
        ret = list()
        for transition in actions['workflow']:
            ret.append({
                'title': transition['title'],
                'url': transition['url'],
                'style': 'background:none;',
            })
        return ret