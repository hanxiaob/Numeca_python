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

class TurboTestSuite(BaseTestClass):

    def __init__(self, *args, **kwargs):
        # unittest.TestCase base class instantiates itself this class and checks the args passed in *args, **kwargs
        # --> we cannot add extra args and we need initalize them before base class constructor call:

        self.package  = 'turbo'
        self.this_dir = op.dirname( op.abspath(__file__) )

        super(TurboTestSuite, self).__init__(*args, **kwargs)

    # -----------------------------------------------------------------------------

    def launch_pvm(self):

        # launch pvm daemon through fine
        self.launch_exec('fine',['-batch','-print','-script','dummy'] )

    # -----------------------------------------------------------------------------

    def write_euranus_log(self,log_file):

        with open( log_file, 'r' ) as f:
            self.logger.info('#------------------------------------')
            self.logger.info('         euranus LOG file' )
            self.logger.info('#------------------------------------')
            for line in f.readlines():
                self.logger.info(line.strip(os.linesep))

    # -----------------------------------------------------------------------------

    def test_critical_files(self):

        self.assertEqual( op.exists( op.join( self.version_dir, 'para_schema') ), True )

        #--- Check file or dir existance under COMMON (LINUX) or bin (WINDOWS)
        if os.name == 'posix': common = 'COMMON'
        else:                  common = 'bin'

        self.assertTrue ( op.exists( op.join( self.version_dir, common, 'thermodynamic_tables') ) )
        self.assertTrue ( op.exists( op.join( self.version_dir, common, 'tabgen_fluids') ) )
        self.assertTrue ( op.exists( op.join( self.version_dir, common, 'hexpressfiles','guiconfig.conf') ) )
        self.assertTrue ( op.isdir ( op.join( self.version_dir, '_python','_CFView','cfview_turbowizard') ) )
        self.assertFalse( op.isdir ( op.join( self.version_dir, '_python','_CFView','cfview_turbowizard','cfview_turbowizard') ) )

        # LINUX specific files
        if os.name == 'posix':
            self.assertTrue( op.exists( op.join( self.version_dir, 'LINUX', 'dtkCatiaV5_3dToXmt.exe') ) )
            self.assertTrue( op.exists( op.join( self.version_dir, 'LINUX', '_mpi','_impi2018.1') ) )
            self.assertTrue( op.exists( op.join( self.version_dir, 'LINUX', '_mpi','_ompi2.1.2_gcc48') ) )
            self.assertTrue( op.exists( op.join( self.version_dir, 'LINUX', '_mpi','_ompi2.1.2_icc15') ) )
            self.assertTrue( op.exists( op.join( self.version_dir, 'LINUX', '_mpi','_ompi2.1.2_pgi18') ) )
            self.assertTrue( op.exists( op.join( self.version_dir, 'LINUX', '_python_admin') ) )
            self.assertTrue( op.exists( op.join( self.version_dir, 'LINUX', 'cfview','cfv.so') ) )

    # -----------------------------------------------------------------------------

    def test_fine(self):

        fine_script = op.join(self.this_dir,'fine.py')
        output = self.launch_exec('fine',['-batch','-print','-script',fine_script] )
        
        version_in_file = self.grep1(output,'FINE/Turbo(.*?)-',1) # i.e. FINE/Turbo 13.2a5  -  

        self.assertEqual( version_in_file, expected['package_version'] )

        tcl_file = op.join( self.version_dir, '_tcl/_fine/welcome.tcl' )

        version_in_file = ''

        with open( tcl_file, 'r' ) as f:
            for line in f.readlines():
                m = re.search('set(.*)itf\(version\)(.*)', line)  # set itf(version) 14.1
                if m:
                    version_in_file = m.group(2).strip()
                    break
        self.assertEqual(version_in_file, expected['package_version'])

        #... _tcl/_taskManager/taskDaemon.tcl
        #
        tcl_file = op.join( self.version_dir, '_tcl/_taskManager/taskDaemon.tcl' )

        version_in_file = ''
        with open( tcl_file, 'r' ) as f:
            for line in f.readlines():
                m = re.search('set(.*)version(.*)', line)  # set version 14.1
                if m:
                    version_in_file = m.group(2).strip()
                    break
        self.assertEqual(version_in_file, expected['package_version'])

    # -----------------------------------------------------------------------------

    def test_finebatch(self):

        if sys.platform == "win32":
            finebatch = op.join(self.version_dir,'bin64','finebatchx86_64.exe')
            process = subprocess.Popen ( [finebatch,'-batch'], stdout=subprocess.PIPE , stderr=subprocess.PIPE )
            output, err = process.communicate()
            self.to_log_file(output)  # output command to log file
        else:
            output = self.launch_exec('fine',['-batch','-print'] )

        version_in_file = self.grep1(output,'FINEBATCH(.*)-',1) # <***>   FINEBATCH 13.2a5 ...
        self.assertEqual(version_in_file, expected['package_version'])

    # -----------------------------------------------------------------------------

    def test_igg(self):

        igg_script = op.join(self.this_dir,'igg.py')
        output     = self.launch_exec('igg',['-script',igg_script,'-real-batch','-print'] )

        version_in_file = self.grep1(output,'IGG(.*?)-',1)
        para_version    = self.grep1(output,'Using Parasolid(.*)',1)

        self.assertEqual(version_in_file , expected['package_version'])
        self.assertEqual(para_version    , expected['parasolid_version'])

        script_run_ok = self.grep1(output,'SCRIPT_RETURN_VALUE(.*)',1)
        self.assertEqual(script_run_ok,'1')

    #-----------------------------------------------------------------------------

    def test_cfview(self):

        output = self.launch_exec('cfview',['-batch','-print'] )

        version_in_file = self.grep1(output,'CFView(.*?)-',1)

        self.assertEqual(version_in_file, expected['package_version'])

    #-----------------------------------------------------------------------------

    def test_autoblade(self):
        output = self.launch_exec('autoblade',['-batch','-print'] )
        
        version_in_file = self.grep1(output,'AutoBlade - version(.*)',1)
        self.assertEqual(version_in_file, expected['package_version'])

    #-----------------------------------------------------------------------------

    def test_design3d(self):

        self.launch_pvm()

        run_file = op.join( self.this_dir, 'input','agtb_db_parameterisation','_dbs','agtb.run')
        output = self.launch_exec('design3d',['-print','-run',run_file] )

        version_in_file = self.grep1(output,'Design3D - version(.*)',1)
        self.assertEqual(version_in_file, expected['package_version'])

        geom_turbo = op.join( self.this_dir, 'input','agtb_db_parameterisation','_dbs','_flow_1','agtb.geomTurbo')
        self.assertTrue( op.exists(geom_turbo) )

    #-----------------------------------------------------------------------------

    @unittest.skipIf(sys.platform == 'win32','Only for linux')
    def test_design3d_par(self):

        self.launch_pvm()

        run_file  = op.join( self.this_dir, 'input','agtb_db_Parallel','_dbs','agtb.run')
        p4pg_file = op.join( self.this_dir, 'input','agtb_db_Parallel','_dbs','agtb.p4pg')
        output = self.launch_exec('design3d',['-print','-run',run_file,'-p4pg',p4pg_file] )

        version_in_file = self.grep1(output,'Design3D - version(.*)',1)
        self.assertEqual(version_in_file, expected['package_version'])

        geom_turbo = op.join( self.this_dir, 'input','agtb_db_parameterisation','_dbs','_flow_1','agtb.geomTurbo')
        self.assertTrue( op.exists(geom_turbo) )

        geom_turbo = op.join( self.this_dir, 'input','agtb_db_parameterisation','_dbs','_flow_2','agtb.geomTurbo')
        self.assertTrue( op.exists(geom_turbo) )

    #-----------------------------------------------------------------------------

    def test_design3d_minamo(self):
        run_file  = op.join( self.this_dir, 'input','agtb_db_seq_Minamo_light','_mdb','agtb.run')
        output = self.launch_exec('design3d',['-print','-run',run_file] )

        version_in_file = self.grep1(output,'Design3D - version(.*)',1)
        self.assertEqual(version_in_file, expected['package_version'])

        geom_turbo = op.join( self.this_dir, 'input','agtb_db_seq_Minamo_light','_mdb','_flow_1','agtb.geomTurbo')
        self.assertTrue( op.exists(geom_turbo) )

        geom_turbo = op.join( self.this_dir, 'input','agtb_db_seq_Minamo_light','_mdb','_flow_2','agtb.geomTurbo')
        self.assertTrue( op.exists(geom_turbo) )

        minamo_file = op.join( self.this_dir, 'input','agtb_db_seq_Minamo_light','_mdb','agtb_init.plan')
        self.assertTrue( op.exists(minamo_file) )

    #-----------------------------------------------------------------------------

    def test_sysnoise(self):
        output = self.launch_exec('outputSysnoise',['-print'] )
        version_in_file = self.grep1(output,'SYSNOISE OUTPUT : VERSION(.*)',1)

        self.assertEqual(version_in_file, expected['package_version'])

    #-----------------------------------------------------------------------------

    @unittest.skipIf(sys.platform == 'win32','Only for linux')
    def test_pl2dOutput(self):
        output = self.launch_exec('pl2dOutput',['-print'] )

        version_in_file = self.grep1(output,'PL2D OUTPUT : VERSION(.*)',1)
        self.assertEqual(version_in_file, expected['package_version'])

    #-----------------------------------------------------------------------------

    def _test_fwh(self):
        output = self.launch_exec('fwh',['-print'] )

        version_in_file = self.grep1(output,'FWH OUTPUT : VERSION(.*)',1)
        self.assertEqual(version_in_file, expected['package_version'])

    #-----------------------------------------------------------------------------

    def test_tabgen(self):
        output = self.launch_exec('tabgen',['-batch','-print'] )
        version_in_file = self.grep1(output,'tabgen(.*?)-',1)

        self.assertEqual(version_in_file, expected['package_version'])

    #-----------------------------------------------------------------------------

    def test_taskManager(self):
        output = self.launch_exec('taskManager',['-print'] )
        version_in_file = self.grep1(output,'taskManager(.*)-',1)

        self.assertEqual(version_in_file, expected['package_version'])

    #-----------------------------------------------------------------------------

    def test_hybrid(self):
        output = self.launch_exec('hexpresshybrid',['-print'] )
        version_in_file = self.grep1(output,'HEXPRESS/Hybrid(.*)-',1)

        self.assertEqual(version_in_file, expected['hybrid_version'])

    # -----------------------------------------------------------------------------

    def test_monitor(self):

        output = self.launch_exec('monitor',['-batch','-print'] )

        version_in_file = self.grep1(output,'Monitor(.*)-',1)
        self.assertEqual(version_in_file, expected['package_version'])

    # -----------------------------------------------------------------------------

    @unittest.skipIf(sys.platform == 'win32','Only for linux')
    def test_oofelie(self):
        if os.name == 'posix':
            output = self.launch_exec('oofelie',['-batch','-print'] )
            version_in_file = self.grep1(output,'(V[0-9\.-]+)',1)

            self.assertEqual(version_in_file, expected['oofelie_version'])

    # -----------------------------------------------------------------------------

    def test_minamo(self):
        if sys.platform == "win32":
            output = subprocess.check_output([ op.join(self.version_dir,'minamo','bin','minamoDOE.bat'),'--version'],stderr=subprocess.STDOUT ).rstrip()
            self.to_log_file(output)  # output command to log file
        else:
            output = self.launch_exec('minamoDOE',['-print'] )
            
#        version_in_file = self.grep1(output,'CENAERO Minamo(.*)Revision(.*)',2)
        version_in_file = self.grep1(output,'CENAERO Minamo(.*), Branch(.*)',1)
        self.assertEqual(version_in_file, expected['minamo_version'])

    # -----------------------------------------------------------------------------

    def test_admin(self):
        if sys.platform == "win32":
            output = subprocess.check_output([ op.join(self.version_dir,'admin_tool.exe'),'--version'],stderr=subprocess.STDOUT ).rstrip()
        else:
            output = subprocess.check_output([ op.join(self.version_dir,'LINUX','admin_tool'),'--version'],stderr=subprocess.STDOUT )

        self.to_log_file(output)  # output command to log file
        self.assertEqual( output.strip('\n'), expected['admin_version'] )

    # -----------------------------------------------------------------------------

    def test_flexlm(self):
        if os.name == 'posix':
            flexlm_dir = op.join( self.version_dir, 'LINUX/install/flex64' )
            lmutil     = op.join( flexlm_dir, 'lmutil' )
            igg        = op.join( self.version_dir, 'LINUX','igg','iggx86_64' )
        else:
            flexlm_dir = op.join( self.version_dir, 'flexlm' )
            lmutil     = op.join( flexlm_dir, 'lmutil.exe' )
            igg        = op.join( self.version_dir, 'bin64', 'iggx86_64.exe' )

        output = subprocess.check_output([lmutil,'lmver',igg],stderr=subprocess.STDOUT )
        flex_version = self.grep1(output,'FlexNet Licensing(.*)build',1)
                
        self.assertEqual( flex_version, expected['flexlm_version'] )

    #-----------------------------------------------------------------------------

    @unittest.skipIf(sys.platform == 'win32','Only for linux')
    def test_euranus_intel_impi_seq(self):
        
        self.launch_pvm()

        run_file   = op.join( self.this_dir, 'input', 'input_sequential','input_sequential.run')
        solver_log = op.join( self.this_dir, 'input', 'input_sequential','input_sequential.log')

        output = self.launch_exec('euranusTurbo',[run_file,'-intelmpi','-intel','-print'] )

        if op.exists( solver_log ):
            self.write_euranus_log( solver_log )

        version_in_file = self.grep1(output,'SOLVER VERSION(.*)SINGLE',1)
        self.assertEqual( version_in_file, expected['package_version'] )
        
        self.assertIsNotNone( self.grep(output,'EURANUS/TURBO HAS FINISHED') )

    #-----------------------------------------------------------------------------

    @unittest.skipIf(sys.platform == 'win32','Only for linux')
    def test_euranusdp_intel_impi_seq(self):

        self.launch_pvm()

        run_file   = op.join( self.this_dir, 'input', 'input_sequential','input_sequential.run')
        solver_log = op.join( self.this_dir, 'input', 'input_sequential','input_sequential.log')

        output = self.launch_exec('euranusTurbodp',[run_file,'-intelmpi','-intel','-print'] )

        if op.exists( solver_log ):
            self.write_euranus_log( solver_log )

        version_in_file = self.grep1(output,'SOLVER VERSION(.*)DOUBLE',1)

        self.assertEqual    ( version_in_file, expected['package_version'] )
        self.assertIsNotNone( self.grep(output,'EURANUS/TURBO HAS FINISHED') )

    #-----------------------------------------------------------------------------

    @unittest.skipIf(sys.platform == 'win32','Only for linux')
    def test_euranus_intel_ompi_seq(self):

        self.launch_pvm()

        run_file   = op.join( self.this_dir, 'input', 'input_sequential','input_sequential.run')
        solver_log = op.join( self.this_dir, 'input', 'input_sequential','input_sequential.log')

        output = self.launch_exec('euranusTurbo',[run_file,'-intel','-print'] )

        if op.exists( solver_log ):
            self.write_euranus_log( solver_log )

        version_in_file = self.grep1(output,'SOLVER VERSION(.*)SINGLE',1)

        self.assertEqual    ( version_in_file, expected['package_version'] )
        self.assertIsNotNone( self.grep(output,'EURANUS/TURBO HAS FINISHED') )

    #-----------------------------------------------------------------------------

    @unittest.skipIf(sys.platform == 'win32','Only for linux')
    def test_euranusdp_intel_ompi_seq(self):

        self.launch_pvm()

        run_file   = op.join( self.this_dir, 'input', 'input_sequential','input_sequential.run')
        solver_log = op.join( self.this_dir, 'input', 'input_sequential','input_sequential.log')

        output = self.launch_exec('euranusTurbodp',[run_file,'-intel','-print'] )

        if op.exists( solver_log ):
            self.write_euranus_log( solver_log )

        version_in_file = self.grep1(output,'SOLVER VERSION(.*)DOUBLE',1)

        self.assertEqual    ( version_in_file, expected['package_version'] )
        self.assertIsNotNone( self.grep(output,'EURANUS/TURBO HAS FINISHED') )

    #-----------------------------------------------------------------------------

    @unittest.skipIf(sys.platform == 'win32','Only for linux')
    def test_euranus_pgi_impi_seq(self):

        self.launch_pvm()

        run_file   = op.join( self.this_dir, 'input', 'input_sequential','input_sequential.run')
        solver_log = op.join( self.this_dir, 'input', 'input_sequential','input_sequential.log')

        output = self.launch_exec('euranusTurbo',[run_file,'-intelmpi','-pgi','-print'] )

        if op.exists( solver_log ):
            self.write_euranus_log( solver_log )

        version_in_file = self.grep1(output,'SOLVER VERSION(.*)SINGLE',1)

        self.assertEqual    ( version_in_file, expected['package_version'] )
        self.assertIsNotNone( self.grep(output,'EURANUS/TURBO HAS FINISHED') )

    #-----------------------------------------------------------------------------

    @unittest.skipIf(sys.platform == 'win32','Only for linux')
    def test_euranusdp_pgi_impi_seq(self):

        self.launch_pvm()

        run_file   = op.join( self.this_dir, 'input', 'input_sequential','input_sequential.run')
        solver_log = op.join( self.this_dir, 'input', 'input_sequential','input_sequential.log')

        output = self.launch_exec('euranusTurbodp',[run_file,'-intelmpi','-pgi','-print'] )

        if op.exists( solver_log ):
            self.write_euranus_log( solver_log )

        version_in_file = self.grep1(output,'SOLVER VERSION(.*)DOUBLE',1)

        self.assertEqual    ( version_in_file, expected['package_version'] )
        self.assertIsNotNone( self.grep(output,'EURANUS/TURBO HAS FINISHED') )

    #-----------------------------------------------------------------------------

    @unittest.skipIf(sys.platform == 'win32','Only for linux')
    def test_euranus_intel_impi_par(self):

        self.launch_pvm()

        run_file   = op.join( self.this_dir, 'input', 'input_parallel','input_parallel.run')
        solver_log = op.join( self.this_dir, 'input', 'input_parallel','input_parallel.log')
        
        p4pg = op.join( self.this_dir, 'input', 'input_parallel','input_parallel.p4pg')
        with open(p4pg,'w') as f:
            f.write( socket.gethostname() + ' 2 euranusTurbo' +  self.release_version.replace('.','') + '\n' )

        output = self.launch_exec('euranusTurbo_parallel',[run_file,'-intelmpi','-intel','-print','-p4pg',p4pg] )

        if op.exists( solver_log ):
            self.write_euranus_log( solver_log )

        #mpi_version = self.grep1(output,'MPI VERSION: IMPI(.*)',1)
        #self.assertEqual    ( mpi_version, expected['impi_version'] )

        self.assertIsNotNone( self.grep(output,'EURANUS/TURBO HAS FINISHED') )

    #-----------------------------------------------------------------------------

    @unittest.skipIf(sys.platform == 'win32','Only for linux')
    def test_euranusdp_intel_impi_par(self):

        self.launch_pvm()

        run_file   = op.join( self.this_dir, 'input', 'input_parallel','input_parallel.run')
        solver_log = op.join( self.this_dir, 'input', 'input_parallel','input_parallel.log')
        
        p4pg = op.join( self.this_dir, 'input', 'input_parallel','input_parallel.p4pg')
        with open(p4pg,'w') as f:
            f.write( socket.gethostname() + ' 2 euranusTurbo' +  self.release_version.replace('.','') + '\n' )

        output      = self.launch_exec('euranusTurbodp_parallel',[run_file,'-intelmpi','-intel','-print','-p4pg',p4pg] )

        if op.exists( solver_log ):
            self.write_euranus_log( solver_log )

        mpi_version = self.grep1(output,'MPI VERSION: IMPI(.*)',1)

        self.assertEqual    ( mpi_version, expected['impi_version'] )
        self.assertIsNotNone( self.grep(output,'EURANUS/TURBO HAS FINISHED') )

    #-----------------------------------------------------------------------------

    @unittest.skipIf(sys.platform == 'win32','Only for linux')
    def test_euranus_intel_ompi_par(self):

        self.launch_pvm()

        run_file   = op.join( self.this_dir, 'input', 'input_parallel','input_parallel.run')
        solver_log = op.join( self.this_dir, 'input', 'input_parallel','input_parallel.log')

        p4pg = op.join( self.this_dir, 'input', 'input_parallel','input_parallel.p4pg')
        with open(p4pg,'w') as f:
            f.write( socket.gethostname() + ' 2 euranusTurbo' +  self.release_version.replace('.','') + '\n' )

        output      = self.launch_exec('euranusTurbo_parallel',[run_file,'-intel','-print','-p4pg',p4pg] )

        if op.exists( solver_log ):
            self.write_euranus_log( solver_log )

        #mpi_version = self.grep1(output,'MPI VERSION: OMPI(.*)',1)
        #self.assertEqual( mpi_version, expected['ompi_version'] )

        self.assertIsNotNone( self.grep(output,'EURANUS/TURBO HAS FINISHED') )

    #-----------------------------------------------------------------------------

    @unittest.skipIf(sys.platform == 'win32','Only for linux')
    def test_euranusdp_intel_ompi_par(self):

        self.launch_pvm()

        run_file   = op.join( self.this_dir, 'input', 'input_parallel','input_parallel.run')
        solver_log = op.join( self.this_dir, 'input', 'input_parallel','input_parallel.log')

        p4pg = op.join( self.this_dir, 'input', 'input_parallel','input_parallel.p4pg')
        with open(p4pg,'w') as f:
            f.write( socket.gethostname() + ' 2 euranusTurbo' +  self.release_version.replace('.','') + '\n' )

        output = self.launch_exec('euranusTurbodp_parallel',[run_file,'-intel','-print','-p4pg',p4pg] )

        if op.exists( solver_log ):
            self.write_euranus_log( solver_log )

        mpi_version = self.grep1(output,'MPI VERSION: OMPI(.*)',1)

        self.assertEqual    ( mpi_version, expected['ompi_version'] )
        self.assertIsNotNone( self.grep(output,'EURANUS/TURBO HAS FINISHED') )

    #-----------------------------------------------------------------------------

    @unittest.skipIf(sys.platform == 'win32','Only for linux')
    def test_euranus_no_args_ompi_par(self):
        run_file   = op.join( self.this_dir, 'input', 'input_parallel','input_parallel.run')
        solver_log = op.join( self.this_dir, 'input', 'input_parallel','input_parallel.log')

        p4pg = op.join( self.this_dir, 'input', 'input_parallel','input_parallel.p4pg')
        with open(p4pg,'w') as f:
            f.write( socket.gethostname() + ' 2 euranusTurbo' +  self.release_version.replace('.','') + '\n' )

        output      = self.launch_exec('euranusTurbo_parallel',[run_file,'-print','-p4pg',p4pg] )

        if op.exists( solver_log ):
            self.write_euranus_log( solver_log )

        #mpi_version = self.grep1(output,'MPI VERSION: OMPI(.*)',1)
        #self.assertEqual    ( mpi_version, expected['ompi_version'] )

        self.assertIsNotNone( self.grep(output,'EURANUS/TURBO HAS FINISHED') )

    #-----------------------------------------------------------------------------

    @unittest.skipIf(sys.platform == 'win32','Only for linux')
    def test_euranusdp_no_args_ompi_par(self):
        run_file   = op.join( self.this_dir, 'input', 'input_parallel','input_parallel.run')
        solver_log = op.join( self.this_dir, 'input', 'input_parallel','input_parallel.log')

        p4pg = op.join( self.this_dir, 'input', 'input_parallel','input_parallel.p4pg')
        with open(p4pg,'w') as f:
            f.write( socket.gethostname() + ' 2 euranusTurbo' +  self.release_version.replace('.','') + '\n' )

        output = self.launch_exec('euranusTurbodp_parallel',[run_file,'-print','-p4pg',p4pg] )

        if op.exists( solver_log ):
            self.write_euranus_log( solver_log )

        #mpi_version = self.grep1(output,'MPI VERSION: OMPI(.*)',1)
        #self.assertEqual    ( mpi_version, expected['ompi_version'] )

        self.assertIsNotNone( self.grep(output,'EURANUS/TURBO HAS FINISHED') )

    #-----------------------------------------------------------------------------

    @unittest.skipIf(sys.platform == 'win32','Only for linux')
    def test_euranus_pgi_ompi_par(self):
        run_file   = op.join( self.this_dir, 'input', 'input_parallel','input_parallel.run')
        solver_log = op.join( self.this_dir, 'input', 'input_parallel','input_parallel.log')

        p4pg = op.join( self.this_dir, 'input', 'input_parallel','input_parallel.p4pg')
        with open(p4pg,'w') as f:
            f.write( socket.gethostname() + ' 2 euranusTurbo' +  self.release_version.replace('.','') + '\n' )

        output = self.launch_exec('euranusTurbo_parallel',[run_file,'-pgi','-print','-p4pg',p4pg] )

        if op.exists( solver_log ):
            self.write_euranus_log( solver_log )

        #mpi_version = self.grep1(output,'MPI VERSION: OMPI(.*)',1)
        #self.assertEqual    ( mpi_version, expected['ompi_version'] )

        self.assertIsNotNone( self.grep(output,'EURANUS/TURBO HAS FINISHED') )

    #-----------------------------------------------------------------------------

    @unittest.skipIf(sys.platform == 'win32','Only for linux')
    def test_euranusdp_pgi_ompi_par(self):
        run_file   = op.join( self.this_dir, 'input', 'input_parallel','input_parallel.run')
        solver_log = op.join( self.this_dir, 'input', 'input_parallel','input_parallel.log')

        p4pg = op.join( self.this_dir, 'input', 'input_parallel','input_parallel.p4pg')
        with open(p4pg,'w') as f:
            f.write( socket.gethostname() + ' 2 euranusTurbo' +  self.release_version.replace('.','') + '\n' )

        output = self.launch_exec('euranusTurbodp_parallel',[run_file,'-pgi','-print','-p4pg',p4pg] )

        if op.exists( solver_log ):
            self.write_euranus_log( solver_log )

        #mpi_version = self.grep1(output,'MPI VERSION: OMPI(.*)',1)
        #self.assertEqual    ( mpi_version, expected['ompi_version'] )

        self.assertIsNotNone( self.grep(output,'EURANUS/TURBO HAS FINISHED') )

    #-----------------------------------------------------------------------------

    @unittest.skipIf(sys.platform == 'win32','Only for linux')
    def test_euranus_pgi_impi_par(self):
        run_file   = op.join( self.this_dir, 'input', 'input_parallel','input_parallel.run')
        solver_log = op.join( self.this_dir, 'input', 'input_parallel','input_parallel.log')

        p4pg = op.join( self.this_dir, 'input', 'input_parallel','input_parallel.p4pg')
        with open(p4pg,'w') as f:
            f.write( socket.gethostname() + ' 2 euranusTurbo' +  self.release_version.replace('.','') + '\n' )

        output = self.launch_exec('euranusTurbo_parallel',[run_file,'-intelmpi','-pgi','-print','-p4pg',p4pg] )

        if op.exists( solver_log ):
            self.write_euranus_log( solver_log )

        #mpi_version = self.grep1(output,'MPI VERSION: IMPI(.*)',1)
        #self.assertEqual( mpi_version, expected['impi_version'] )

        self.assertIsNotNone( self.grep(output,'EURANUS/TURBO HAS FINISHED') )

    #-----------------------------------------------------------------------------

    @unittest.skipIf(sys.platform == 'win32','Only for linux')
    def _test_euranus_pgi18_impi_par(self):
        run_file   = op.join( self.this_dir, 'input', 'input_parallel','input_parallel.run')
        p4pg       = op.join( self.this_dir, 'input', 'input_parallel','input_parallel.p4pg')
        solver_log = op.join( self.this_dir, 'input', 'input_parallel','input_parallel.log')

        with open(p4pg,'w') as f:
            f.write( socket.gethostname() + ' 2 euranusTurbo' +  self.release_version.replace('.','') + '\n' )

        output      = self.launch_exec('euranusTurbo_parallel',[run_file,'-intelmpi','-pgi18','-print','-p4pg',p4pg] )

        if op.exists( solver_log ):
            self.write_euranus_log( solver_log )


        if op.exists( solver_log ):
            with open( solver_log, 'r' ) as f:
                for line in f.readlines():
                    self.logger.info(line)

        #mpi_version = self.grep1(output,'MPI VERSION: IMPI(.*)',1)
        #self.assertEqual( mpi_version, expected['impi_version'] )

        self.assertIsNotNone( self.grep(output,'EURANUS/TURBO HAS FINISHED') )

    #-----------------------------------------------------------------------------

    @unittest.skipIf(sys.platform == 'win32','Only for linux')
    def test_euranusdp_pgi_impi_par(self):
        run_file   = op.join( self.this_dir, 'input', 'input_parallel','input_parallel.run')
        solver_log = op.join( self.this_dir, 'input', 'input_parallel','input_parallel.log')

        p4pg = op.join( self.this_dir, 'input', 'input_parallel','input_parallel.p4pg')
        with open(p4pg,'w') as f:
            f.write( socket.gethostname() + ' 2 euranusTurbo' +  self.release_version.replace('.','') + '\n' )

        output = self.launch_exec('euranusTurbodp_parallel',[run_file,'-intelmpi','-pgi','-print','-p4pg',p4pg] )

        if op.exists( solver_log ):
            self.write_euranus_log( solver_log )

        #mpi_version = self.grep1(output,'MPI VERSION: IMPI(.*)',1)
        #self.assertEqual( mpi_version, expected['impi_version'] )

        self.assertIsNotNone( self.grep(output,'EURANUS/TURBO HAS FINISHED') )

#------------------------------------------------------------------------------------------------------------

    @unittest.skipUnless(sys.platform == 'win32','Only for windows')
    def test_euranussp_par_mpich2(self):

        run_file     = op.join( self.this_dir, 'input', 'input_parallel','input_parallel.run')
        machine_file = op.join( self.this_dir, 'input', 'input_parallel','input_parallel.machines')
        
        with open(machine_file,'w') as f:
            f.write( socket.gethostname() + '\n')
            f.write( socket.gethostname() )

        finebatch = op.join(self.version_dir,'bin64','finebatchx86_64.exe')
        process = subprocess.Popen ( [finebatch,'-batch','-parallel','-computation',run_file,'-nproc','2'], stdout=subprocess.PIPE , stderr=subprocess.PIPE )
        output, err = process.communicate()
        self.to_log_file(output)  # output command to log file

        mpiexec = op.join(self.version_dir,'bin64','mpiexec.exe')
        euranus = op.join(self.version_dir,'bin64','euranusx86_64.exe')
        args    = ['-n','3','-localroot','-mapall','-machinefile',machine_file,euranus,run_file]
        
        process = subprocess.Popen ( [mpiexec] + args, stdout=subprocess.PIPE , stderr=subprocess.PIPE )
        output, err = process.communicate()
        self.to_log_file(output)  # output command to log file

        version_in_file = self.grep1(output,'SOLVER VERSION(.*)SINGLE',1)
        self.assertEqual( version_in_file, expected['package_version'] )

        self.assertIsNotNone( self.grep(output,'EURANUS/TURBO HAS FINISHED') )

#-------------------------------------------------------------------------------------------------------------------
# Run and close. !! Do not modify the lines below !!

if __name__ == '__main__':
    main('turbo',TurboTestSuite,expected)
    
