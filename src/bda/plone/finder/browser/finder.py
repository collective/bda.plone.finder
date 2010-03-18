# -*- coding: utf-8 -*-
import simplejson as json
from zope.interface import (
    implements,
    directlyProvides,
    noLongerProvides,
)
from zope.component import (
    getAdapter,
    getMultiAdapter,
)
from zope.component.interfaces import ComponentLookupError
from ZODB.POSException import ConflictError
from OFS.CopySupport import CopyError
from AccessControl import (
    getSecurityManager,
    Unauthorized,
)
from Acquisition import (
    aq_inner,
    aq_parent,
)
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.memoize.instance import memoize
from plone.app.layout.viewlets.common import ViewletBase
from plone.app.layout.icons.interfaces import IContentIcon
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFPlone.utils import (
    typesToList,
    transaction_note,
    safe_unicode,
)
from Products.Archetypes.interfaces import IBaseFolder
from bda.plone.finder.interfaces import (
    IPloneRoot,
    IPloneContent,
    IPloneControlPanel,
    IPloneAddons,
    IPloneAction,
    IActionExecution,
)

class OverlayViewlet(ViewletBase):
    
    render = ViewPageTemplateFile('templates/overlay.pt')
    
    def update(self):
        user = getSecurityManager().getUser()
        self.show = not user.has_role('Anonymous')

class Finder(BrowserView):
    
    __call__ = ViewPageTemplateFile('templates/finder.pt')
    
    @property
    def columns(self):
        ret = list()
        for obj in self._next_parent:
            ret.append(obj.restrictedTraverse('finder_column'))
        ret.reverse()
        while len(ret) < 4:
            ret.append('<div>&nbsp;</div>')
        return ret
    
    @property
    def _next_parent(self):
        context = aq_inner(self.context)
        while not IPloneSiteRoot.providedBy(context):
            toadapt = (context, self.request)
            state = getMultiAdapter(toadapt, name=u'plone_context_state')
            if state.is_default_page():
                context = aq_parent(context)
            yield context
            child = context
            context = aq_parent(aq_inner(context))
            if IPloneSiteRoot.providedBy(context) \
              and IBaseFolder.providedBy(child):
                directlyProvides(context, IPloneContent)
                yield context
                noLongerProvides(context, IPloneContent)
        yield context

class AjaxColumn(BrowserView):
    """Class to render a nav or details column by uid via XML HTTP request.
    """
    
    def expandColumn(self):
        self.request['_skip_selection_check'] = True
        return self._render('finder_column')
    
    def detailsColumn(self):
        return self._render('finder_details')
    
    def _render(self, view):
        uid = self.request.get('uid')
        for name, iface in [('plone_content', IPloneContent),
                            ('plone_control_panel', IPloneControlPanel),
                            ('plone_addons', IPloneAddons)]:
            if uid == name:
                context = self.context.portal_url.getPortalObject()
                return self._render_marked(context, iface, view)
        if uid in self._cp_actions + self._ac_actions:
            context = self.context.portal_url.getPortalObject()
            return self._render_marked(context, IPloneAction, view)
        brains = self.context.portal_catalog(UID=uid)
        if not brains:
            return u'<div>%s</div>' % _(u'Unknown Column')
        return brains[0].getObject().restrictedTraverse(view)()
    
    def _render_marked(self, context, iface, view):
        context = aq_inner(context)
        directlyProvides(context, iface)
        rendered = context.restrictedTraverse(view)()
        noLongerProvides(context, iface)
        return rendered
    
    @property
    def _cp_actions(self):
        return self._actions_by_group('Plone')
    
    @property
    def _ac_actions(self):
        return self._actions_by_group('Products')
    
    def _actions_by_group(self, group):
        context = self.context
        configlets = context.portal_controlpanel.enumConfiglets(group=group)
        return [item['id'] for item in configlets]

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

DETAILS = """
<div id="%(id)s">
  %(details)s
</div>
"""

DETAILS_CONTENT = """
<ul>
  <li>
    <strong>%(text)s</strong>
  </li>
</ul>
"""

class Details(BrowserView):
    """Details base. Used as fallback.
    """
    
    def __call__(self):
        return DETAILS % {
            'id': self.uid,
            'details': self.details(),
        }
    
    @property
    def uid(self):
        return col_id(self.request.get('uid'))
    
    def details(self):
        return DETAILS_CONTENT % {
            'text': _(u'No Details.'),
        }
    
    @memoize
    def toLocalizedTime(self, time, long_format=None, time_only = None):
        util = self.context.translation_service
        try:
            return util.ulocalized_time(time,
                                        long_format,
                                        time_only,
                                        self.context,
                                        domain='plonelocales')
        except TypeError, e:
            return util.ulocalized_time(time,
                                        long_format,
                                        self.context,
                                        domain='plonelocales')

class ATDetails(Details):
    
    details = ViewPageTemplateFile('templates/at_details.pt')
    
    @property
    def type(self):
        return _(self.context.portal_type)
    
    @property
    def size(self):
        return self.context.getObjSize()
    
    @property
    def state(self):
        catalog = self.context.portal_catalog
        return _(catalog(UID=self.context.UID())[0].review_state)
    
    @property
    def created(self):
        return self._date(self.context.created())
    
    @property
    def modified(self):
        return self.toLocalizedTime(self.context.ModificationDate(),
                                   long_format=1)
    
    @property
    def effective(self):
        return self._date(self.context.effective())
    
    @property
    def expires(self):
        return self._date(self.context.expires())
    
    @property
    def author(self):
        return self.context.Creator()
    
    @property
    def preview(self):
        return u''
    
    def _date(self, date):
        if date.year() < 1900 or date.year() > 2400:
            return _(u'undefined')
        return self.toLocalizedTime(date, long_format=1)

class PloneDetails(Details):
    
    details = ViewPageTemplateFile('templates/plone_details.pt')
    
    @property
    def title(self):
        return self._pprop('title')
    
    @property
    def description(self):
        return self._pobj.Description()
        
    @property
    def link(self):
        return self._url()
    
    @property
    def _pobj(self):
        if not hasattr(self, '_pobj_'):
            self._pobj_ = self.context.portal_url.getPortalObject()
        return self._pobj_
    
    def _url(self, resource=None):
        if resource:
            return u'%s/%s' % (self._pobj.absolute_url(), resource)
        return self._pobj.absolute_url()
    
    def _pprop(self, name):
        return getattr(self._pobj, name, None)

class ContentDetails(PloneDetails): pass

class ControlPanelDetails(PloneDetails):
    
    @property
    def title(self):
        return _(u'Website-Configuration')
    
    @property
    def description(self):
        return _(u'Configuration Area for Plone')
        
    @property
    def link(self):
        return self._url(resource=u'plone_control_panel')
    
class AddOnDetails(PloneDetails):
    
    @property
    def title(self):
        return _(u'Add-On-Configuration')
    
    @property
    def description(self):
        return _(u'Configuration Area for Add-On Products')
        
    @property
    def link(self):
        return self._url(resource=u'plone_control_panel')

class ActionDetails(PloneDetails):
    
    @property
    def title(self):
        self._action
        return self._action['title']
    
    @property
    def description(self):
        return self._action['description']
        
    @property
    def link(self):
        return self._action['url']
    
    @property
    def _action(self):
        return self._action_by_id(self._group, self.uid[14:])
    
    @property
    def _group(self):
        if self.uid[14:] in self._cp_actions:
            return 'Plone'
        if self.uid[14:] in self._ac_actions:
            return 'Products'
        raise ValueError(_(u'unknown UID'))
    
    @property
    def _cp_actions(self):
        return [i['id'] for i in self._actions_by_group('Plone')]
    
    @property
    def _ac_actions(self):
        return [i['id'] for i in self._actions_by_group('Products')]
    
    def _action_by_id(self, group, id):
        for item in self._actions_by_group(group):
            if item['id'] == id:
                return item
    
    def _actions_by_group(self, group):
        context = self.context
        return context.portal_controlpanel.enumConfiglets(group=group)

class Column(BrowserView):
    
    __call__ = ViewPageTemplateFile('templates/column.pt')
    
    @property
    def uid(self):
        return col_id(self.context.UID())
    
    @property
    def items(self):
        ret = list()
        context = aq_inner(self.context)
        brains = self.context.portal_catalog({
            'portal_type': typesToList(self.context),
            'sort_on': 'getObjPositionInParent',
            'path': {
                'query': '/'.join(self.context.getPhysicalPath()),
                'depth': 1,
            },
        })
        for brain in brains:
            icon = getMultiAdapter((context, self.request, brain), IContentIcon)
            uid = brain.UID
            cut = self.request.cookies.get('__fct') == uid
            ret.append(nav_item(item_id(uid),
                                icon.url,
                                brain.Title,
                                brain.is_folderish, 
                                self._item_selected(brain.getURL()),
                                brain.review_state,
                                cut))
        return ret
    
    def _item_selected(self, url):
        if self.request.get('_skip_selection_check', False):
            return False
        requested = self.request.getURL()[:-17]
        return requested.startswith(url)
    
    def strip_title(self, title):
        if len(title) > 24:
            return '%s...%s' % (title[:10], title[-10:])
        return title

class FolderColumn(Column): pass

class PloneColumn(Column):
    """Dispatcher view for IPloneSiteRoot.
    """
    
    def __call__(self):
        uid = self.request.get('uid', 'plone_root')
        for name, iface in [('plone_root', IPloneRoot),
                            ('plone_content', IPloneContent),
                            ('plone_control_panel', IPloneControlPanel),
                            ('plone_addons', IPloneAddons)]:
            if uid == name:
                context = aq_inner(self.context)
                directlyProvides(context, iface)
                rendered = context.restrictedTraverse('finder_column')()
                noLongerProvides(context, iface)
                return rendered
        return u'<div>%s</div>' % _(u'Unknown Column')

class PloneRoot(Column):
    
    @property
    def uid(self):
        return col_id('plone_root')
    
    @property
    def items(self):
        uid = self.request.get('uid', 'plone_root')
        ret = list()
        if self.request.getURL()[:-17] != self.context.absolute_url():
            uid = 'plone_content'
        for id, title, icon in [
                ('plone_content', _('Content'), 'logoIcon.gif'),
                ('plone_control_panel', _('Control Panel'), 'site_icon.gif'),
                ('plone_addons', _('Addon Configuration'), 'product_icon.gif')]:
            ret.append(nav_item(item_id(id),
                                icon,
                                title,
                                True,
                                uid == id and True or False))
        return ret

class PloneContent(Column):
    
    @property
    def uid(self):
        return col_id('plone_content')

class ControlPanelColumn(Column):
    
    def items_by_configlets(self, group):
        ret = list()
        context = self.context
        pu = context.plone_utils
        configlets = context.portal_controlpanel.enumConfiglets(group=group)
        for item in configlets:
            if not item['available'] or not item['allowed']:
                continue
            ret.append(nav_item(item_id(item['id']),
                                pu.getIconFor('controlpanel', item['id']),
                                item['title'],
                                False,
                                False)) # XXX selected.
        return ret

class PloneControlPanel(ControlPanelColumn):
    
    @property
    def uid(self):
        return col_id('plone_control_panel')
    
    @property
    def items(self):
        return self.items_by_configlets('Plone')

class PloneAddons(ControlPanelColumn):
    
    @property
    def uid(self):
        return col_id('plone_addons')
    
    @property
    def items(self):
        return self.items_by_configlets('Products')

class Item(BrowserView):
    
    __call__ = ViewPageTemplateFile('templates/item.pt')
    
    @property
    def itembrain(self):
        uid = self.request.get('uid')
        return self.context.portal_catalog(UID=uid)[0]
    
    @property
    def uid(self):
        return col_id(self.request.get('uid'))
    
    @property
    def item(self):
        toadapt = (self.context,self.request, self.itembrain)
        icon = getMultiAdapter(toadapt, IContentIcon)
        return nav_item(item_id(self.itembrain.UID), 
                        icon.url,
                        self.itembrain.Title,
                        self.itembrain.is_folderish, 
                        False,
                        self.itembrain.review_state)

class Actions(BrowserView):
    
    def actionInfo(self):
        data = dict()
        for name in ['action_view', 'action_edit']:
            data[name] = self._create_action()
        for name in ['action_cut',
                     'action_copy',
                     'action_paste',
                     'action_delete']:
            data[name] = self._create_action(ajax=True)
        uid = self.request.get('uid')
        if not uid:
            return json.dumps(data)
        brains = self.context.portal_catalog(UID=uid)
        if not brains:
            self._set_special_action_url(uid, data)
            return json.dumps(data)
        for name in ['action_cut',
                     'action_copy',
                     'action_paste',
                     'action_delete']:
            data[name]['enabled'] = True
        url = brains[0].getURL()
        data['action_view']['url'] = url
        data['action_view']['enabled'] = True
        data['action_edit']['url'] = '%s/edit' % url
        data['action_edit']['enabled'] = True
        return json.dumps(data)
    
    def execute(self):
        name = self.request.get(u'name', u'')
        uid = self.request.get(u'uid', u'')
        brains = self.context.portal_catalog(UID=uid)
        if not brains:
            return json.dumps(_(u'Object not found. Could not continue.'))
        context = brains[0].getObject()
        err = False
        ret_uid = None
        try:
            execution = getAdapter(context, IActionExecution, name=name)
            msg, ret_uid = execution(self.request)
            if ret_uid is None:
                ret_uid = uid
        except ComponentLookupError, e:
            err = True
            msg = 'No such action: %s for %s.' % (name, uid)
        except Exception, e:
            err = True
            msg = str(e)
        ret = {
            'err': err,
            'msg': msg,
            'uid': ret_uid,
        }
        return json.dumps(ret)
    
    def _create_action(self, enabled=False, url='', ajax=False):
        return {
            'enabled': enabled,
            'url': url,
            'ajax': ajax,
        }
    
    def _set_special_action_url(self, uid, data):
        action = self._action_by_id(uid)
        if action:
            data['action_view']['enabled'] = True
            data['action_view']['url'] = action['url']
        if uid in ['plone_content',
                   'plone_control_panel',
                   'plone_addons']:
            data['action_view']['enabled'] = True
            data['action_view']['url'] = \
                self.context.portal_url.getPortalObject().absolute_url()
            if uid in ['plone_control_panel',
                       'plone_addons']:
                data['action_view']['url'] += '/plone_control_panel'
        return data
    
    @property
    def _actions(self):
        return [i['id'] for i in self._actions_by_group('Plone')] + \
               [i['id'] for i in self._actions_by_group('Products')]
    
    def _action_by_id(self, id):
        for group in ['Plone', 'Products']:
            for item in self._actions_by_group(group):
                if item['id'] == id:
                    return item
    
    def _actions_by_group(self, group):
        context = self.context
        return context.portal_controlpanel.enumConfiglets(group=group)

class ActionExecution(object):
    
    implements(IActionExecution)
    
    def __init__(self, context):
        self.context = context
    
    def __call__(self, request):
        raise NotImplementedError(u'Abstract ActionExecution does not ',
                                  u'implement ``__call__``.')

class CutAction(ActionExecution):
    
    def __call__(self, request):
        context = self.context
        title = safe_unicode(context.title_or_id())
        mtool = context.portal_membership
        if not mtool.checkPermission('Copy or Move', context):
            #msg = _(u'Permission denied to cut ${title}.',
            #        mapping={u'title' : title})
            msg = u'Permission denied to cut %s.' % title
            raise Unauthorized, msg
        try:
            lock_info = context.restrictedTraverse('plone_lock_info')
        except AttributeError:
            lock_info = None
        if lock_info is not None and lock_info.is_locked():
            #msg = _(u'${title} is locked and cannot be cut.',
            #        mapping={u'title' : title})
            msg = u'%s is locked and cannot be cut.' % title
            raise Exception, msg
        parent = aq_parent(aq_inner(context))
        try:
            parent.manage_cutObjects(context.getId(), request)
        except CopyError:
            #msg = _(u'${title} is not moveable.',
            #        mapping={u'title' : title})
            msg = u'%s is not moveable.' % title
            raise Exception, msg
        request.response.setCookie('__fct', self.context.UID(), path='/')
        #msg = _(u'${title} cut.', mapping={u'title' : title})
        msg = u'%s cut.' % title
        transaction_note('Cut object %s' % context.absolute_url())
        return msg, None

class CopyAction(ActionExecution):
    
    def __call__(self, request):
        context = self.context
        title = safe_unicode(context.title_or_id())
        mtool = context.portal_membership
        if not mtool.checkPermission('Copy or Move', context):
            #msg = _(u'Permission denied to copy ${title}.',
            #        mapping={u'title' : title})
            msg = u'Permission denied to copy %s.' % title
            raise Unauthorized, msg
        parent = aq_parent(aq_inner(context))
        try:
            parent.manage_copyObjects(context.getId(), request)
        except CopyError:
            #msg = _(u'${title} is not copyable.',
            #        mapping={u'title' : title})
            msg = u'%s is not copyable.' % title
            raise Exception, msg
        #msg = _(u'${title} copied.',
        #        mapping={u'title' : title})
        msg = u'%s copied.' % title
        transaction_note('Copied object %s' % context.absolute_url())
        return msg, None

class PasteAction(ActionExecution):
    
    def __call__(self, request):
        context = self.context
        msg = _(u'Copy or cut one or more items to paste.')
        if context.cb_dataValid:
            try:
                context.manage_pasteObjects(request['__cp'])        
                transaction_note(
                    'Pasted content to %s' % (context.absolute_url()))
                request.response.expireCookie('__fct', path='/')
                msg = _(u'Item(s) pasted.')
                return msg, context.objectValues()[-1].UID()
            except ConflictError, e:
                raise e
            except ValueError:
                msg = _(u'Disallowed to paste item(s).')
            except (Unauthorized, 'Unauthorized'):
                msg = _(u'Unauthorized to paste item(s).')
            except: # fallback
                msg = _(u'Paste could not find clipboard content.')
        return msg, None

class DeleteAction(ActionExecution):
    
    def __call__(self, request):
        context = self.context
        parent = context.aq_inner.aq_parent
        title = safe_unicode(context.title_or_id())
        try:
            lock_info = context.restrictedTraverse('@@plone_lock_info')
        except AttributeError:
            lock_info = None
        if lock_info is not None and lock_info.is_locked():
            #msg = _(u'${title} is locked and cannot be deleted.',
            #        mapping={u'title' : title})
            msg = u'%s is locked and cannot be deleted.' % title
            raise Exception(msg)
        else:
            parent.manage_delObjects(context.getId())
            #msg = _(u'${title} has been deleted.', mapping={u'title' : title})
            msg = u'%s has been deleted.' % title
            transaction_note('Deleted %s' % context.absolute_url())
            return msg, None