# -*- coding: utf-8 -*-

import sys
import os
import os.path as op
import unittest
import subprocess
import re
import socket
import shutil
import logging
import traceback
import time
from optparse import OptionParser

#-------------------------------------------------------------------------------------------------------------------

class InstallationTestLogger(object):

    class IOMultiplexer(object):
        """The unittest TestRunner outputs to one stream only. But we want to output to stdout & to a file.
        --> create a IOMultiplexer class that outputs to both, and that is passed as streaming object to unittest.TextTestRunner
        """
    
        def __init__(self,outfile):
            self.terminal = sys.stdout
            self.outfile = open(outfile,'a+')

        def __del__(self):
            self.outfile.close()

        def write(self,string):
            self.terminal.write(string)
            self.outfile.write(string)

        def flush(self):
            self.terminal.flush()
            self.outfile.flush()

    def __init__(self,logs_dir):

        if op.exists( logs_dir ):
            shutil.rmtree( logs_dir )
        os.mkdir( logs_dir )

        file_handler = logging.FileHandler(op.join(logs_dir,'LAUNCH_LOG.txt'))
        logging.root.addHandler(file_handler)
        logging.root.setLevel(logging.DEBUG)

        #... output multiplexer (will be used by unittests)
        #
        out_result_file = op.join(logs_dir,'all_results.txt')
        multiplex_stream = InstallationTestLogger.IOMultiplexer( out_result_file )

        #... Result logger
        #
        result_logger = logging.getLogger("result_logger")
        result_logger.setLevel(logging.DEBUG)
        result_logger.propagate = False
        result_logger.addHandler( logging.StreamHandler(multiplex_stream) )    # log to stdout

        self.result_logger    = result_logger
        self.multiplex_stream = multiplex_stream

#-------------------------------------------------------------------------------------------------------------------

class BaseTestClass(unittest.TestCase):

    test_db = 'to_be_overloaded_in_derived_class'    # must point to an 'input' directory
    log_dir = 'to_be_specified'
    
    def __init__(self, *args, **kwargs):
        super(BaseTestClass, self).__init__(*args, **kwargs)

        # self.this_dir MUST be defined by derived class BEFORE this constructor is called

    def setUp(self):

        # This script is supposed to be under _python/_tests_db/_installations/open
        self.version_dir         = op.dirname( op.dirname( op.dirname( op.dirname( op.abspath(__file__) ) ) ) )
        self.numeca_multiversion = op.dirname( self.version_dir )
        self.release_version     = op.basename(self.version_dir).replace('fine','').replace('hexpress','').replace('autoblade','').replace('cfview','').replace('autogrid','')

        os.environ['PATH'] = op.join( self.numeca_multiversion, 'bin') + ':' + os.environ['PATH']

        logging.info('BaseTestClass::setUp db input dir: {}'.format(BaseTestClass.test_db) )

        if BaseTestClass.test_db == 'to_be_overloaded_in_derived_class':
            raise Exception("BaseTestClass.test_db must be overloaded in derived class")

        if not op.exists( op.join(self.this_dir,'input') ) and op.exists( op.join( BaseTestClass.test_db ) ):
            shutil.copytree( op.join( BaseTestClass.test_db ), op.join(self.this_dir,'input') )

        #... Instanticate special logging for each test (output of the execs)

        self.logger = logging.getLogger(self._testMethodName)
        file_handler = logging.FileHandler( op.join( BaseTestClass.log_dir, self._testMethodName + '.txt' ) )
        self.logger.addHandler(file_handler)
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False

    # -----------------------------------------------------------------------------
    # Utility functions

    def launch_exec(self,soft_name,args):
        """Launch the soft using full pathname (link to numeca_start under bin)

        @param soft_name: software name (i.e. hexpress, fine,...)
        @param args: list of parameters (must be compatible with subprocess requirements)
        
        @return: output from the shell, as multiline string
        """

        if sys.platform == "win32":
            if soft_name == 'taskManager':      soft_name = 'nitaskmgr'
            if soft_name == 'openLabsCreator_': soft_name = 'openlabscreator'
            the_exec = op.join(self.version_dir,'bin64',soft_name + 'x86_64.exe')
        else:
            soft_name = soft_name.replace('fine_open','fine') 
            soft_name = soft_name.replace('fine_marine','fine') 
            the_exec = op.join(self.numeca_multiversion,'bin',soft_name + self.release_version)

        logging.info(' '.join([the_exec] + args) )

        try:
            process = subprocess.Popen ( [the_exec] + args, stdout=subprocess.PIPE , stderr=subprocess.PIPE )
            output, err = process.communicate()
        except:
            traceback.print_exc(file=sys.stdout)

            # It may happen that the launch command fails for obscure reasons. We take a second chance here
            time.sleep(10) 
            process = subprocess.Popen ( [the_exec] + args, stdout=subprocess.PIPE , stderr=subprocess.PIPE )
            output, err = process.communicate()

        self.to_log_file(output)  # output command to log file

        return output

    # -----------------------------------------------------------------------------
    # Utility functions

    def launch_ecn(self,soft_name,args):
        """Launch the soft using full pathname (link to numeca_start under bin)

        @param soft_name: software name (i.e. hexpress, fine,...)
        @param args: list of parameters (must be compatible with subprocess requirements)
        
        @return: output from the shell, as multiline string
        """
        
        if sys.platform == "win32":
            if soft_name == 'hxp2isis_no_interactive' : soft_name = 'hexpress2isis_no_interactive'
            if soft_name == 'isis2cfv_no_interactive' : soft_name = 'isis2cfview_no_interactive'
            the_exec = op.join(self.version_dir,'bin','isis64',soft_name + '.exe')
        else:
            the_exec = op.join(self.numeca_multiversion,'bin',soft_name + self.release_version)

        logging.info(' '.join([the_exec] + args) )

        try:
            if sys.platform == "win32":
                process = subprocess.Popen ( [the_exec] + args, stdout=subprocess.PIPE , stderr=subprocess.PIPE )
                output, err = process.communicate()
            else:
                # On LINUX we use check_output, because of instaliblities with subprocess.Popen and its output
                # (got weird behaviour at times)
                output = subprocess.check_output([the_exec] + args,stderr=subprocess.STDOUT )
        except:
            traceback.print_exc(file=sys.stdout)

        self.to_log_file(output)  # output command to log file
        
        return output

    #-----------------------------------------------------------------------------

    def grep(self,lines,regexp):
        """Search for regexp (or string) in lines

        @param lines: multiline string with os.linesep
        @param regexp: python regular expression
        
        @return: matched line or None if no match is found
        """

        for line in lines.split(os.linesep):
            m = re.search(regexp, line)
            if m:
                return line
        return None

    #-----------------------------------------------------------------------------

    def grep1(self,lines,regexp,position):
        """ Grep the lines and check for regexp match. Returns the ith match
        
        @param lines: multiline string with os.linesep
        @param regexp: python regular expression
        @param position: position of the match to return
        
        @return: string or None if no match is found
        """
        for line in lines.split(os.linesep):
            m = re.search(regexp, line)  # set itf(version) 14.1
            if m:
                return m.group(position).strip()
        return None

    #-----------------------------------------------------------------------------

    def to_log_file(self,lines):
        """Output the lines to the log

        @param lines: multiline string
        """
        for line in lines.split(os.linesep):
            self.logger.debug(line)

#-------------------------------------------------------------------------------------------------------------------

def main(package,TestSuite,expected):
    """Will be called in test_package.py of each package

    @param package: turbo, open, igg, cfview, ....
    """

    os.environ['DISPLAY'] = ''  #disable the display for some exec like hexpressview, which would otherwise popup

    if sys.platform == "win32":
        test_db_root = 'Y:\\tests\\installations'
    else:
        test_db_root ='/develop/tests/installations'

    test_db_data = op.join( test_db_root, package, 'input' )
    logs_dir     = op.join( op.dirname( op.abspath(__file__) ), package, '_logs' )

    parser = OptionParser()
    parser.add_option( '-l', '--log-dir', dest='log_dir'           , default=logs_dir    , help='Specify the result log directory' )
    parser.add_option(       '--db-data', dest='database_data_path', default=test_db_data, help='Path to the centralized python tests data' )

    (argv,args) = parser.parse_args()
    BaseTestClass.test_db = argv.database_data_path
    BaseTestClass.log_dir = argv.log_dir

    loggers = InstallationTestLogger( argv.log_dir )

    suite = unittest.TestLoader().loadTestsFromTestCase( TestSuite )

    #... output the expected versions for each exec
    #
    result_logger = loggers.result_logger
    result_logger.info(" EXPECTED versions:")
    result_logger.info(" ------------------")

    for (key,val) in expected.iteritems():
        result_logger.info("{:<20} : {}".format(key,val))

    #... launch the unittests
    #
    result_logger.info("\n--- START EXEC TESTS ---\n")
    unittest.TextTestRunner(verbosity=2,stream=loggers.multiplex_stream).run(suite)
    result_logger.info("\n--- END EXEC TESTS ---\n")

    #python -m unittest test_package.InstallationTestSuite.test_license
