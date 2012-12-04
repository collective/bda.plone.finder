Overview
========

This package provides an AJAX browser for Plone sites.

It uses the column browsing metaphor of OSX finder.

The intention was to speed up content management issues, and fast content
browsing in Plone.

.. image:: http://bluedynamics.com/bda.plone.finder.png


Installation
============

- Make egg available in your Plone site
  
- Apply corresponding GS profile


Restrictions
============

If you want to browse Dexterity contents, consider to provide a UID by your
dexterity types in order to make them work with finder.


Usage
=====

After installation you have a link named 'Finder' at the top right of your
plone site. This link is provided by a viewlet and is positioned absolute. Use
CSS of your theme to put it wherever you like.

The finder gets displayed with focus on trigger context by clicking this
link.


Development and evaluation
==========================

you can checkout and install from source code. Plone 4 buildout configuration
is included.

Checkout with write access::

    git clone git@github.com:collective/bda.plone.finder.git

Anonymous checkout::

    git clone git://github.com/collective/bda.plone.finder.git


Compatibility
=============

Plone Versions
--------------

- Plone 3

- Plone 4


Browser
-------
  
- Firefox
  
- Chrome
  
- Safari
  
- IE6 (looks ugly due to png images, but works)
  
- IE7
  
- IE8


Contributors
============

- Robert Niederreiter <dev@bluedynamics.com>
  
- Sven Plage
  
- Thanks to the Sprinters at Cathedral Sprint 2010 for ideas and feedback


Changes
=======

1.1
---

- Add specific permission to trigger finder

1.0.1
-----

- Add ``p3`` and ``p4`` profile for different CSS registration

1.0
---

- Add image preview
  
- Add event preview
  
- Show items of all languages if LinguaPlone is installed.
  
- Fix bug with css class manipulation and column reloading after workflow
  state changed.
  
- Use zope:class and zope:implements directives to set marker interface for
  finder root instead of five:implements

1.0rc1
------

- Fix bug with base URL after delete item, if finder was called from deleted
  item.
  
- Remove autoload behavior.
  
- Change workflow state action ajaxified.
  
- Fix base_url detection in viewlet. 
  
- Shorten title in listing to avoid line break.
  
- Do not display items without UID.
  
- Add separate conditional CSS for Plone 3 + 4.
  
- Remove trigger link from object actions and provide it by viewlet instead.
  
- Plone 3 Compatibility.

1.0b7
-----

- Basically bind dexterity compatible views. Dexterity support not finished
  yet due to missing UID indexing support.
  
- Provide CSS for default plone content types icons.

- Check for ``INonStructuralFolder`` in ``AddItemAction.enabled`` if context
  is folderish.
  
- Use id in column item if title not set in ``FolderColumn``.

1.0b6
-----

- Add finder overlay via JS instead of viewlet.
  
- Refactor server side column rendering API.

1.0b5
-----

- Check for 'Add portal content' permission in ``OFSPasteAction.enabled``.
  
- Check for 'Delete objects' permission in ``OFSCutAction.enabled``.
  
- Check for 'Modify portal content' permission in ``EditAction.enabled``.
  
- Only show control panel and addon configuration links in root column if
  user is manager.
  
- Protect browser views from within against anonymous user.

- Bind finder trigger to ``View`` permission.

- Adopt browser view's permissions for non managers.
  
- Use i18n messages in actions and use ``context.translate``.
  
- CSS fix for IE6

1.0b4
-----

- Refactor finder actions.

- Add View interfaces.
  
- Fix ``uid`` property in ``ATDetails`` column view.

- Fix initial finder rendering when called on leaf object located in plone.
    root

- Enable paste action on plone root content.

1.0b3
-----

- Add action hook for view action resetting finder ``bda.plone.finder``.
  cookie
  
- Deliver context URL for ajax calls from server.
  
- ``bda.plone.finder`` cookie can contain url's now (beside value 'autoload')
  which define the actual context to be used as base url for auto load.
  
- Rename ``perform_action`` to ``perform_ajax`` and add ``follow_action_link``
  function as non ajax callback for actions.

- Change autoload logic, remove from server side action definitions and let
  do JS action callbacks the work.
  
- Enable before hooks on non ajax actions.
  
- Wrap finder JS code inside ``(function($) { ... })(jQuery);`` block
  and use ``$`` instead of ``jQuery``.
  
- Refactor actions performing and corresponding hooks.

- Add minified finder.js.

1.0b2
-----
  
- Remove ``li.cut`` dom elems after paste action.
  
- Add ``finder.base_url`` in JS to fix ajax request context.
  
- Do not cache ajax requests.
  
- Scroll column to selected item if necessary.
  
- Disable navigate right arrow on init.
  
- Initially render context column when opening finder on plone root.
  
- JS cleanup and documentation.

1.0b1
-----

- Improve dialog styles.
  
- Remove auto fading status message when performing actions. Instead write
  this information to status bar below columns now.
  
- Reset ``finder._overlay`` and ``finder._scrollable`` on close.
  
- IE7 CSS fix for column items.
  
- Remove dependencies to ``bda.plone.ajax``.

1.0a4
-----

- Remove column batching. instead use css overflow.
  
- adopt to new jQuery tools scrollable.
  
- make me basically work in IE7.
  
- JS refactoring.

1.0a3
-----

- Change look and feel of batching column pages. Its a vertical slider now.

- Implement auto loading after editing or adding items out of finder.

- Implement change state dropdown.

- Implement add dropdown.

- Implement column filtering.

- Remove unused imports from source files.
  
- Titles for finder controls.

1.0a2
-----

- Basic code cleanup.
  
- Implement column batching.
  
- Self-contained buildout for plone 3 and plone 4.

1.0a1
-----

- Make it work.
