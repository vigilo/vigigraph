# -*- coding: utf-8 -*-

name = u'vigigraph'

project = u'VigiGraph'

pdf_documents = [
        ('util', "util-%s" % name, "%s : Guide d'utilisation" % project, u'Vigilo'),
]

latex_documents = [
        ('util', 'util-%s.tex' % name, u"%s : Guide d'utilisation" % project,
         'AA100004-2/UTI00004', 'vigilo'),
]

execfile("../buildenv/doc/conf.py")
