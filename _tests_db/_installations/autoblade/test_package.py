#-*- coding: utf-8 -*-

import os, sys
import os.path as op
import unittest
import subprocess
import re
import socket
import shutil
import logging
import fileinput

#-------------------------------------------------------------------------------------------------------------------

sys.path.append( op.dirname( op.dirname(os.path.abspath(__file__)) ) )   #  import relative to parent dir

from common import BaseTestClass, main

#-------------------------------------------------------------------------------------------------------------------

expected = {
    'package_version'    : '14.2',
    'hybrid_version'     : '8.2-3',
    'flexlm_version'     : 'v11.14.0.2',
    'admin_version'      : '2019.5',
    'parasolid_version'  : 'V31.0.203',
    'qt_version'         : '14.2',
    'ompi_version'       : '2.1.2',
    'impi_version'       : '2018.0.1',
    'oofelie_version'    : 'V4.3-20',
    'minamo_version'     : '2.10.0',
}

#-------------------------------------------------------------------------------------------------------------------

class AutobladeTestSuite(BaseTestClass):

    def __init__(self, *args, **kwargs):
        self.package = 'autoblade'
        self.this_dir = op.dirname( op.abspath(__file__) )  # init BEFORE base class constructor call

        super(AutobladeTestSuite, self).__init__(*args, **kwargs)

    # -----------------------------------------------------------------------------

    def test_critical_files(self):

        self.assertEqual( op.exists( op.join( self.version_dir, 'para_schema') ), True )

    #-----------------------------------------------------------------------------

    def test_autoblade(self):
        output = self.launch_exec('autoblade',['-batch','-print'] )
        
        version_in_file = self.grep1(output,'AutoBlade - version(.*)',1)
        self.assertEqual(version_in_file, expected['package_version'])

#-------------------------------------------------------------------------------------------------------------------
# Run and close. !! Do not modify the lines below !!

if __name__ == '__main__':

    main('autoblade',AutobladeTestSuite,expected)
