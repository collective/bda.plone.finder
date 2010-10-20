# -*- coding: utf-8 -*-
import simplejson as json
from zope.interface import implements
from zope.component import getUtility
from zope.component import getAdapter
from zope.component import getAdapters
from zope.component.interfaces import ComponentLookupError
from zope.app.publisher.interfaces.browser import IBrowserMenu
from ZODB.POSException import ConflictError
from OFS.CopySupport import CopyError
from AccessControl import Unauthorized
from Acquisition import (
    aq_inner,
    aq_parent,
)
from Products.Five import BrowserView
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.utils import (
    transaction_note,
    safe_unicode,
)
from bda.plone.finder.interfaces import IAction

class Actions(BrowserView):
    
    def actionInfo(self):
        data = dict()
        actions = list(getAdapters((self.context, self.request), IAction))
        for id, action in actions:
            data[id] = {
                'enabled': action.enabled,
                'url': action.url,
                'ajax': action.ajax,
            }
        return json.dumps(data)
        
        # old
        data = dict()
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
                     'action_delete',
                     'action_change_state',
                     'action_add_item']:
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
        context = self._get_object(uid)
        if not context:
            return json.dumps({
                'err': True,
                'msg': _(u'Object not found. Could not continue.'),
            })
        err = False
        ret_uid = None
        try:
            execution = getAdapter(context, IAction, name=name)
            msg, ret_uid = execution(self.request)
            if ret_uid is None:
                ret_uid = uid
        except ComponentLookupError, e:
            err = True
            msg = 'No such action: %s for %s.' % (name, uid)
        except Exception, e:
            err = True
            msg = str(e)
        return json.dumps({
            'err': err,
            'msg': msg,
            'uid': ret_uid,
        })
    
    def _set_special_action_url(self, uid, data):
        action = self._action_by_id(uid)
        if action:
            data['action_view']['enabled'] = True
            data['action_view']['url'] = action['url']
        if uid in ['plone_content',
                   'plone_control_panel',
                   'plone_addons']:
            purl = self.context.portal_url.getPortalObject().absolute_url()
            data['action_view']['enabled'] = True
            data['action_view']['url'] = purl
            if uid == 'plone_content':
                data['action_add_item']['enabled'] = True
                data['action_edit']['enabled'] = True
                data['action_edit']['url'] = purl + '/edit'
                data['action_paste']['enabled'] = True
            if uid in ['plone_control_panel', 'plone_addons']:
                data['action_view']['url'] = purl + '/plone_control_panel'
        return data

class ControlPanelItems(object):
    
    def __init__(self, context):
        self.context = context
    
    def item_by_id(self, id):
        for group in ['Plone', 'Products']:
            for item in self.items_by_group(group):
                if item['id'] == id:
                    return item
    
    def items_by_group(self, group):
        """Group 'Plone' or 'Products'
        """
        return self.context.portal_controlpanel.enumConfiglets(group=group)

ROOT_UID = 'plone_root'
CONTENT_UID = 'plone_content'
CP_UID = 'plone_control_panel'
ADDONS_UID = 'plone_addons'

class Action(object):
    implements(IAction)
    
    title = None
    order = 0
    group = None
    dropdown = False
    enabled = False
    url = u''
    ajax = False
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
    
    def __call__(self, request):
        raise NotImplementedError(u'Abstract Action does not ',
                                  u'implement ``__call__``.')
    
    @property
    def _uid(self):
        return self.request.get('uid')
    
    @property
    def _pobj(self):
        return self.context.portal_url.getPortalObject()
    
    def _query_object(self, uid):
        brains = self.context.portal_catalog(UID=uid)
        if not brains:
            return None
        return brains[0].getObject()

class ViewAction(Action):
    title = _('View')
    order = 10
    group = 10
    enabled = True
    
    @property
    def url(self):
        uid = self._uid
        # if content root, return portal url
        if uid == CONTENT_UID:
            return self._pobj.absolute_url()
        # if control panel or addons uid return plone_control_panel url
        if uid in [CP_UID, ADDONS_UID]:
            url = self._pobj.absolute_url()
            url += '/plone_control_panel'
            return url
        # if control panel item uid, return it's url
        cp_item = ControlPanelItems(self.context).item_by_id(uid)
        if cp_item:
            return cp_item['url']
        # if object queried from catalog, return it's url
        obj = self._query_object(uid)
        if not obj:
            return u''
        return obj.absolute_url()

class EditAction(Action):
    title = _('Edit')
    order = 20
    group = 10
    
    @property
    def enabled(self):
        uid = self._uid
        # if control panel or addons uid, disable edit
        if uid in [CP_UID, ADDONS_UID]:
            return False
        # if control panel item uid, disable
        cp_item = ControlPanelItems(self.context).item_by_id(uid)
        if cp_item:
            return False
        # XXX: check edit permissions for authenticated user
        return True
    
    @property
    def url(self):
        uid = self._uid
        # if content root, return portal edit url
        if uid == CONTENT_UID:
            return self._pobj.absolute_url() + '/edit'
        # if object queried from catalog, return object edit url
        obj = self._query_object(uid)
        if obj is not None:
            return obj.absolute_url() + '/edit'
        return None

class ChangeStateAction(Action):
    title = _('Change state')
    order = 30
    group = 10
    dropdown = True
    
    @property
    def enabled(self):
        uid = self._uid
        # if object from catalog and transitions available, enable workflow
        # management 
        obj = self._query_object(uid)
        if obj is not None:
            pactions = self.context.portal_actions
            actions = pactions.listFilteredActionsFor(obj)
            if actions['workflow']:
                return True
        return False

class AddItemAction(Action):
    title = _('Add item')
    order = 40
    group = 10
    dropdown = True
    
    @property
    def enabled(self):
        uid = self._uid
        if uid == CONTENT_UID:
            obj = self._pobj
        else:
            obj = self._query_object(uid)
        # if plone content or object from catalog and folderish, enable 
        # item adding
        if obj is not None and obj.isPrincipiaFolderish:
            menu = getUtility(IBrowserMenu, name=u'plone_contentmenu_factory')
            if menu.getMenuItems(obj, self.request):
                return True
        return False

class CutAction(Action):
    title = _('Cut')
    order = 10
    group = 20
    ajax = True
    
    @property
    def enabled(self):
        return False
    
    def __call__(self):
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
            parent.manage_cutObjects(context.getId(), self.request)
        except CopyError:
            #msg = _(u'${title} is not moveable.',
            #        mapping={u'title' : title})
            msg = u'%s is not moveable.' % title
            raise Exception, msg
        self.request.response.setCookie('__fct', self.context.UID(), path='/')
        #msg = _(u'${title} cut.', mapping={u'title' : title})
        msg = u'%s cut.' % title
        transaction_note('Cut object %s' % context.absolute_url())
        return msg, None

class CopyAction(Action):
    title = _('Copy')
    order = 20
    group = 20
    ajax = True
    
    @property
    def enabled(self):
        return False
    
    def __call__(self):
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
            parent.manage_copyObjects(context.getId(), self.request)
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

class PasteAction(Action):
    title = _('Paste')
    order = 30
    group = 20
    ajax = True
    
    @property
    def enabled(self):
        return False
    
    def __call__(self):
        context = self.context
        msg = _(u'Copy or cut one or more items to paste.')
        if context.cb_dataValid:
            try:
                context.manage_pasteObjects(self.request['__cp'])        
                transaction_note(
                    'Pasted content to %s' % (context.absolute_url()))
                self.request.response.expireCookie('__fct', path='/')
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

class DeleteAction(Action):
    title = _('Delete')
    order = 40
    group = 20
    ajax = True
    
    @property
    def enabled(self):
        return False
    
    def __call__(self):
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