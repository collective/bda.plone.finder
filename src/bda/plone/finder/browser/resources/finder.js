// finder.js
//
// author: Robert Niederreiter
// version: 1.0b2
// license: GPL2

jQuery(document).ready(function(){
	var selector = '#contentview-bda_plone_finder';
	
	// bind finder trigger
	var link = jQuery(selector);
    link.attr('rel', '#bda_finder_overlay');
    link.bind('click', function(event){
		event.preventDefault();
		jQuery(selector).finder();
    });
    
	// autoload finder if cookie set and not portal_factory context
    var cookie = readCookie('bda.plone.finder');
    if (cookie == 'autoload') {
        var cur_url = document.location.href;
        if (cur_url.indexOf('/portal_factory/') == -1 &&
            cur_url.substring(cur_url.lastIndexOf('/') + 1,
                              cur_url.length) != 'edit') {
			link.finder();
        }
    }
});

// query and show finder
jQuery.fn.finder = function(){
    var overlay = finder.overlay();
    var elem = jQuery(this);
    elem.overlay({
        target: overlay,
        mask: {
            color: '#eee',
            loadSpeed: 200,
            fixed: true
        },
        onBeforeLoad: function() {
			finder.query_html('bda.plone.finder', function(data) {
                overlay.append(data);
                var scrollable = finder.scrollable();
                scrollable.scrollable({
                    clickable: false,
                    speed: 150,
                    onBeforeSeek: function(event, index){
                        var size = finder.columns.length;
                        if (index > size - 4) {
                            return false;
                        }
                    },
                    onSeek: finder.prepare_navigation
                });
                finder.scroll_api = scrollable.data('scrollable');
                finder.initialize();
            });
        },
        onClose: function(){
            createCookie('bda.plone.finder', '');
            jQuery('.finder_container', overlay).remove();
			finder.reset();
        },
        oneInstance: false,
        closeOnClick: false
    });
    finder.overlay_api = elem.data('overlay');
    finder.overlay_api.load();
};

// action hooks for finder.actions
action_hooks = {

    /* before action hooks */
    
    // display confirmation dialog
	confirm_delete: function(uid, container, callback){
        finder.dialog.msg = 'Do you really want to delete this item?';
        finder.dialog.show(callback);
    },
    
    /* after action hooks */
    
    // reload column after cut or delete action
	cut_delete_entry: function(uid, container, data){
        var overlay = finder.overlay();
        var selector = '#finder_nav_item_' + container + ' a.column_expand';
        var elem = jQuery(selector, overlay).get(0);
        finder.query_column(elem, 'bda.plone.finder.expand');
    },
    
    // reload column after paste action
	paste_entry: function(uid, container, data){
        var url = 'bda.plone.finder.expand?uid=' + uid;
		finder.query_html(url, function(data) {
            for (var i = 0; i < finder.columns.length; i++) {
                if (finder.columns[i] == container) {
                    finder.actions.load(uid, container);
                    finder.apply_column(container, data, i);
                }
            }
        });
    },
    
    /* after load hooks */
    
    // rebind add action dropdown with current focused column
	rebind_add_action: function(actions){
        var overlay = finder.overlay();
        var action = jQuery('div.action_add_item a', overlay);
        action.unbind();
        action.bind('click', function(){
            if (jQuery(this).hasClass('disabled')) {
                return false;
            }
            createCookie('bda.plone.finder', 'autoload');
            var parent = jQuery(this).parent();
            var dropdown = jQuery('.action_dropdown', parent);
            var uid = finder.current_focused;
            finder.dropdown.elem = dropdown;
            finder.dropdown.show('bda.plone.finder.additemsmenu', uid, function(target){
                document.location.href = target.href;
            });
            return false;
        });
    }
};

// finder object
finder = {

    /* object members */
    
    // set by jQuery finder extension
    overlay_api: null,
    // set by jQuery finder extension
    scroll_api: null,
    columns: [],
    current_filter: null,
    // current focused column uid
    current_focused: null,
    // current selected item uid
    current_item: null,
    
    // action hooks configuration
    action_hooks: {
        action_cut: {
            before: null,
            after: action_hooks.cut_delete_entry
        },
        action_delete: {
            before: action_hooks.confirm_delete,
            after: action_hooks.cut_delete_entry
        },
        action_paste: {
            before: null,
            after: action_hooks.paste_entry
        }
    },
    
    /* object functions */
    
    // base url for ajax requests
	base_url: function() {
		var url = document.location.href;
        var idx = url.indexOf('?');
        if (idx != -1) {
            url = url.substring(0, idx);
        }
		if (url.substr(-1) === "/") {
			url = url.substring(0, url.length - 1);
		}
        return url;
    },
	
	// return overlay dom elem as jQuery object
    overlay: function(){
        if (!finder._overlay) {
            finder._overlay = jQuery('#bda_finder_overlay');
        }
        return finder._overlay;
    },
    
    // return columns dom elem as jQuery object
    scrollable: function(){
        if (!finder._scrollable) {
            finder._scrollable = jQuery('div.finder_columns', finder.overlay());
        }
        return finder._scrollable;
    },
    
    // uncached html ajax request
	query_html: function(url, callback) {
		jQuery.ajax({
            dataType: 'html',
            url: finder.base_url() + '/' + url,
            cache: false,
            success: callback
		});
	},
	
	// uncached json ajax request
	query_json: function(url, callback) {
		jQuery.ajax({
            dataType: 'json',
            url: finder.base_url() + '/' + url,
            cache: false,
            success: callback
        });
	},
	
	// reset finder dom elem references
	reset: function() {
		finder._overlay = null;
        finder._scrollable = null;
		finder._base_url = null;
	},
	
	// initialize finder
    initialize: function(){
        var idx = 0;
        var lastidx = 0;
        var items = finder.scroll_api.getItems();
        items.each(function(){
            var uid = this.id.substring(14, this.id.length);
            if (uid) {
                lastidx = idx;
            }
            finder.columns[idx] = uid;
			var column = jQuery(this);
            finder.bind_colums_items(column);
			finder.scroll_column_to_selected(column);
            idx++;
        });
        finder.actions.load(finder.columns[lastidx], finder.columns[lastidx - 1]);
        finder.bind_column_filter();
        var index = finder.scroll_api.getSize() - 4;
        finder.scroll_api.seekTo(index, 1);
    },
	
	// initialize column navigation UI callback
	prepare_navigation: function(event, index){
        var size = finder.columns.length;
        var button = jQuery('a.next', finder.overlay());
        if ((size <= 4) || (index == size - 4)) {
            // XXX: hack, for some reason on finer load time 'disabled' class
			//      is reset on scrollable.onSeek. So we use custom disabled
			//      css class 'f_disabled'.
            button.addClass('f_disabled');
        } else {
            button.removeClass('f_disabled');
            button.removeClass('disabled');
        }
    },
    
    // bind focus and keyup events on column filter input field
    bind_column_filter: function(){
        var overlay = finder.overlay();
        
		// reset filter input field
		jQuery('input.column_filter', overlay).bind('focus', function(){
            finder.current_filter = null;
            this.value = '';
            jQuery(this).css('color', '#000');
        });
        
		// refresh focused column with filtered listing
		jQuery('input.column_filter', overlay).bind('keyup', function(){
            finder.current_filter = this.value;
            var url = 'bda.plone.finder.expand?uid=';
            url += finder.current_focused + '&f=';
            url += finder.current_filter;
			finder.query_html(url, function(data) {
                var uid = finder.current_focused;
                for (var i = 0; i < finder.columns.length; i++) {
                    if (finder.columns[i] == uid) {
                        var after = finder.columns[i - 1];
                        finder.apply_column(after, data, i - 1);
                    }
                }
            });
        });
    },
    
    // bind click events to column items
    bind_colums_items: function(column){
        
		// expand contents to the right
		jQuery('a.column_expand', column).bind('click', function(){
            var uid = finder.column_uid(this);
            finder.current_focused = uid;
            finder.current_item = uid;
            finder.query_column(this, 'bda.plone.finder.expand');
        });
        
		// expand details to the right
		jQuery('a.column_details', column).bind('click', function(){
            finder.current_item = finder.column_uid(this);
            finder.query_column(this, 'bda.plone.finder.details');
        });
    },
	
	// scroll column to selected item if necessary
	scroll_column_to_selected: function(column) {
		var selected = jQuery('li.selected', column);
		if (selected.length) {
			var listing = jQuery('ul.columnitems', column);
			var list_h = listing.height();
			var col_h = column.height();
			if (list_h > col_h) {
				var range_y = list_h - col_h;
				var sel_y = selected.position().top - col_h;
	            var sel_h = selected.height();
				if (sel_y > 0) {
	                column.scrollTop(sel_y + sel_h + 3);
	            }
			}
		}
	},
    
    // query finder column
    query_column: function(elem, view){
        var obj_uid = finder.column_uid(elem);
        var column_uid = elem.rel.substring(15, elem.rel.length);
        var url = view + '?uid=' + obj_uid;
		finder.query_html(url, function(data) {
            for (var i = 0; i < finder.scroll_api.getSize(); i++) {
                if (finder.columns[i] == column_uid) {
                    finder.actions.load(obj_uid, column_uid);
                    finder.apply_column(column_uid, data, i);
                    break;
                }
            }
        });
    },
    
    // apply finder column
    apply_column: function(after, data, index){
        var scroll_api = finder.scroll_api;
        var items = scroll_api.getItems();
        
        // detect after position
        var after_uid;
        var after_position = 0;
        for (var i = 0; i < items.length; i++) {
            after_uid = jQuery(items.get(i)).attr('id');
            after_uid = after_uid.substring(14, after_uid.length);
            if (after_uid == after) {
                after_position = i;
                break;
            }
        }
        
        // set column uid's in finder.columns and detect after_col
        var column_uid = jQuery(data).get(0).id;
        column_uid = column_uid.substring(14, column_uid.length);
        var count = items.length;
        count = count < after_position + 2 ? after_position + 2 : count;
        var col, after_col;
        for (var i = 0; i < count; i++) {
            col = items.get(i);
            if (i == after_position) {
                after_col = jQuery(col);
            } else if (i == after_position + 1) {
                finder.columns[i] = column_uid;
            } else if (i > after_position + 1) {
                finder.columns[i] = null;
            }
        }
        
        // append new column after after_col
        after_col.after(data);
        
        // replace remaining columns with empty column or collect
        // them to be removed 
        var to_remove = [];
        var remove_count = 0;
        var empty_column = '<div class="finder_column">&nbsp;</div>';
        items = scroll_api.getItems();
        for (var i = after_position; i < scroll_api.getSize(); i++) {
            col = items.get(i);
            if (i > after_position + 1 && i <= 3) {
                jQuery(col).replaceWith(empty_column);
            } else if (i > after_position + 1 && i > 3) {
                to_remove[remove_count] = col;
                remove_count++;
            }
        }
        
        // remove superfluos columns and finalize
        jQuery(to_remove).remove();
        finder.trim_column_arr(after_position + 1);
        finder.set_selected_item(after_col, column_uid);
        var new_col = jQuery('#finder_column_' + column_uid, finder.scrollable());
        finder.bind_colums_items(new_col);
		finder.scroll_column_to_selected(new_col);
        var index = finder.scroll_api.getSize() - 4;
        index = index < 0 ? 0 : index;
        finder.scroll_api.seekTo(index, 1);
    },
    
    // trim finder.columns array
    trim_column_arr: function(count){
        var new_columns = [];
        if (count < 3) {
            count = 3;
        }
        for (var i = 0; i <= count; i++) {
            new_columns[i] = finder.columns[i];
        }
        finder.columns = new_columns;
    },
    
    // set selected column item
    set_selected_item: function(column, uid){
        jQuery('li.selected', column).toggleClass('selected');
        jQuery('#finder_nav_item_' + uid, column).toggleClass('selected');
    },
    
    // extract column uid
    column_uid: function(navitem){
        var uid = jQuery(navitem).parent().attr('id');
        return uid.substring(16, uid.length);
    },
    
    /* finder member objects */
    
    // yes / no dialog
    dialog: {
    
        // current dialog message
        msg: 'You see a dialog with an unset message',
        
        // dialog dom element
        elem: function(){
            return jQuery('div.finder_dialog', finder.overlay());
        },
        
        // show dialog and bind callback to ok button click event
        show: function(callback){
            var dialog = finder.dialog.elem();
            jQuery('.text', dialog).html(finder.dialog.msg);
            jQuery('button', dialog).unbind();
            jQuery('button.submit', dialog).bind('click', function(){
                finder.dialog.hide();
                callback();
            });
            jQuery('button.cancel', dialog).bind('click', function(){
                finder.dialog.hide();
            });
            dialog.fadeIn('fast');
        },
        
        // fade out dialog
        hide: function(){
            finder.dialog.elem().fadeOut('fast');
        }
    },
    
    // action dropdown menu
    dropdown: {
    
        // dropdown dom element. set before triggered
        elem: null,
        
        // show dropdown menu
        show: function(view, uid, callback){
            var dropdown = finder.dropdown.elem;
            var url = view + '?uid=' + uid;
            finder.query_html(url, function(data){
                dropdown.html(data);
                jQuery('a', dropdown).unbind();
            });
            jQuery(document).bind('mousedown', function(event){
                if (!event) {
                    var event = window.event;
                }
                if (event.target) {
                    var target = event.target;
                }
                else 
                    if (event.srcElement) {
                        var target = event.srcElement;
                    }
                if (jQuery(target).hasClass('action_dropdown') ||
                jQuery(target).hasClass('action_dropdown_item')) {
                    return true;
                }
                if (jQuery(target).hasClass('action_dropdown_link')) {
                    callback(target);
                }
                dropdown.css('display', 'none');
                dropdown.empty();
            });
            dropdown.css('display', 'block');
        }
    },
    
    // transitions
    transitions: {
    
        // bind change state action
        bind: function(){
            var overlay = finder.overlay();
            var action = jQuery('div.action_change_state a', overlay);
            action.unbind();
            action.bind('click', function(){
                if (jQuery(this).hasClass('disabled')) {
                    return false;
                }
                finder.transitions.query_transitions(this);
                return false;
            });
        },
        
        // query transitions and display dropdown
        query_transitions: function(action){
            if (jQuery(action).hasClass('disabled')) {
                return false;
            }
            createCookie('bda.plone.finder', 'autoload');
            var parent = jQuery(action).parent();
            var dropdown = jQuery('.action_dropdown', parent);
            var uid = finder.current_item;
            var view = 'bda.plone.finder.transitionsmenu';
            finder.dropdown.elem = dropdown;
            finder.dropdown.show(view, uid, function(target){
                // XXX: ajaxify
                document.location.href = target.href;
            });
        }
    },
    
    // actions
    actions: {
    
        /* actions object members */
        
		uid: null,
        column: null,
        actions: null,
        url: null,
        name: null,
        
        /* actions object functions */
        
        // load actions
        load: function(uid, column){
            finder.actions.uid = uid;
            finder.actions.column = column;
            var container = finder.overlay();
            var url = 'bda.plone.finder.actioninfo?uid=' + uid;
            var actions = finder.actions;
            finder.query_json(url, function(data){
                actions.actions = data;
                for (var action_name in actions.actions) {
                    var action = jQuery('.' + action_name + ' a', container);
                    var url = actions.actions[action_name]['url'];
                    var enabled = actions.actions[action_name]['enabled'];
                    var ajax = actions.actions[action_name]['ajax'];
                    var autoload = actions.actions[action_name]['autoload'];
                    action.attr('href', url);
                    if (enabled) {
                        actions.enable(action);
                    }
                    else {
                        actions.disable(action);
                    }
                    if (ajax && enabled) {
                        action.bind('click', function(event){
                            actions.execute(this);
                            event.preventDefault();
                        });
                    }
                    if (!ajax && enabled && autoload) {
                        action.bind('click', function(){
                            createCookie('bda.plone.finder', 'autoload');
                        });
                    }
                }
                // XXX: make after load calls hookable
                finder.transitions.bind();
                action_hooks.rebind_add_action(actions);
            });
        },
        
        // enable action
        enable: function(action){
            if (action.hasClass('disabled')) {
                action.removeClass('disabled');
            }
            action.unbind();
        },
        
        // disable action
        disable: function(action){
            if (!action.hasClass('disabled')) {
                action.addClass('disabled');
            }
            action.attr('href', '#');
            action.unbind();
            action.bind('click', function(){
                return false;
            });
        },
        
        // execute action
        execute: function(action){
            action = jQuery(action);
            finder.actions.name = action.parent().attr('class');
            finder.actions.url = 'bda.plone.finder.execute?uid=' + finder.actions.uid;
            finder.actions.url += '&name=' + finder.actions.name;
            var hook = finder.action_hooks[finder.actions.name];
            if (hook) {
                var func = hook['before'];
                if (func) {
                    func(finder.actions.uid, finder.actions.column, finder.actions.perform_action);
                    return;
                }
            }
            finder.actions.perform_action();
        },
        
        // perform action
        perform_action: function(){
            var actions = finder.actions;
            var url = finder.actions.url;
            finder.query_json(url, function(data){
                var container = finder.overlay();
                var icon_name = 'error_icon.png';
				if (!data.err) {
					icon_name = 'info_icon.png';
                    var hook = finder.action_hooks[actions.name];
                    if (hook) {
                        var func = hook['after'];
                        if (func) {
                            func(actions.uid, actions.column, data);
                        }
                    }
                }
				var message = jQuery('div.finder_message_bar', container);
				var icon = '<img src="++resource++bda.plone.finder.images/';
				icon += icon_name + '" alt="" />';
                message.html(icon + data.msg);
            });
        }
    }
};
