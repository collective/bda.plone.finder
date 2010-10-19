// finder.js
//
// author: Robert Niederreiter
// version: 1.0b4
// license: GPL2

(function($) {
    
    $(document).ready(function() {
        var selector = '#contentview-bda_plone_finder';
        
        // bind finder trigger
        var link = $(selector);
        link.attr('rel', '#bda_finder_overlay');
        link.bind('click', function(event) {
            event.preventDefault();
            $(selector).finder();
        });
        
        // autoload finder if cookie set and not portal_factory context
        var cookie = readCookie('bda.plone.finder');
        if (cookie) {
            var cur_url = document.location.href;
            if (cur_url.indexOf('/portal_factory/') == -1 &&
                cur_url.substring(cur_url.lastIndexOf('/') + 1,
                                  cur_url.length) != 'edit') {
                link.finder();
            }
        }
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
                createCookie('bda.plone.finder', '');
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
            
            // return value of bda.plone.finder cookie. this cookie is expected
            // to be a url if present, not '' and not 'autoload'
            var cookie = readCookie('bda.plone.finder');
            if (cookie && cookie != 'autoload') {
                return cookie;
            }
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
                // XXX: hack, for some reason on finer load time 'disabled'
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
                $(document).bind('mousedown', function(event) {
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
            execute: function(action) {
                action = $(action);
                finder.actions.name = action.parent().attr('class');
                var ajax = action.hasClass('ajax');
                var cb;
                
                // set action url. value depends if ajax action or not
                if (ajax) {
                    cb = finder.actions.perform_ajax;
                    finder.actions.url = 'bda.plone.finder.execute?uid=';
                    finder.actions.url += finder.actions.uid;
                    finder.actions.url += '&name=' + finder.actions.name;
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
        
        // cut_delete_entry_hook, reload column after cut or delete action
        cut_delete_entry_hook: function(uid, container, data) {
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
                createCookie('bda.plone.finder', 'autoload');
                var parent = $(action).parent();
                var dropdown = $('.action_dropdown', parent);
                var uid = finder.current_item;
                var view = 'bda.plone.finder.transitionsmenu';
                finder.dropdown.elem = dropdown;
                finder.dropdown.show(view, uid, function(target) {
                    // XXX: ajaxify
                    document.location.href = target.href;
                });
            }
        }
    });
    
    // set finder hooks for specific actions
    $.extend(finder.hooks.actions, {
        
        // action view
        action_view: {
            
            // reset cookie
            before: function(uid, container, callback) {
                createCookie('bda.plone.finder', '');
                callback();
            },
            
            // view action is a non ajax action, after hooks are never called
            after: null
        },
        
        // edit action
        action_edit: {
            
            // write object location to re-open finder with after edit to
            // cookie
            before: function(uid, container, callback) {
                var url = finder.actions.url;
                url = url.substring(0, url.indexOf('/edit'));
                createCookie('bda.plone.finder', url);
                callback();
            },
            
            // edit action is a non ajax action, after hooks are never called
            after: null
        },
        
        // cut action
        action_cut: {
            
            // no action before cut
            before: null,
            
            // reload column after cut or delete action
            // XXX: seperate cut and delete
            after: finder.utils.cut_delete_entry_hook
        },
        
        // delete action
        action_delete: {
            
            // confirm_delete, display confirmation dialog
            before: function(uid, container, callback) {
                finder.dialog.msg = 'Do you really want to delete this item?';
                finder.dialog.show(callback);
            },
            
            // reload column after cut or delete action
            // XXX: seperate cut and delete
            after: finder.utils.cut_delete_entry_hook
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
                createCookie('bda.plone.finder', 'autoload');
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