# -*- coding: utf-8 -*-
from zope.interface import Interface

class IFinderLayer(Interface):
    """Browser layer for bda.plone.finder.
    """

class IPloneRoot(Interface):
    """Marker interface for plone root column.
    """

class IPloneContent(Interface):
    """Marker interface for plone content column.
    """

class IPloneControlPanel(Interface):
    """Marker interface for plone control panel column.
    """

class IPloneAddons(Interface):
    """Marker interface for plone addons column.
    """

class IPloneAction(Interface):
    """Marker interface for plone actions column.
    """

class IActionExecution(Interface):
    """Action execution adapter interface.
    
    Must be registered for context with action name.
    """
    
    def __call__(self, request):
        """Execute action. Return message. and UID as tuple.
        """