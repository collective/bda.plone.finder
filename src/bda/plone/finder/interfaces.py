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
# Finder common interfaces
###############################################################################

class IUidProvider(Interface):
    """Interface providing uid for initial finder rendering.

    An implementation is registered as utility by flavor name.
    """

    def uid(context, request):
        """Return initial finder uid.
        """


class IColumnProvider(Interface):
    """Interface for providing and rendering finder columns.
    """

    flavor = Attribute(u"Finder flavor this object provides context for.")

    def provides(uid):
        """Return Flag wether context by uid is provided by this object or not.
        """

    def get(uid):
        """Return context by uid.
        """

    def render(uid, view):
        """Render column with context by uid with view.
        """

    def rendered_columns(uid):
        """Render initial finder columns with object by uid as anchor.
        """


###############################################################################
# Finder view interfaces
###############################################################################

class IFinder(Interface):
    """View interface for finder.
    """

    show = Attribute(u"Flag wether to dispay finder or not.")

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
# Finder actions related interfaces
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


class IDropdown(Interface):

    show = Attribute(u"Flag wether to display dropdown or not")

    noitems = Attribute(u"Text to be displyed if dropdown has no items.")

    items = Attribute(u"List of dicts with keys ``title``, ``url`` and "
                      u"``style``.")


###############################################################################
# Finder root context marker
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
