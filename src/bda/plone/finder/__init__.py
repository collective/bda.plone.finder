from Products.CMFCore.permissions import setDefaultRoles


setDefaultRoles('bda.plone.finder: Trigger Finder',
                ('Authenticated', 'Member', 'Manager', 'Site Administrator'))
