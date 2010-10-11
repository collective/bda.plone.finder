Overview
========

This package provides an AJAX browser for Plone sites.

It uses the column browsing metaphor of OSX finder.

The intention was to speed up content management issues, and fast content
browsing in Plone.

.. image:: http://bluedynamics.com/bda.plone.finder.png

Installation
============

  * make egg available in your Plone site
  
  * apply corresponding GS profile
  
  * now you have a link named 'Finder' in the document actions which trigger the
    widget

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

  * Written by Robert Niederreiter <rnix@squarewave.at>
  
  * Thanks to the Sprinters at Cathedral Sprint 2010 for ideas and feedback

Changes
=======

1.0b3
-----

  * Wrap finder JS code inside ``(function($) { ... })(jQuery);`` block
    and use ``$`` instead of ``jQuery`` [rnix]
  
  * Refactor actions performing and corresponding hooks [rnix]

  * Add minified finder.js [rnix]

1.0b2
-----
  
  * Remove ``li.cut`` dom elems after paste action [rnix] 
  
  * Add ``finder.base_url`` in JS to fix ajax request context [rnix]
  
  * Do not cache ajax requests [rnix]
  
  * Scroll column to selected item if necessary [rnix]
  
  * Disable navigate right arrow on init [rnix]
  
  * Initially render context column when opening finder on plone root [rnix]
  
  * JS cleanup and documentation [rnix]

1.0b1
-----

  * Improve dialog styles [rnix]
  
  * Remove auto fading status message when performing actions. Instead write
    this information to status bar below columns now [rnix]
  
  * Reset ``finder._overlay`` and ``finder._scrollable`` on close [rnix]
  
  * IE7 CSS fix for column items [rnix]
  
  * Remove dependencies to ``bda.plone.ajax`` [rnix]

1.0a4
-----

  * Remove column batching. instead use css overflow [rnix]
  
  * adopt to new jQuery tools scrollable [rnix]
  
  * make me basically work in IE7 [rnix]
  
  * JS refactoring [rnix]

1.0a3
-----

  * Change look and feel of batching column pages. Its a vertical slider now
    [rnix]

  * Implement auto loading after editing or adding items out of finder [rnix]

  * Implement change state dropdown [rnix]

  * Implement add dropdown [rnix]

  * Implement column filtering [rnix]

  * Remove unused imports from source files [rnix]
  
  * Titles for finder controls [rnix]

1.0a2
-----

  * Basic code cleanup [rnix]
  
  * Implement column batching [rnix]
  
  * Self-contained buildout for plone 3 and plone 4 [jensens]

1.0a1
-----

  * Make it work [rnix]