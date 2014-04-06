from Products.CMFCore.permissions import setDefaultRoles


setDefaultRoles(
    'bda.plone.finder: Trigger Finder',
    ('Editor', 'Contributor', 'Reviewer', 'Site Administrator', 'Manager'))
