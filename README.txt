Overview
========

This package provides an AJAX browser for Plone sites.

It uses the column browsing metaphor of MacOS finder.

The intention was to speed up content management issues, and fast content
browsing in Plone.

Another intention is to use this widget as reference browser.

Note
====
  
  * Not all features are implemented yet.
  
  * Its only tested in Firefox yet.
  
  * Still not works in plone 4.

Installation
============

  * make egg available in your plone site
  
  * apply corresponsing GS profile
  
  * now you have a link named 'Finder' in the portal Actions which triggers the
    widget

Credits
=======

  * Written by Robert Niederreiter <rnix@squarewave.at>
  
  * Thanks to the Sprinters at Cathedral Sprint 2010 for ideas and feedback

Chnages
=======

1.0.1a
------

  * basic code cleanup [rnix]
  
  * implement column batching [rnix]
  
  * self-contained buildout for plone 3 and plone 4 [jensens]

1.0
---

  * make it work [rnix]