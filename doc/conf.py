# -*- coding: utf-8 -*-
# Copyright (C) 2011-2012 CS-SI
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

name = u'vigigraph'

project = u'VigiGraph'

pdf_documents = [
        ('admin', "admin-%s" % name, "%s : Guide d'administration" % project, u'Vigilo'),
        ('util', "util-%s" % name, "%s : Guide d'utilisation" % project, u'Vigilo'),
]

latex_documents = [
        ('admin', 'admin-%s.tex' % name, u"%s : Guide d'administration" % project,
         'AA100004-2/ADM00006', 'vigilo'),
        ('util', 'util-%s.tex' % name, u"%s : Guide d'utilisation" % project,
         'AA100004-2/UTI00004', 'vigilo'),
]

execfile("../buildenv/doc/conf.py")
