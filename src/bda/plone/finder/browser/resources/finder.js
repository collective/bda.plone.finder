// finder.js
//
// author: Robert Niederreiter
// version: 1.0b7
// license: GPL2

(function($) {
    
    $(document).ready(function() {
        
        // add finder overlay to dom tree
        var elem = '<div class="finder_overlay" id="bda_finder_overlay"></div>';
        $(elem).insertBefore($('#visual-portal-wrapper'));
        
        // bind finder trigger
        var selector = '.findertrigger a';
        var link = $(selector);
        link.attr('rel', '#bda_finder_overlay');
        link.bind('click', function(event) {
            event.preventDefault();
            $(selector).finder();
        });
    });
    
    // query and show finder
    $.fn.finder = function() {
        var overlay = finder.overlay();
        var elem = $(this);
        elem.overlay({
            target: overlay,
            mask: {
                color: '#eee',
                loadSpeed: 200,
                fixed: true
            },
            onBeforeLoad: function() {
                finder.request_html('bda.plone.finder', function(data) {
                    overlay.append(data);
                    var scrollable = finder.scrollable();
                    scrollable.scrollable({
                        clickable: false,
                        speed: 150,
                        onBeforeSeek: function(event, index) {
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
            onClose: function() {
                $('.finder_container', overlay).remove();
                finder.reset();
            },
            oneInstance: false,
            closeOnClick: false
        });
        finder.overlay_api = elem.data('overlay');
        finder.overlay_api.load();
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
        // extend this when you need finder specific helper stuff
        utils: {},
        
        /* object functions */
        
        // base url for ajax requests
        base_url: function() {
            if (!finder._base_url) {
                finder._base_url = $('#finder_base_url').text();
            }
            return finder._base_url;
        },
        
        // return overlay dom elem as jQuery object
        overlay: function() {
            if (!finder._overlay) {
                finder._overlay = $('#bda_finder_overlay');
            }
            return finder._overlay;
        },
        
        // return columns dom elem as jQuery object
        scrollable: function() {
            if (!finder._scrollable) {
                finder._scrollable = $('div.finder_columns', finder.overlay());
            }
            return finder._scrollable;
        },
        
        // uncached html ajax request
        request_html: function(url, callback) {
            $.ajax({
                dataType: 'html',
                url: finder.base_url() + '/' + url,
                data: {ajax_load: 1},
                cache: false,
                success: callback
            });
        },
        
        // uncached json ajax request
        request_json: function(url, callback) {
            $.ajax({
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
        initialize: function() {
            var idx = 0;
            var lastidx = 0;
            var items = finder.scroll_api.getItems();
            items.each(function() {
                var uid = this.id.substring(14, this.id.length);
                if (uid) {
                    lastidx = idx;
                }
                finder.columns[idx] = uid;
                var column = $(this);
                finder.bind_colums_items(column);
                finder.scroll_column_to(column, 'li.selected');
                idx++;
            });
            finder.current_focused = finder.columns[lastidx];
            finder.current_item = finder.columns[lastidx];
            finder.actions.load(finder.columns[lastidx],
                                finder.columns[lastidx - 1]);
            finder.bind_column_filter();
            var index = finder.scroll_api.getSize() - 4;
            finder.scroll_api.seekTo(index, 1);
        },
        
        // initialize column navigation UI callback
        prepare_navigation: function(event, index) {
            var size = finder.columns.length;
            var button = $('a.next', finder.overlay());
            if ((size <= 4) || (index == size - 4)) {
                // XXX: hack, for some reason on finder load time 'disabled'
                //      class is reset on scrollable.onSeek. So we use custom
                //      disabled css class 'f_disabled'.
                button.addClass('f_disabled');
            } else {
                button.removeClass('f_disabled');
                button.removeClass('disabled');
            }
        },
        
        // bind focus and keyup events on column filter input field
        bind_column_filter: function() {
            var overlay = finder.overlay();
            
            // reset filter input field
            $('input.column_filter', overlay).bind('focus', function() {
                finder.current_filter = null;
                this.value = '';
                $(this).css('color', '#000');
            });
            
            // refresh focused column with filtered listing
            $('input.column_filter', overlay).bind('keyup', function() {
                finder.current_filter = this.value;
                var url = 'bda.plone.finder.expand?uid=';
                url += finder.current_focused + '&f=';
                url += finder.current_filter;
                finder.request_html(url, function(data) {
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
        bind_colums_items: function(column) {
            
            // expand contents to the right
            $('a.column_expand', column).bind('click', function() {
                var uid = finder.column_uid(this);
                finder.current_focused = uid;
                finder.current_item = uid;
                finder.query_column(this, 'bda.plone.finder.expand');
            });
            
            // expand details to the right
            $('a.column_details', column).bind('click', function() {
                finder.current_item = finder.column_uid(this);
                finder.query_column(this, 'bda.plone.finder.details');
            });
        },
        
        // scroll column to item if necessary
        scroll_column_to: function(column, selector) {
            var selected = $(selector, column);
            if (selected.length) {
                var listing = $('ul.columnitems', column);
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
        query_column: function(elem, view) {
            var obj_uid = finder.column_uid(elem);
            var column_uid = elem.rel.substring(15, elem.rel.length);
            var url = view + '?uid=' + obj_uid;
            finder.request_html(url, function(data) {
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
        apply_column: function(after, data, index) {
            var scroll_api = finder.scroll_api;
            var items = scroll_api.getItems();
            
            // detect after position
            var after_uid;
            var after_position = 0;
            for (var i = 0; i < items.length; i++) {
                after_uid = $(items.get(i)).attr('id');
                after_uid = after_uid.substring(14, after_uid.length);
                if (after_uid == after) {
                    after_position = i;
                    break;
                }
            }
            
            // set column uid's in finder.columns and detect after_col
            var column_uid = $(data).get(0).id;
            column_uid = column_uid.substring(14, column_uid.length);
            var count = items.length;
            count = count < after_position + 2 ? after_position + 2 : count;
            var col, after_col;
            for (var i = 0; i < count; i++) {
                col = items.get(i);
                if (i == after_position) {
                    after_col = $(col);
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
                    $(col).replaceWith(empty_column);
                } else if (i > after_position + 1 && i > 3) {
                    to_remove[remove_count] = col;
                    remove_count++;
                }
            }
            
            // remove superfluos columns and finalize
            $(to_remove).remove();
            finder.trim_column_arr(after_position + 1);
            finder.set_selected_item(after_col, column_uid);
            var new_col = $('#finder_column_' + column_uid,
                            finder.scrollable());
            finder.bind_colums_items(new_col);
            finder.scroll_column_to(new_col, 'li.selected');
            var index = finder.scroll_api.getSize() - 4;
            index = index < 0 ? 0 : index;
            finder.scroll_api.seekTo(index, 1);
        },
        
        // trim finder.columns array
        trim_column_arr: function(count) {
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
        set_selected_item: function(column, uid) {
            $('li.selected', column).toggleClass('selected');
            $('#finder_nav_item_' + uid, column).toggleClass('selected');
        },
        
        // extract column uid
        column_uid: function(navitem) {
            var uid = $(navitem).parent().attr('id');
            return uid.substring(16, uid.length);
        },
        
        /* finder member objects */
        
        // yes / no dialog
        dialog: {
        
            // current dialog message
            msg: 'You see a dialog with an unset message',
            
            // dialog dom element
            elem: function() {
                return $('div.finder_dialog', finder.overlay());
            },
            
            // show dialog and bind callback to ok button click event
            show: function(callback) {
                var dialog = finder.dialog.elem();
                $('.text', dialog).html(finder.dialog.msg);
                $('button', dialog).unbind();
                $('button.submit', dialog).bind('click', function() {
                    finder.dialog.hide();
                    callback();
                });
                $('button.cancel', dialog).bind('click', function() {
                    finder.dialog.hide();
                });
                dialog.fadeIn('fast');
            },
            
            // fade out dialog
            hide: function() {
                finder.dialog.elem().fadeOut('fast');
            }
        },
        
        // action dropdown menu
        dropdown: {
        
            // dropdown dom element. set before triggered
            elem: null,
            
            // show dropdown menu
            show: function(view, uid, callback) {
                var dropdown = finder.dropdown.elem;
                var url = view + '?uid=' + uid;
                finder.request_html(url, function(data) {
                    dropdown.html(data);
                    $('a', dropdown).unbind();
                });
                $(document).unbind('mousedown')
                           .bind('mousedown', function(event) {
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
                    if ($(target).hasClass('action_dropdown') ||
                    $(target).hasClass('action_dropdown_item')) {
                        return true;
                    }
                    if ($(target).hasClass('action_dropdown_link')) {
                        callback(target);
                    }
                    dropdown.css('display', 'none');
                    dropdown.empty();
                });
                dropdown.css('display', 'block');
            }
        },
        
        // finder actions object.
        // provide querying and executing of actions for a specific context.
        actions: {
        
            /* actions object members */
            
            uid: null,
            column: null,
            actions: null,
            url: null,
            name: null,
            
            /* actions object functions */
            
            // load actions for current selected item and bind events
            load: function(uid, column) {
                finder.actions.uid = uid;
                finder.actions.column = column;
                var container = finder.overlay();
                var url = 'bda.plone.finder.actioninfo?uid=' + uid;
                var actions = finder.actions;
                finder.request_json(url, function(data) {
                    actions.actions = data;
                    for (var action_name in actions.actions) {
                        var action = $('.' + action_name + ' a', container);
                        var url = actions.actions[action_name]['url'];
                        var enabled = actions.actions[action_name]['enabled'];
                        var ajax = actions.actions[action_name]['ajax'];
                        action.attr('href', url);
                        if (enabled) {
                            actions.enable(action);
                            action.unbind();
                            action.bind('click', function(event) {
                                actions.execute(this);
                                event.preventDefault();
                            });
                            if (ajax) {
                                action.addClass('ajax');
                            }
                        } else {
                            actions.disable(action);
                            if (!ajax) {
                                action.removeClass('ajax');
                            }
                        }
                    }
                    
                    // perform after actions load hooks
                    // XXX adopt to $.each
                    for (var hook_name in finder.hooks.actions_loaded) {
                        var func = finder.hooks.actions_loaded[hook_name];
                        if (func) {
                            func(actions);
                        }
                    }
                });
            },
            
            // remove disabled css class from action dom element
            enable: function(action) {
                if (action.hasClass('disabled')) {
                    action.removeClass('disabled');
                }
                action.unbind();
            },
            
            // add disabled css class from action dom element
            disable: function(action) {
                if (!action.hasClass('disabled')) {
                    action.addClass('disabled');
                }
                action.attr('href', '#');
                action.unbind();
                action.bind('click', function() {
                    return false;
                });
            },
            
            // execute action
            //
            // action: the action link
            // options: optional execution info, if given, action is ignored.
            execute: function(action, options) {
                var name, ajax, href;
                if (options) {
                    name = options.name;
                    ajax = options.ajax;
                    href = options.href;
                } else {
                    action = $(action);
                    name = action.parent().attr('class');
                    ajax = action.hasClass('ajax');
                    href = action.attr('href');
                }
                finder.actions.name = name;
                
                // set action url. value depends if ajax action or not
                var cb;
                if (ajax) {
                    cb = finder.actions.perform_ajax;
                    finder.actions.url = 'bda.plone.finder.execute?uid=';
                    finder.actions.url += finder.actions.uid;
                    finder.actions.url += '&name=' + finder.actions.name;
                    
                    // consider optional parameters if execute is called 
                    // manually
                    if (options && options.params) {
                        var params = options.params;
                        for (param in params) {
                            finder.actions.url += 
                                '&' + param + '=' + params[param];
                        }
                    }
                } else {
                    cb = finder.actions.follow_action_link;
                    finder.actions.url = action.attr('href');
                }
                
                // execute befor action hook if exists and return
                var hook = finder.hooks.actions[finder.actions.name];
                if (hook) {
                    var func = hook['before'];
                    if (func) {
                        func(finder.actions.uid, finder.actions.column, cb);
                        return;
                    }
                }
                
                // no hook defined for action, execute action performing
                // callback directly
                if (ajax) {
                    finder.actions.perform_ajax();
                } else {
                    finder.actions.follow_action_link();
                }
            },
            
            // follow action link callback for non ajax actions
            follow_action_link: function() {
                document.location.href = finder.actions.url;
            },
            
            // ajax action callback, expected to be called by
            // ``finder.actions.execute`` by action callback
            perform_ajax: function() {
                var actions = finder.actions;
                var url = finder.actions.url;
                finder.request_json(url, function(data) {
                    var container = finder.overlay();
                    var icon_name = 'error_icon.png';
                    if (!data.err) {
                        icon_name = 'info_icon.png';
                        var hook = finder.hooks.actions[actions.name];
                        if (hook) {
                            var func = hook['after'];
                            if (func) {
                                func(actions.uid, actions.column, data);
                            }
                        }
                    }
                    var message = $('div.finder_message_bar', container);
                    var icon = '<img src="++resource++bda.plone.finder.images/';
                    icon += icon_name + '" alt="" />';
                    message.html(icon + data.msg);
                });
            }
        },
        
        // object for finder hooks.
        hooks: {
            
            // hooks executed after actions load
            actions_loaded: {},
            
            // before and after hooks for actions by id
            actions: {}
        }
    };
    
    // set action hook utility function
    $.extend(finder.utils, {
        
        // set autoload and load function
        
        // reload column after action, see below at action hooks
        reload_column_hook: function(uid, container, data) {
            var overlay = finder.overlay();
            var selector = '#finder_nav_item_' + container + ' a.column_expand';
            var elem = $(selector, overlay).get(0);
            finder.query_column(elem, 'bda.plone.finder.expand');
        },
        
        // transitions action extension
        transitions: {
        
            // bind change state action
            bind: function(actions) {
                var overlay = finder.overlay();
                var action = $('div.action_change_state a', overlay);
                action.unbind();
                action.bind('click', function() {
                    if ($(this).hasClass('disabled')) {
                        return false;
                    }
                    finder.utils.transitions.query_transitions(this);
                    return false;
                });
            },
            
            // query transitions and display dropdown
            query_transitions: function(action) {
                if ($(action).hasClass('disabled')) {
                    return false;
                }
                var parent = $(action).parent();
                var dropdown = $('.action_dropdown', parent);
                var uid = finder.current_item;
                var view = 'bda.plone.finder.transitionsmenu';
                finder.dropdown.elem = dropdown;
                finder.dropdown.show(view, uid, function(target) {
                    var url = $(target).attr('href');
                    var idx = url.indexOf('=') + 1;
                    var workflow_action = url.substring(idx, url.length);
                    var options = {
                        name: 'action_change_state',
                        ajax: true,
                        href: '',
                        params: { workflow_action: workflow_action }
                    };
                    finder.actions.execute(null, options);
                });
            }
        }
    });
    
    // set finder hooks for specific actions
    $.extend(finder.hooks.actions, {
        
        // change state action
        action_change_state: {
            
            // no action before change state
            before: null,
            
            // reload after change state action
            after: function(uid, container, data) {
                
                // XXX: remove item and no column rendering if wf change caused
                //      context to be inaccessable (postbox style)
                
                // query new wf state and alter css class
                var url = 'bda.plone.finder.review_state?uid=' + uid;
                finder.request_html(url, function(data) {
                    if (!data) {
                        return;
                    }
                    var parts = data.split(':');
                    var selector = '#finder_nav_item_' + parts[0];
                    var overlay = finder.overlay();
                    elem = $(selector, overlay);
                    var classes = '';
                    $(elem.attr('class').split(' ')).each(function() {
                        if (this.indexOf('state-') == -1) {
                            classes += this + ' ';
                        }
                    });
                    elem.attr('class', classes + 'state-' + parts[1]);
                });
                
                // render details column. skip if details view is actually not
                // shown
                var overlay = finder.overlay();
                var selector = '#finder_column_' + uid + ' ul.columnitems';
                if ($(selector, overlay).length) {
                    return;
                }
                url = 'bda.plone.finder.details?uid=' + uid;
                finder.request_html(url, function(data) {
                    for (var i = 0; i < finder.columns.length; i++) {
                        if (finder.columns[i] == container) {
                            finder.actions.load(uid, container);
                            finder.apply_column(container, data, i);
                        }
                    }
                });
            }
        },
        
        // cut action
        action_cut: {
            
            // no action before cut
            before: null,
            
            // reload column after cut action
            after: finder.utils.reload_column_hook
        },
        
        // delete action
        action_delete: {
            
            // before hook sets original base url, after hook overwrites finder
            // base url if necessary.
            _base_url: null,
            
            // confirm_delete, display confirmation dialog
            before: function(uid, container, callback) {
                finder.dialog.msg = 'Do you really want to delete this item?';
                $.ajax({
                    dataType: 'html',
                    url: 'bda.plone.finder.base_url?uid=' + uid,
                    cache: false,
                    success: function(url) {
                        finder.hooks.actions.action_delete._base_url = url;
                        finder.dialog.show(callback);
                    }
                });
            },
            
            // reload column after delete action
            after: function(uid, container, data) {
                var del_url = finder.hooks.actions.action_delete._base_url;
                if (finder.base_url() == del_url) {
                    $.ajax({
                        dataType: 'html',
                        url: 'bda.plone.finder.base_url?uid=' + container,
                        cache: false,
                        success: function(url) {
                            finder._base_url = null;
                            $('#finder_base_url').html(url);
                            finder.current_focused = container;
                            finder.utils.reload_column_hook(
                                uid, container, data);
                        }
                    });
                } else {
                    finder.utils.reload_column_hook(uid, container, data);
                }
            }
        },
        
        // paste action
        action_paste: {
            
            // no action before paste
            before: null,
            
            // paste_entry, reload column after paste action
            after: function(uid, container, data) {
                var url = 'bda.plone.finder.expand?uid=' + uid;
                finder.request_html(url, function(data) {
                    for (var i = 0; i < finder.columns.length; i++) {
                        if (finder.columns[i] == container) {
                            finder.actions.load(uid, container);
                            finder.apply_column(container, data, i);
                            $('li.cut', finder.scrollable()).remove();
                        }
                    }
                });
            }
        }
    });
    
    // set finder hooks for after actions load
    $.extend(finder.hooks.actions_loaded, {
        
        // rebind add action dropdown with current focused column
        rebind_add_action: function(actions) {
            var overlay = finder.overlay();
            var action = $('div.action_add_item a', overlay);
            action.unbind();
            action.bind('click', function() {
                if ($(this).hasClass('disabled')) {
                    return false;
                }
                var parent = $(this).parent();
                var dropdown = $('.action_dropdown', parent);
                var uid = finder.current_focused;
                finder.dropdown.elem = dropdown;
                finder.dropdown.show('bda.plone.finder.additemsmenu',
                                     uid,
                                     function(target) {
                    document.location.href = target.href;
                });
                return false;
            });
        },
        
        // bind transitions dropdown menu
        bind_tansitions_dropdown: finder.utils.transitions.bind
    });

})(jQuery);