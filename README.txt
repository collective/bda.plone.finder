Overview
========

This package provides an AJAX browser for Plone sites.

It uses the column browsing metaphor of MacOS finder.

The intention was to speed up content management issues, and fast content
browsing in Plone.

Installation
============

  * make egg available in your plone site
  
  * apply corresponsing GS profile
  
  * now you have a link named 'Finder' in the document Actions which trigger the
    widget

Credits
=======

  * Written by Robert Niederreiter <rnix@squarewave.at>
  
  * Thanks to the Sprinters at Cathedral Sprint 2010 for ideas and feedback

Note
====

  * Plone 4 only
  
  * Firefox, IE7

Changes
=======

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