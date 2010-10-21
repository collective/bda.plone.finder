from Products.Five import BrowserView
from bda.plone.finder.browser.utils import get_provider

class AjaxColumn(BrowserView):
    """Class to render a navigation or details column by uid via XML HTTP
    request.
    """
    
    @property
    def flavor(self):
        return self.request.get('flavor', 'default')
    
    def expandColumn(self):
        self.request['_skip_selection_check'] = True # XXX: ?? get rid of
        return self._render('finder_column')
    
    def detailsColumn(self):
        return self._render('finder_details')
    
    def _render(self, view):
        uid = self.request.get('uid')
        provider = get_provider(self.context, self.flavor, uid)
        if provider is not None:
            return provider.render(uid, view)
        return u'<div class="finder_column"></div>'