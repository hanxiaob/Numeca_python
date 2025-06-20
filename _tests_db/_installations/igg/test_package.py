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

class IGGTestSuite(BaseTestClass):

    def __init__(self, *args, **kwargs):
        self.package = 'igg'
        self.this_dir = op.dirname( op.abspath(__file__) )  # init BEFORE base class constructor call

        super(IGGTestSuite, self).__init__(*args, **kwargs)

    # -----------------------------------------------------------------------------

    def test_critical_files(self):

        self.assertEqual( op.exists( op.join( self.version_dir, 'para_schema') ), True )

        #--- Check file or dir existance under COMMON (LINUX) or bin (WINDOWS)
        if os.name == 'posix': common = 'COMMON'
        else:                  common = 'bin'

        # LINUX specific files
        if os.name == 'posix':
            self.assertTrue( op.exists( op.join( self.version_dir, 'LINUX', 'dtkCatiaV5_3dToXmt.exe') ) )

    # -----------------------------------------------------------------------------

    def test_igg(self):
        # Test igg launch and catia V5 import
        # 
        
        igg_script = op.join(self.this_dir,'igg.py')
        output     = self.launch_exec('igg',['-script',igg_script,'-real-batch','-print'] )

        version_in_file = self.grep1(output,'IGG(.*?)-',1)
        para_version    = self.grep1(output,'Using Parasolid(.*)',1)

        self.assertEqual(version_in_file , expected['package_version'])
        self.assertEqual(para_version    , expected['parasolid_version'])

        script_run_ok = self.grep1(output,'SCRIPT_RETURN_VALUE(.*)',1)
        self.assertEqual(script_run_ok,'1')

#-------------------------------------------------------------------------------------------------------------------
# Run and close. !! Do not modify the lines below !!

if __name__ == '__main__':

    main('igg',IGGTestSuite,expected)
