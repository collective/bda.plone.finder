### work in progress

AJAX Views Used by finder JS
============================

  * ``bda.plone.finder`` browser view is requested for initial finder rendering
    via XML HTTP request and the returned markup gets displayed inside the
    overlay.

  * For expanding columns respective rendering details columns the views
    ``bda.plone.finder.expand`` and ``bda.plone.finder.details`` are requested.

  * The actions configuration for focused context is requested by
    ``bda.plone.finder.actioninfo`` browser view as JSON request.

  * Execution of ajax actions is done by requesting
    ``bda.plone.finder.execute``, again as JSON request.
  
  * A utility view is used for querying workflow states after workflow
    transitions using 'bda.plone.finder.review_state'.


Application behavior
====================

Triggering finder
-----------------

  * When requesting a page by URL, on server side the base URL for requesting
    further AJAX calls is rendered by viewlet ``bda.plone.finder.viewlet``.

  * If user is authenticated, she gets displayed the finder triggering link in
    object actions.

  * When finder gets triggered, ``bda.plone.finder`` browser view gets
    requested on recent context.

  * The actions registered for current finder flavor are rendered. At this
    state all actions are disabled.

  * Rendering columns is done by ``IColumnProvider`` implementation, which
    knows about the recent rendering context and flavor, how to render this
    context and the initial columns to be displayed.

  * After hooking result to DOM tree, ``bda.plone.finder.actioninfo`` gets
    called and finder actions are initialized for recent context and flavor.

Expanding columns
-----------------

  * XXX

Display details column
----------------------

  * XXX

Performing actions
------------------

  * XXX


Providing Custom Actions
========================

To add an action to finder, you have to write an
``bda.plone.finder.interfaces.IAction`` implementation. A base implementation
exists in ``bda.plone.finder.browser.actions`` which you can derive from.
::

    >>> from bda.plone.finder.browser.actions import Action
    >>> class MyAction(Action):
    ...     title = _('My Action')
    ...     order = 10
    ...     group = 10
    ...     ajax = True
    ...     
    ...     @property
    ...     def enabled(self):
    ...         return True
    ... 
    ...     def __call__(self):
    ...         # do something
    ...         return 'foo', None

Register your action via ZCML.
::

    <adapter for="* zope.publisher.interfaces.http.IHTTPRequest"
        name="my_action"
        factory=".mypackage.MyAction"
    />


  * ``order``, ``group`` and ``title`` attributes are used for action rendering
    in finder menu bar.

  * The ``enabled`` property defines action availability for focused context
    and is requested during object focus in UI via
    ``bda.plone.finder.actioninfo`` view.

  * If ``ajax`` property is set to ``True``, finder JS calls
    ``bda.plone.finder.execute`` with appropriate object uid and action id. In
    this case ``__call__`` function must be implemented, which gets triggered
    by ``bda.plone.finder.execute`` view.

  * If ``ajax`` property is set to False, ``url`` property must be provided. On
    non ajax actions finder just follows provided URL.

You can hook custom Javascript on the client side, if some ajax action requires
this. 3 hooks are provided. After action was loaded by actioninfo view, before
action is executed, and after action has been executed.
::

    $.extend(finder.hooks.actions_loaded, {    
        
        // after load hooks gets passed ``finder.actions`` object 
        my_after_load_hook: function(actions) {
            // do something    
        }
    });
    
    $.extend(finder.hooks.actions, {
        
        // action id
        my_action: {
            
            // hook before action is executed. you can use this i.e. for
            // validation.
            //
            // gets passed focused object uid, container uid and the action
            // callback, which must be called if action finally should be
            // executed.
            before: function(uid, container, callback) {
                // do something
                callback();
            },
            
            // hook after action is executed you can use this i.e. for dom
            // manipulation depending on action result.
            //
            // gets passed focused object uid, container uid and the JSON result
            // from ajax action execution.
            after: function(uid, container, data) {
                // do something
            }
        }
    });

If you want to skip one ore another hook, set it to ``null``.

Note: on non ajax action, after hooks are never called!