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

Behavior
========

``bda.plone.finder`` browser view is requested via XML HTTP request and the
returned markup gets displayed inside the overlay.

For expanding columns respective rendering details columns the views
``bda.plone.finder.expand`` and ``bda.plone.finder.details`` are requested.

The actions configuration for context is requested via
``bda.plone.finder.actioninfo`` browser view by JSON request.

Execution of actions is done by requesting ``bda.plone.finder.execute``, again
via JSON

Development and evaluation
==========================

you can checkout and install from source code. Plone 4 buildout configuration
is included.
::

    https://svn.plone.org/svn/collective/bda.plone.finder/trunk/

Note
====

  * Plone 4 only
  
  * Testet in Firefox, Chrome, Safari, IE7

Credits
=======

  * Robert Niederreiter <dev@bluedynamics.com>
  
  * Thanks to the Sprinters at Cathedral Sprint 2010 for ideas and feedback

Changes
=======

1.0b4
-----

  * Refactor finder actions

  * Add View interfaces
  
  * Fix ``uid`` property in ATDetails column view

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
