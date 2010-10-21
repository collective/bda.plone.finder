# -*- coding: utf-8 -*-
from zope.interface import Interface
from zope.interface import Attribute

###############################################################################
# Finder browser layer
###############################################################################

class IFinderLayer(Interface):
    """Browser layer for bda.plone.finder.
    """

###############################################################################
# Finder column provider interface
###############################################################################

class IColumnProvider(Interface):
    """Interface for providing and rendering finder columns.
    """
    
    flavor = Attribute(u"Finder flavor this object provides context for.")
    
    def provides(uid):
        """Return Flag wether context by uid is provided by this object.
        """
    
    def get(uid):
        """Return current context for column rendering.
        """
    
    def render(uid, view):
        """
        """
    
    def rendered_columns(uid):
        """
        """

###############################################################################
# Finder view interfaces
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
# Finder action interface
###############################################################################

class IAction(Interface):
    """Action adapter interface.
    
    Must be registered as multi adapter for context and request with action
    id as name.
    """
    
    flavor = Attribute(u"Finder flavor this action is provided for.")
    
    title = Attribute(u"Action title")
    
    order = Attribute(u"Integer defining action position.")
    
    group = Attribute(u"Integer for visually grouping actions.")
    
    dropdown = Attribute(u"Flag wether dropdown ul should be rendered for "
                         u"this action or not.")
    
    enabled = Attribute(u"Flag wether action is enabled or not")
    
    url = Attribute(u"URL of action")
    
    ajax = Attribute(u"Flag wether action is performed via AJAX or not."
                     u"Note - Non AJAX actions always follow ``url``")
    
    def __call__():
        """Execute action. Return message. and UID as tuple.
        """

###############################################################################
# Finder root marker
###############################################################################

class IFinderRoot(Interface):
    """Marker interface for finder root object.
    """

###############################################################################
# Finder column markers
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

class IPloneConfigItem(Interface):
    """Marker interface for plone configuration items.
    """

class IPloneAction(Interface):
    """Marker interface for plone actions column.
    
    XXX: remove
    """