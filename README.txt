Overview
========

This package provides an AJAX browser for Plone sites.

It uses the column browsing metaphor of OSX finder.

The intention was to speed up content management issues, and fast content
browsing in Plone.

.. image:: http://bluedynamics.com/bda.plone.finder.png


Installation
============

  * Make egg available in your Plone site
  
  * Apply corresponding GS profile


Usage
=====

After installation you have a link named 'Finder' in the document actions.
The finder gets displayed with focus on triggering context by clicking this
link.


AJAX Views Used by finder JS
============================

``bda.plone.finder`` browser view is requested via XML HTTP request and the
returned markup gets displayed inside the overlay.

For expanding columns respective rendering details columns the views
``bda.plone.finder.expand`` and ``bda.plone.finder.details`` are requested.

The actions configuration for focudes context is requested via
``bda.plone.finder.actioninfo`` browser view by JSON request.

Execution of ajax actions is done by requesting ``bda.plone.finder.execute``,
again via JSON


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

``order``, ``group`` and ``title`` attributes are used for action rendering
in finder menu bar.

The ``enabled`` property defines action availability for focused context and
is requested during object focus in UI via ``bda.plone.finder.actioninfo`` view.

If ``ajax`` property is set to ``True``, finder JS calls
``bda.plone.finder.execute`` with appropriate object uid and action id. In this
case ``__call__`` function must be implemented, which gets triggered by
``bda.plone.finder.execute`` view.

If ``ajax`` property is set to False, ``url`` property must be provided. On
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

If you want to skip one ore another hook, set it to ``null``.

Note: on non ajax action, after hooks are never called!


Development and evaluation
==========================

you can checkout and install from source code. Plone 4 buildout configuration
is included.
::

    https://svn.plone.org/svn/collective/bda.plone.finder/trunk/


Note
====

  * Plone 4 only
  
  * Testet in Firefox, Chrome, Safari, IE6, IE7, IE8


Credits
=======

  * Robert Niederreiter <dev@bluedynamics.com>
  
  * Thanks to the Sprinters at Cathedral Sprint 2010 for ideas and feedback


Changes
=======

1.0b5
-----

  * Bind finder trigger to ``View`` permission.

  * Adopt browser view permissions
  
  * Use i18n messages in actions and use ``context.translate``
  
  * CSS fix for IE6

1.0b4
-----

  * Refactor finder actions

  * Add View interfaces
  
  * Fix ``uid`` property in ``ATDetails`` column view

  * Fix initial finder rendering when called on leaf object located in plone
    root

  * Enable paste action on plone root content

1.0b3
-----

  * Add action hook for view action resetting finder ``bda.plone.finder``
    cookie
  
  * Deliver context URL for ajax calls from server
  
  * ``bda.plone.finder`` cookie can contain url's now (beside value 'autoload')
    which define the actual context to be used as base url for auto load
  
  * Rename ``perform_action`` to ``perform_ajax`` and add ``follow_action_link``
    function as non ajax callback for actions

  * Change autoload logic, remove from server side action definitions and let
    do JS action callbacks the work
  
  * Enable before hooks on non ajax actions
  
  * Wrap finder JS code inside ``(function($) { ... })(jQuery);`` block
    and use ``$`` instead of ``jQuery``
  
  * Refactor actions performing and corresponding hooks

  * Add minified finder.js

1.0b2
-----
  
  * Remove ``li.cut`` dom elems after paste action 
  
  * Add ``finder.base_url`` in JS to fix ajax request context
  
  * Do not cache ajax requests
  
  * Scroll column to selected item if necessary
  
  * Disable navigate right arrow on init
  
  * Initially render context column when opening finder on plone root
  
  * JS cleanup and documentation

1.0b1
-----

  * Improve dialog styles
  
  * Remove auto fading status message when performing actions. Instead write
    this information to status bar below columns now
  
  * Reset ``finder._overlay`` and ``finder._scrollable`` on close
  
  * IE7 CSS fix for column items
  
  * Remove dependencies to ``bda.plone.ajax``

1.0a4
-----

  * Remove column batching. instead use css overflow
  
  * adopt to new jQuery tools scrollable
  
  * make me basically work in IE7
  
  * JS refactoring

1.0a3
-----

  * Change look and feel of batching column pages. Its a vertical slider now

  * Implement auto loading after editing or adding items out of finder

  * Implement change state dropdown

  * Implement add dropdown

  * Implement column filtering

  * Remove unused imports from source files
  
  * Titles for finder controls

1.0a2
-----

  * Basic code cleanup
  
  * Implement column batching
  
  * Self-contained buildout for plone 3 and plone 4

1.0a1
-----

  * Make it work
