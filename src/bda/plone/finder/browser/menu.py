# -*- coding: utf-8 -*-
from zope.component import getMultiAdapter
from Acquisition import aq_inner
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.contentmenu.interfaces import IContentMenuItem
from bda.plone.finder.dispatcher import AjaxContext

class AddItemsMenu(AjaxContext):
    
    __call__ = ViewPageTemplateFile(u'templates/dropdown.pt')
    
    @property
    def items(self):
        menu = getMultiAdapter((self.current_context, self.request),
                               IContentMenuItem,
                               name=u'plone.contentmenu.factories')
        
        return list()