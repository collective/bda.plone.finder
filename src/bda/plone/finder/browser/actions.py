# -*- coding: utf-8 -*-
import simplejson as json
from zope.interface import implements
from zope.component import getAdapter
from zope.component.interfaces import ComponentLookupError
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
from bda.plone.finder.interfaces import IActionExecution

class Actions(BrowserView):
    
    def actionInfo(self):
        
        
        data = dict()
        for name in ['action_view',
                     'action_edit',
                     'action_change_state',
                     'action_add_item']:
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
        return json.dumps({
            'err': err,
            'msg': msg,
            'uid': ret_uid,
        })
    
    def _get_object(self, uid):
        if uid == 'plone_content':
            return self.context.portal_url.getPortalObject()
        brains = self.context.portal_catalog(UID=uid)
        if not brains:
            return None
        return brains[0].getObject()
    
    def _create_action(self, enabled=False, url='',
                       ajax=False):
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

class Action(object):
    implements(IAction)
    
    title = None
    order = 0
    group = None
    dropdown = False
    
    @property
    def enabled(self):
        return False
    
    @property
    def url(self):
        return u''
    
    @property
    def ajax(self):
        return False
    
    def __init__(self, context):
        self.context = context

class ViewAction(Action):
    title = _('View')
    order = 10
    group = 10

class EditAction(Action):
    title = _('Edit')
    order = 20
    group = 10

class ChangeStateAction(Action):
    title = _('Change state')
    order = 30
    group = 10
    dropdown = True

class AddItemAction(Action):
    title = _('Add item')
    order = 40
    group = 10
    dropdown = True

class CutAction(Action):
    title = _('Cut')
    order = 10
    group = 20

class CopyAction(Action):
    title = _('Copy')
    order = 20
    group = 20

class PasteAction(Action):
    title = _('Paste')
    order = 30
    group = 20

class DeleteAction(Action):
    title = _('Delete')
    order = 40
    group = 20

class ActionExecution(object):
    
    implements(IActionExecution)
    
    def __init__(self, context):
        self.context = context
    
    def __call__(self, request):
        raise NotImplementedError(u'Abstract ActionExecution does not ',
                                  u'implement ``__call__``.')

class CutActionExecution(ActionExecution):
    
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

class CopyActionExecution(ActionExecution):
    
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

class PasteActionExecution(ActionExecution):
    
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

class DeleteActionExecution(ActionExecution):
    
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