# -*- coding: utf-8 -*-
from zope.interface import Interface
from zope.interface import Attribute

class IFinderLayer(Interface):
    """Browser layer for bda.plone.finder.
    """

###############################################################################
# Finder View interfaces
###############################################################################

class IFinder(Interface):
    """View interface for finder.
    """
    
    actions = Attribute(u"List of action groups containing ordered action "
                        u"defs.")
    
    columns = Attribute(u"List of rendered columns.")

class IColumn(Interface):
    """View interface for column.
    """
    
    uid = Attribute(u"``finder_column_`` prefixed uid of context.")

class IFolderishColumn(IColumn):
    """View interface for folderish column.
    """
    
    filtereditems = Attribute(u"List of items created by"
                              u"``bda.plone.finder.utils.nav_item``")

###############################################################################
# Finder Column marker interfaces
###############################################################################

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

###############################################################################
# action related interfaces
###############################################################################

class IAction(Interface):
    """Action adapter interface.
    
    Must be registered as adapter for context with action id as name.
    """
    
    title = Attribute(u"Action title")
    
    order = Attribute(u"Integer defining action position.")
    
    group = Attribute(u"Group integer for visually grouping actions.")
    
    dropdown = Attribute(u"Flag wether dropdown ul should be rendered for "
                         u"this action or not.")
    
    enabled = Attribute(u"Flag wether action is enabled or not")
    
    url = Attribute(u"URL of action")
    
    ajax = Attribute(u"Flag wether action is performed via AJAX or not."
                     u"Note - Non AJAX actions always follow ``url``")

class IActionExecution(Interface):
    """Action execution adapter interface for ajax enabled actions.
    
    Must be registered as adapter for context with action id as name.
    """
    
    def __call__(self, request):
        """Execute action. Return message. and UID as tuple.
        """