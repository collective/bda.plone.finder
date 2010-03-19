jQuery(document).ready(function() {
	var link = jQuery('#siteaction-bda_plone_finder');
	link.attr('rel', '#bda_finder_overlay');
	link.bind('click', function() {
        link.plonefinder();
        return false;
    });
	ploneFinderActionHooks = {
		action_cut: {
			before: null,
			after: ploneFinderCutDeleteEntry
		},
		action_delete: {
            before: ploneFinderConfirmDelete,
            after: ploneFinderCutDeleteEntry
        },
		action_paste: {
            before: null,
            after: ploneFinderPasteEntry
        }
	};
});

jQuery.fn.plonefinder = function() {
	ploneFinder = new PloneFinder();
	var overlay = jQuery('#bda_finder_overlay');
    var overlay_api = jQuery(this).overlay({
        target: overlay,
        expose: {
            color: '#eee',
            loadSpeed: 200,
            onBeforeLoad: function() {
                jQuery.get('bda.plone.finder', function(data) {
					overlay.append(data);
					scrollable_api = jQuery('div.finder_columns',
					                        overlay).scrollable({
						size: 4,
                        api: true,
                        clickable: false
					});
					ploneFinder.scrollable_api = scrollable_api;
					ploneFinder.load();
				});
            }
        },
		onClose: function() {
			jQuery('.finder_container', overlay).remove();
		},
		closeOnClick: false,
        api: true
    });
	ploneFinder.overlay_api = overlay_api;
	overlay_api.load();
}

var ploneFinder = null;

function PloneFinder() {
	
	this.overlay_api = null;
	this.scrollable_api = null;
	this.actions = null;
	this.columns = [];
	this.dialog = null;
	
    this.load = function() {
		this.dialog = new PloneFinderDialog();
		this.dialog.overlay_api = this.overlay_api;
		var idx = 0;
		var lastidx = 0;
		var items = this.scrollable_api.getItems();
		items.each(function() {
			var id = this.id.substring(14, this.id.length);
			if (id) {
				lastidx = idx;
			}
			ploneFinder.columns[idx] = id;
			ploneFinder.bindNavItems(this);
			ploneFinder.bindColumnBatch(this);
			idx++;
		});
		this.initActions(ploneFinder.columns[lastidx],
		                 ploneFinder.columns[lastidx - 1]);
		this.scrollable_api.end(1);
    }
	
	this.bindNavItems = function(column) {
		//jQuery('a.column_expand', column).unbind();
		jQuery('a.column_expand', column).bind('click', function() {
            ploneFinder.renderColumn(this, 'bda.plone.finder.expand');
        });
		//jQuery('a.column_details', column).unbind();
        jQuery('a.column_details', column).bind('click', function() {
            ploneFinder.renderColumn(this, 'bda.plone.finder.details');
        });
	}
	
	this.bindColumnBatch = function(column) {
		var column_uid = jQuery(column).attr('id');
		column_uid = column_uid.substring(14, column_uid.length);
		jQuery('p.col_navigation a', column).unbind();
        jQuery('p.col_navigation a', column).bind('click', function() {
			var page = this.href.substring(this.href.lastIndexOf('/') + 1,
			                               this.href.length);
			var url = 'bda.plone.finder.expand?uid=';
			url += column_uid + '&b=' + page;
			jQuery.get(url, function(data) {
                for (var i = 0; i < ploneFinder.columns.length; i++) {
                    if (ploneFinder.columns[i] == column_uid) {
						var after = ploneFinder.columns[i - 1]
                        ploneFinder.applyColumn(after, data, i - 1);
                    }
                }
            });
			return false;
        });
    }
	
	this.initActions = function(uid, column) {
        this.actions = new PloneFinderActions();
		this.actions.overlay_api = this.overlay_api;
		this.actions.load(uid, column);
    }
	
	this.renderColumn = function(elem, view) {
		var obj_uid = jQuery(elem).parent().attr('id');
        obj_uid = obj_uid.substring(16, obj_uid.length);
		var column_uid = elem.rel.substring(15, elem.rel.length);
        var url = view + '?uid=' + obj_uid;
        jQuery.get(url, function(data) {
			for (var i = 0; i < ploneFinder.columns.length; i++) {
				if (ploneFinder.columns[i] == column_uid) {
					ploneFinder.initActions(obj_uid, column_uid);
					ploneFinder.applyColumn(column_uid, data, i);
				}
			}
        });
	}
	
	this.applyColumn = function(after, data, index) {
		// XXX check if scroll back and do exact seek.
		this.scrollable_api.begin(1);
		var items = this.scrollable_api.getItems();
		var finder_columns = this.scrollable_api.getItemWrap();
		var empty_column = '<div>&nbsp;</div>';
		var to_remove = [];
		for (var i = index; i < this.columns.length - 1; i++) {
			var col = items.get(i + 1);
			if (i < 2) {
				jQuery(col).replaceWith(empty_column);
			} else {
				to_remove[i] = col;
			}
			this.columns[i + 1] = null;
		}
		jQuery(to_remove).remove();
		var after_col = jQuery('#finder_column_' + after, finder_columns);
		after_col.after(data);
		var column_uid = jQuery(data).get(0).id;
		column_uid = column_uid.substring(14, column_uid.length);
		var new_col = jQuery('#finder_column_' + column_uid, finder_columns);
		this.columns[index + 1] = column_uid;
		this.resetColumns(index);
		this.setSelected(after_col, column_uid);
		this.bindNavItems(new_col);
		this.bindColumnBatch(new_col);
		this.scrollable_api.reload().end(1);
	}
	
	this.resetColumns = function(index) {
        var new_columns = [];
        var count = index + 1;
        if (count < 3) {
            count = 3
        }
        for (var i = 0; i <= count; i++) {
            new_columns[i] = this.columns[i];
        }
        this.columns = new_columns;
	}
	
	this.setSelected = function(column, uid) {
		jQuery('li.selected', column).toggleClass('selected');
		jQuery('#finder_nav_item_' + uid, column).toggleClass('selected');
	}
}

var ploneFinderActionHooks = {};

function PloneFinderActions() {
    
    this.uid = null;
	this.column = null;
	this.actions = null;
	this.overlay_api = null;
	this.url = null;
	this.name = null;
	
    this.load = function(uid, column) {
		this.uid = uid;
		this.column = column;
		var container = this.overlay_api.getOverlay();
		var url = 'bda.plone.finder.actioninfo?uid=' + uid;
		var actions = this;
        jQuery.getJSON(url, function(data) {
		    actions.actions = data;
			for (var action_name in actions.actions) {
				var action = jQuery('.' + action_name + ' a', container);
				var url = actions.actions[action_name]['url'];
				var enabled = actions.actions[action_name]['enabled'];
                var ajax = actions.actions[action_name]['ajax'];
                action.attr('href', url);
				if (enabled) {
					actions.enable(action);
				} else {
					actions.disable(action);
				}
				if (ajax && enabled) {
					action.bind('click', function() {
						actions.execute(this);
						return false;
					});
				}
			}
        });
	}
	
	this.enable = function(action) {
		if (action.hasClass('disabled')) {
			action.removeClass('disabled');
		}
		action.unbind();
	}
	
	this.disable = function(action) {
        if (!action.hasClass('disabled')) {
            action.addClass('disabled');
        }
		action.attr('href', '#');
        action.unbind();
        action.bind('click', function() {
			return false;
		});
    }
	
	this.execute = function(action) {
		action = jQuery(action);
		this.name = action.parent().attr('class');
		this.url = 'bda.plone.finder.execute?uid=' + this.uid;
		this.url += '&name=' + this.name;
		var hook = ploneFinderActionHooks[this.name];
        if (hook) {
            var func = hook['before'];
            if (func) {
                func(this.uid, this.column, this.performAction);
                return;
            }
        }
        this.performAction();
	}
	
	this.performAction = function() {
		var actions = ploneFinder.actions;
		var url = ploneFinder.actions.url;
		jQuery.getJSON(url, function(data) {
            var container = actions.overlay_api.getOverlay();
            var message = jQuery('div.finder_message', container);
            message.html(data.msg);
            if (!data.err) {
                var hook = ploneFinderActionHooks[actions.name];
		        if (hook) {
		            var func = hook['after'];
		            if (func) {
		                func(actions.uid, actions.column, data);
		            }
		        }
            }
            message.fadeIn('slow', function() {
                setTimeout(function() {
                    message.fadeOut('slow', function() {
                        message.empty();
                    });
                }, 1000);
            });
        });
	}
}

function PloneFinderDialog() {

	this.overlay_api = null;
	this.msg = 'You see a dialog with an unset message';
	
	this.dialog = function() {
		return jQuery('div.finder_dialog', this.overlay_api.getOverlay());
	}
	
	this.show = function(callback) {
		var dialog = this.dialog();
		jQuery('.text', dialog).html(this.msg);
		jQuery('button', dialog).unbind();
		jQuery('button.submit', dialog).bind('click', function() {
			dialog.hide();
			callback();
		});
		jQuery('button.cancel', dialog).bind('click', function() {
			dialog.hide();
		});
		dialog.fadeIn('fast')
	}
	
	this.hide = function() {
		this.dialog().fadeOut('fast');
	}
}

/* before action hooks */

ploneFinderConfirmDelete = function(uid, container, callback) {
    ploneFinder.dialog.msg = 'Do you really want to delete this item?';
    ploneFinder.dialog.show(callback);
}

/* after action hooks */

ploneFinderCutDeleteEntry = function(uid, container, data) {
	var overlay = ploneFinder.overlay_api.getOverlay()
	var selector = '#finder_nav_item_' + container + ' a.column_expand';
	var elem = jQuery(selector, overlay).get(0);
	ploneFinder.renderColumn(elem, 'bda.plone.finder.expand');
}

ploneFinderPasteEntry = function(uid, container, data) {
    var url = 'bda.plone.finder.expand?uid=' + uid;
    jQuery.get(url, function(data) {
        for (var i = 0; i < ploneFinder.columns.length; i++) {
            if (ploneFinder.columns[i] == container) {
                ploneFinder.initActions(uid, container);
                ploneFinder.applyColumn(container, data, i);
            }
        }
    });
}