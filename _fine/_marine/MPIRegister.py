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

def checkUserCredentials():
    if (sys.platform == "win32"):
        apath = os.path.dirname(os.path.abspath(__file__))
        NUMECA_DIR = os.path.abspath(os.path.join(apath,"..","..",".."))
        NUMECA_BIN = os.path.abspath(os.path.join(NUMECA_DIR, "bin", "isis64"))
        CMD  = os.path.join(NUMECA_BIN, "mpiexec.exe") + ' -validate'
        p = Popen(CMD, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=False)
        output = p.stdout.read()

        if "SUCCESS" in output:
            eval_tcl_string("global mpi_register; set mpi_register(validate,result) \"SUCCESS\"")
            return 1
        else:
            eval_tcl_string("global mpi_register; set mpi_register(validate,result) \""+output+"\"")
            return 0

    return 1

def registerUserCredentials():
    if (sys.platform == "win32"):
        apath = os.path.dirname(os.path.abspath(__file__))
        NUMECA_DIR = os.path.abspath(os.path.join(apath,"..","..",".."))
        NUMECA_BIN = os.path.abspath(os.path.join(NUMECA_DIR, "bin", "isis64"))
        CMD  = os.path.join(NUMECA_BIN, "mpiexec.exe") + ' -register'
        DETACHED_PROCESS = 0x00000008
        p = Popen(CMD, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=False, creationflags=DETACHED_PROCESS)
        p.wait()


