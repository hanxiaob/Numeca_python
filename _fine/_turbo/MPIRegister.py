#--------------------------------------------------------------------------------------------#
#      Numeca International                                                                  #
#                                                                                            #
#      MPIRegister python module                                                             #
#      Version 1.0                                                                           #
#--------------------------------------------------------------------------------------------#

import sys
import os
import subprocess
import types

# ---
# eval_tcl_string method
# ---
from IGGSystem import *

# ---
# subprocess stuffs
# ---
from subprocess import Popen, PIPE, STDOUT

# ------------------------------------------
# Windows only (for registry key access)
if (sys.platform == "win32"): import _winreg
# ------------------------------------------

def checkUserCredentials( MPI_TYPE ):

    if (sys.platform == "win32"):
        
        if Is64Windows_():
            # ----------------------------------------------------------------------------------------------
            # Initialize paths for WINDOWS 64 bits
            #
            # ... This script is supposed to be located in: "finexxx\_python\_turbo\" folder
            apath = os.path.dirname(os.path.abspath(__file__))
            NUMECA_DIR = os.path.abspath(os.path.join(apath,"..","..",".."))
            # ... Search mpiexec.exe in proper folder:
            NUMECA_BIN = os.path.abspath(os.path.join(NUMECA_DIR,"bin64"))
            if (MPI_TYPE=="IntelMPI"):
                NUMECA_BIN = os.path.abspath(os.path.join(NUMECA_DIR,"impi5"))

            CMD  = os.path.join(NUMECA_BIN,"mpiexec.exe")
            CMD += ' -validate'
            p = Popen(CMD, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=False)
            output = p.stdout.read()
            if "SUCCESS" in output:
                eval_tcl_string("global mpi_register; set mpi_register(validate,result) \"SUCCESS\"")
                return 1
            else:
                eval_tcl_string("global mpi_register; set mpi_register(validate,result) \""+output+"\"")
                return 0

        else:

            # ----------------------------------------------------------------------------------------------
            # Initialize paths for WINDOWS 32 bits
            #
            # MPIRegister.exe :  -validate option does not work with version 1.2.4
            # ==> Search in following registry key information about account/passwd :
            # HKEY_CURRENT_USER/Software/MPICH/
            #   -> Account
            #   -> Password
            # ----------------------------------------------------------------------------------------------

            aReg = _winreg.ConnectRegistry(None,_winreg.HKEY_CURRENT_USER)

            # Try to get user credentials for MPICH
            targ = r"Software\MPICH\\"
            try:
                aKey = _winreg.OpenKey(aReg, targ)
                try:
                    value,type = _winreg.QueryValueEx(aKey, "Account")
                    ##print value
                    value,type = _winreg.QueryValueEx(aKey, "Password")
                    ##print value
                    eval_tcl_string("global mpi_register; set mpi_register(validate,result) \"SUCCESS\"")
                    return 1
                except WindowsError:
                    eval_tcl_string("global mpi_register; set mpi_register(validate,result) \"Could not get user credentials.\"")
                    return 0
            except WindowsError:
                eval_tcl_string("global mpi_register; set mpi_register(validate,result) \"Could not get user credentials.\"")
                return 0

    return 1


def registerUserCredentials( MPI_TYPE ):
    
    if (sys.platform == "win32"):
        
        if Is64Windows_():
            # ----------------------------------------------------------------------------------------------
            # MPI register for WINDOWS 64 bits : execute "mpiexec.exe -register"
            # Ask following information in a separate dos shell:
            #   -> Account
            #   -> Password
            #   -> Password (confirm)
            apath = os.path.dirname(os.path.abspath(__file__))
            NUMECA_DIR = os.path.abspath(os.path.join(apath,"..","..",".."))
            # ... Search mpiexec.exe in proper folder:
            NUMECA_BIN = os.path.abspath(os.path.join(NUMECA_DIR,"bin64"))
            if (MPI_TYPE=="IntelMPI"):
                NUMECA_BIN = os.path.abspath(os.path.join(NUMECA_DIR,"impi5"))
            CMD  = os.path.join(NUMECA_BIN,"mpiexec")
            CMD += ' -register'
            DETACHED_PROCESS = 0x00000008
            p= Popen(CMD, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=False, creationflags=DETACHED_PROCESS)
            p.wait()

        else:
            # ----------------------------------------------------------------------------------------------
            # MPI register for WINDOWS 32 bits : execute "MPIRegister.exe"
            # Ask following information in a separate dos shell:
            #   -> Account
            #   -> Password
            #   -> Password (confirm)
            #   -> Action Persistent (y/n)
            # ----------------------------------------------------------------------------------------------
            apath = os.path.dirname(os.path.abspath(__file__))
            NUMECA_DIR = os.path.abspath(os.path.join(apath,"..","..",".."))
            NUMECA_BIN = os.path.abspath(os.path.join(NUMECA_DIR,"bin"))
            CMD  = os.path.join(NUMECA_BIN,"MPIRegister.exe")
            DETACHED_PROCESS = 0x00000008
            p = Popen(CMD, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=False, creationflags=DETACHED_PROCESS)
            p.wait()



def Is64Windows_():
    if (sys.platform == "win32"):
        return 'PROGRAMFILES(X86)' in os.environ


