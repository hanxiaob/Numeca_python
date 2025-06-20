#--------------------------------------------------------------------------------------------#
#      Numeca International                                                                  #
#                                                                                            #
#      OpenLabs python module                                                                #
#      Version 1.1                                                                           #
#--------------------------------------------------------------------------------------------#
# Revisions:                                                                                 #
#                                                                                            #
#  DATE		IMPLEMENTATOR		TYPE OF MODIFICATION                                 #
#--------------------------------------------------------------------------------------------#
# 31/07/2013	Herve Stassin		Defect  #18091 fixed.                                #
# 18/05/2018	Herve Stassin		Defect  #33987 fixed.                                #
# 24/08/2018	Herve Stassin		Defect  #34539 fixed.                                #
# 04/10/2018	Herve Stassin		Defect  #35367 fixed.                                #
#--------------------------------------------------------------------------------------------#

import sys
import os
import subprocess
import types

from subprocess import Popen, PIPE, STDOUT

# ------------------------------------------
# Windows only (for registry key access)
if (sys.platform == "win32"): import _winreg
# ------------------------------------------

#def compile(source,platform,blkIdx,precision,logfile):
def compile(*args):

    source   = args[0]
    platform = args[1]
    if (len(args)>2):
        blkIdx    = args[2]
        precision = args[3]
        logfile   = args[4]
    else:
        blkIdx    = ""
        precision = ""
        logfile   = ""

    print 'source    = ' + source
    print 'platform  = ' + platform
    print 'blkIdx    = ' + blkIdx
    print 'precision = ' + precision
    print 'logfile   = ' + logfile

    print '==='
    print '=== OpenLabs library generation'
    print '==='
    
    # ---------------------------------------------------------------------------------------------------------------------
    # Initialize the basename and extension from sourcefilename
    SOURCE_FILE = os.path.abspath(source)
    ##print 'Source file: '+SOURCE_FILE
    file,ext = os.path.splitext(SOURCE_FILE)

    # ---------------------------------------------------------------------------------------------------------------------
    # Initialize <*.log> file (sourcefilename + <.log>)
    if (logfile != ""):
        LOG_FILE = os.path.abspath(logfile)
    else:
        LOG_FILE = file+".log"
    ##print 'Log file:'+str(LOG_FILE)

    # ---------------------------------------------------------------------------------------------------------------------
    # Open <*.log> file (append information)
    flog = open(LOG_FILE,'a')

    if (os.path.exists(SOURCE_FILE) == False):
        print '=== ERROR: could not find source file: '+SOURCE_FILE
        print '=== Abort.'
        flog.write('=== ERROR: could not find source file: '+SOURCE_FILE+'\n')
        flog.write('=== Abort.\n')
        return
        
    PLATFORM = platform
    ##print 'Platform: '+PLATFORM
    if (platform!="WIN32" and platform!="WIN64"):
        print '=== ERROR: platform '+platform+' is not supported. Must be "WIN32" or "WIN64".'
        print '=== Abort.'
        return

    flog.write('===\n')
    flog.write('=== OpenLabs library generation\n')
    flog.write('===\n')


    # ---------------------------------------------------------------------------------------------------------------------
    # Initialize paths for WINDOWS
    #
    # ... This script is supposed to be located in: "fineopenxxx\_python\_hexa\" folder
    apath = os.path.dirname(os.path.abspath(__file__))
    NUMECA_DIR=''
    NUMECA_BIN=''
    NUMECA_DIR = os.path.abspath(os.path.join(apath,"..","..",".."))
    if (platform=="WIN64"):
        NUMECA_BIN = os.path.abspath(os.path.join(NUMECA_DIR,"bin64"))
    else:
        NUMECA_BIN = os.path.abspath(os.path.join(NUMECA_DIR,"bin"))

    # ... Get Microsoft Visual studio paths
    VC_BIN=''
    VC_INC=''
    VC_LIB=''
    VSfolder,isExpress = getMicrosoftVisualStudioInstallationFolder_(platform)

    if (VSfolder!= ''):
        if (platform=="WIN64"):
            # --------------
            # Windows 64bits
            # --------------

            # Standard or Express VISUAL STUDIO 2015
            # ... ... VC_BIN = "C:\\Program Files (x86)\\Microsoft Visual Studio 10.0\\VC\\bin\\amd64"
            # ... ... VC_INC = "C:\\Program Files (x86)\\Microsoft Visual Studio 10.0\\VC\\include"
            # ... ... VC_LIB = "C:\\Program Files (x86)\\Microsoft Visual Studio 10.0\\VC\lib\\amd64"
            VC_BIN = os.path.abspath(os.path.join(VSfolder,"bin","amd64"))
            VC_INC = os.path.abspath(os.path.join(VSfolder,"include"))
            VC_LIB = os.path.abspath(os.path.join(VSfolder,"lib","amd64"))

        else:
            # --------------
            # Windows 32bits
            # --------------

            # Standard or Express VISUAL STUDIO 2015
            # ... ... VC_BIN = "C:\\Program Files (x86)\\Microsoft Visual Studio 10.0\\VC\\bin"
            # ... ... VC_INC = "C:\\Program Files (x86)\\Microsoft Visual Studio 10.0\\VC\\include"
            # ... ... VC_LIB = "C:\\Program Files (x86)\\Microsoft Visual Studio 10.0\\VC\lib"
            VC_BIN = os.path.abspath(os.path.join(VSfolder,"bin"))
            VC_INC = os.path.abspath(os.path.join(VSfolder,"include"))
            VC_LIB = os.path.abspath(os.path.join(VSfolder,"lib"))

        # VISUAL STUDIO 2015 Express:
        # ... Add VSfolder to environment variable 'PATH' : contains some libraries needed by compiler
        if (isExpress==True):
            if VSfolder not in sys.path:
                os.environ["PATH"] += os.pathsep + VSfolder


    # ... Get Microsoft SDKs paths and latest version
    SDK10_INC=''
    SDK10_LIB=''
    SDK10_LIB2=''
    SDK81_INC=''
    SDK81_LIB=''
    latestVersion=''
    SDK10folder,SDK81folder,latestVersion= getMicrosoftSDKsInstallationFolder_(platform)

    if(SDK10folder==''):
        print '=== ERROR: Microsoft SDK 10.0 is required for OpenLabs. \n'
        print 'Abort.\n'
        flog.write('=== ERROR: Microsoft SDK 10.0 is required for OpenLabs. \n')
        flog.write('=== Abort.\n')
        return
    else:
        if(latestVersion==''):
            latestVersion='10.0.10240.0'
        elif(latestVersion[0:3]=='10.'):
            if(len(latestVersion)==10):
                latestVersion = latestVersion+".0"
    
    if (SDK10folder!= ''):
        SDK10_INC = os.path.abspath(os.path.join(SDK10folder,"Include",latestVersion,"ucrt"))
        SDK10_LIB = os.path.abspath(os.path.join(SDK10folder,"Lib",latestVersion,"ucrt","x64"))
        SDK10_LIB2= os.path.abspath(os.path.join(SDK10folder,"Lib",latestVersion,"um","x64"))
        
    if (SDK81folder!= ''):
        SDK81_INC = os.path.abspath(os.path.join(SDK81folder,"Include","um"))
        SDK81_LIB = os.path.abspath(os.path.join(SDK81folder,"Lib","winv6.3","um","x64"))

       
    ################################
    ##print 'NUMECA_DIR:'+NUMECA_DIR
    ##print 'NUMECA_BIN:'+NUMECA_BIN
    ##print 'VC_BIN:'+VC_BIN
    ##print 'VC_INC:'+VC_INC
    ##print 'VC_LIB:'+VC_LIB
    ##print 'SDK_INC:'+SDK_INC
    ##print 'SDK_LIB:'+SDK_LIB
    ################################


    # ---------------------------------------------------------------------------------------------------------------------
    # Check existence of paths
    if (os.path.exists(NUMECA_DIR) == False):
        print '=== ERROR: cannot find NUMECA_DIR directory: '+NUMECA_DIR
        print 'Abort.'
        flog.write('=== ERROR: Cannot find NUMECA_DIR directory '+NUMECA_DIR+'\n')
        flog.write('=== Abort.\n')
        return

    if (os.path.exists(NUMECA_BIN) == False):
        print '=== ERROR: cannot find NUMECA_BIN directory: '+NUMECA_BIN
        print '=== Abort.'
        flog.write('=== ERROR: Cannot find directory '+NUMECA_BIN+'\n')
        flog.write('=== Abort.\n')
        return

    if (os.path.exists(VC_BIN) == False):
        print '=== ERROR: Cannot find \"Visual Studio\" installation directory: '+VC_BIN
        print '=== Abort.'
        flog.write('=== ERROR: Cannot find \"Visual Studio\" directory '+VC_BIN+'\n')
        flog.write('=== Abort.\n')
        return

    if (os.path.exists(VC_INC) == False):
        print '=== ERROR: Cannot find \"Visual Studio\" include folder: '+VC_INC
        print '=== Abort.'
        flog.write('=== ERROR: Cannot find \"Visual Studio\" include folder '+VC_INC+'\n')
        flog.write('=== Abort.\n')
        return

    if (os.path.exists(VC_LIB) == False):
        print '=== ERROR: Cannot find \"Visual Studio\" library folder: '+VC_LIB
        print '=== Abort.'
        flog.write('=== ERROR: Cannot find \"Visual Studio\" library folder '+VC_LIB+'\n')
        flog.write('=== Abort.\n')
        return

    if (os.path.exists(SDK10_INC) == False):
        print '=== ERROR: Cannot find \"Windows 10 SDK\" include folder: '+SDK10_INC
        print '=== Abort.'
        flog.write('=== ERROR: Cannot find \"Windows 10 SDK\" include folder '+SDK10_INC+'\n')
        flog.write('=== Abort.\n')
        return

    if (os.path.exists(SDK10_LIB) == False):
        print '=== : ERROR find \"Windows 10 SDK\" library folder: '+SDK10_LIB
        print '=== Abort.'
        flog.write('=== ERROR: Cannot find \"Windows 10 SDK\" library folder '+SDK10_LIB+'\n')
        flog.write('=== Abort.\n')
        return

    UM_LIB=''
    if (os.path.exists(SDK10_LIB2) == False):
        print '=== WARNING: Cannot find \"Windows 10 SDK\" um library folder: '+SDK10_LIB2
        flog.write('=== WARNING: Cannot find \"Windows 10 SDK\" um library folder '+SDK10_LIB2+'\n')
        if(os.path.exists(SDK81_LIB) == False):
            print '=== WARNING: Cannot find \"Windows 8.1 SDK\" um library folder: '+SDK81_LIB
            flog.write('=== WARNING: Cannot find \"Windows 8.1 SDK\" um library folder '+SDK81_LIB+'\n')
            print '=== Abort.'
            flog.write('=== Abort.\n')
            return
        else:
            UM_LIB=SDK81_LIB
    else:
        UM_LIB=SDK10_LIB2

    # ---------------------------------------------------------------------------------------------------------------------
    # EXTRACT BLOCK INDEX 
    if (blkIdx != ""):
        # FROM ARGUMENT
        bi = blkIdx
    else:
        # FROM SOURCE NAME
        bi = file.split('_')[-1]
    BLOCK_IDX=bi.split('b')[-1]
    ##print 'BLOCK_IDX: '+str(BLOCK_IDX)
    try:
        IDX = int(BLOCK_IDX)
    except ValueError:
        # Wrong source name: must be compileOpenLabs_bxxx.C
        print '=== ERROR: Wrong block index: '+BLOCK_IDX
        print '=== ERROR: Wrong source name: '+source+' \nMust be compileOpenLabs_bi.cpp , with i any integer.'
        print '=== Abort.'
        flog.write('=== ERROR: Wrong block index: '+BLOCK_IDX+'\n')
        flog.write('=== ERROR: Source name: '+source+'.Must be compileOpenLabs_bi.cpp , with i any integer.\n')
        flog.write('=== Abort.\n')
        return

    # ---------------------------------------------------------------------------------------------------------------------

    COMPUTATION_PATH=os.path.dirname(os.path.abspath(source))
    ##print 'COMPUTATION_PATH: '+COMPUTATION_PATH

    OBJECT_FILE=os.path.abspath( os.path.join(COMPUTATION_PATH,file+'.obj') )
    ##print 'OBJECT_FILE: '+OBJECT_FILE

    ##RUN_FILE=''
    ##dirList = os.listdir(COMPUTATION_PATH)
    ##for f in dirList:
    ##    extension = os.path.splitext(f)[1]
    ##    if (extension == '.run'):
    ##        RUN_FILE = os.path.abspath(os.path.join(COMPUTATION_PATH,f))
    ##        break
    ##print 'RUN_FILE: '+RUN_FILE
    ##if (RUN_FILE==''):
    ##    print '=== ERROR: No <*.run> file found in directory '+COMPUTATION_PATH
    ##    print '=== Abort.'
    ##    flog.write('=== ERROR: No <*.run> file found in directory '+COMPUTATION_PATH+'\n')
    ##    flog.write('=== Abort.\n')
    ##    return

    LIB_FILE=os.path.join(COMPUTATION_PATH,'libOL_b'+str(BLOCK_IDX)+'.dll')
    ##print 'LIB_FILE: '+LIB_FILE

    # ---------------------------------------------------------------------------------------------------------------------
    # EXTRACT PRECISION FROM ARGUMENT
    # IF NOT SPECIFIED, EXTRACT IT FROM RUN FILE
    # ---------------------------------------------------------------------------------------------------------------------
    if (precision != ""):
        PRECISION=precision
    else:        
        # ---------------------------------------------------------------------------------------------------------------------
        # EXTRACT PRECISION FROM RUN FILE
        # WARNING: find 'SOLVER_PRECISION', not 'USER_SOLVER_PRECISION'
        # TRIM (remove extra blank spaces + tabs)
        # ---------------------------------------------------------------------------------------------------------------------
        RUN_FILE=''
        dirList = os.listdir(COMPUTATION_PATH)
        for f in dirList:
            extension = os.path.splitext(f)[1]
            if (extension == '.run'):
                RUN_FILE = os.path.abspath(os.path.join(COMPUTATION_PATH,f))
                break
        if (RUN_FILE==''):
            print '=== ERROR: No <*.run> file found in directory '+COMPUTATION_PATH
            print '=== Abort.'
            flog.write('=== ERROR: No <*.run> file found in directory '+COMPUTATION_PATH+'\n')
            flog.write('=== Abort.\n')
            return

        PRECISION="single"
        for line in open(RUN_FILE):
            if "SOLVER_PRECISION" in line:
                tokens = line.split("SOLVER_PRECISION")
                if (len(tokens)==2 and tokens[0]==''):
                    PRECISION=tokens[1].strip()
                    break


    # ---------------------------------------------------------------------------------------------------------------------
    # CLEANING
    # ---------------------------------------------------------------------------------------------------------------------
    if (os.path.exists(OBJECT_FILE)):
        print '=== Cleaning intermediate files...'
        flog.write('=== Cleaning '+OBJECT_FILE+'\n')
        os.remove(OBJECT_FILE)

    if (os.path.exists(LIB_FILE)):
        print '=== Cleaning existing library...'
        flog.write('=== Cleaning '+LIB_FILE+'\n')
        os.remove(LIB_FILE)


    # ---------------------------------------------------------------------------------------------------------------------
    # COMPILING
    # ---------------------------------------------------------------------------------------------------------------------
    flog.write('=== Compiling '+SOURCE_FILE+' , precision: '+PRECISION+'\n')

    SYSTEM_INC  = "-I\""+VC_INC+"\" -I\""+SDK10_INC+"\" "
    NUMECA_INC  = "-I\""+NUMECA_DIR+"\\_lib_i\\_incl\" "
    NUMECA_INC  += "-I\""+NUMECA_DIR+"\\_lib_i\\_incl\\_solver\""
    EXTRA_INC   = "-I\""+NUMECA_DIR+"\\_lib_i\\_extlibs\\_extra_incls\" "
    EXTRA_INC  += "-I\""+NUMECA_DIR+"\\_lib_i\\_extlibs\\_qt\\QtCore\" "
    EXTRA_INC  += "-I\""+NUMECA_DIR+"\\_lib_i\\_extlibs\\_qt\" "
    EXTRA_INC  += "-I\""+NUMECA_DIR+"\\_lib_i\\_extlibs\\_boost\" "
#    EXTRA_INC  += "-I\""+NUMECA_DIR+"\\_lib_i\\_extlibs\\LINUX\\_ompi1.10.4_gcc48\\include\" "
#    EXTRA_INC  += "-I\""+NUMECA_DIR+"\\_lib_i\\_extlibs\\LINUX\\_mpich-1.2.5\include\" "
#    EXTRA_INC  += "-I\""+NUMECA_DIR+"\\_lib_i\\_extlibs\\FlexLM\\v11.9\\machind\""
    if (platform=="WIN64"):
        # Windows 64bits
        EXTRA_INC  += "-I\""+NUMECA_DIR+"\\_lib_i\\_extlibs\\_mpich\\win64_2_1.2.1p1\\include\""
    else:
        # Windows 32bits
        EXTRA_INC  += "-I\""+NUMECA_DIR+"\\_lib_i\\_extlibs\\_mpich\\win32_1_1.2_5\\include\""


    DEF_FLAGS  = "/D \"_CONSOLE\" /D \"NDEBUG\" /D \"WIN32\" /D \"_VISUALC_\" "

    if (platform=="WIN64"):
        # Windows 64bits
        DEF_FLAGS += "/D \"NIWIN64\" "


    DEF_FLAGS += "/D \"NI_MPI\" /D \"OMPI_SKIP_MPICXX\" /D \"USE_NIBigVector\" /D \"NI_IO\" "
    DEF_FLAGS += "/D \"NI_FLEXLM\" /D \"NO_FLECS\" /D \"NI_PVM\" /D \"TIXML_USE_STL\" "
    DEF_FLAGS += "/D \"COMPILE_INSTANCIATE\" /D \"HEXA_ONLY\" /D \"HEXANS\" /D \"HEXA_MODULE\" "
    DEF_FLAGS += "/D \"NI_COMPILE_STANDALONE_SOLVER\" /D \"NI_OMNIS_AG5_INTEGRATION\" /D \"NI_SERIAL_PARTITIONER\" /D \"DLL_OPENLABS\" "
    DEF_FLAGS += "/D \"MPICH_IGNORE_CXX_SEEK\" /D \"MPICH_SKIP_MPICXX\"  "
    DEF_FLAGS += "/D \"floaT=double\" "

    if   PRECISION=="double":  DEF_FLAGS += " /D \"hReal16=double\" /D \"hReal=double\""
    elif PRECISION=="hybrid":  DEF_FLAGS += " /D \"hReal16=double\" /D \"hReal=float\""
    #elif PRECISION=="single":  DEF_FLAGS += " /D \"hReal16=float\"  /D \"hReal=float\""
    
    OTHER_FLAGS  = "/U \"UNICODE\" /O2 /Ob1 /GL /MD /LD /EHsc /wd4290 /wd4018 /wd4099 "
    OTHER_FLAGS += "/wd4101 /wd4244 /wd4267 /wd4305 /wd4311 /wd4661 /wd4715 /wd4996 /nologo"

    # Create compile command to be executed
    CMD  = VC_BIN+"\\cl.exe "+SYSTEM_INC+" "+NUMECA_INC+" "+EXTRA_INC+" "
    CMD += DEF_FLAGS+" "+OTHER_FLAGS+" "
    CMD += "/Fo\""+OBJECT_FILE+"\" /c "+"\""+SOURCE_FILE+"\""
    flog.write(CMD+'\n')

    # Executing command, and retrieve any error message
    print "=== Compiling, platform:"+PLATFORM+", precision:"+PRECISION+" ..."
    p = Popen(CMD, shell=False, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=False)
    output = p.stdout.read()
    if (output != ''):
        print output
        flog.write(output)

    # ---------------------------
    # Check for compilation error
    # ---------------------------
    for word in output.split():
        if (word=="error:" or word=="error" or word=="g++:"):
            print 'COMPILATION ERROR'
            flog.write('=== Abort.\n')
            return

    # ---------------------------------------------------------------------------------------------------------------------
    # LINKING
    # ---------------------------------------------------------------------------------------------------------------------
    flog.write('=== Generating library '+LIB_FILE+' ...\n')

    LIB_PATH  = "/LIBPATH:\""+VC_LIB+"\" /LIBPATH:\""+SDK10_LIB+"\" /LIBPATH:\""+UM_LIB+"\" "
    if (platform=="WIN64"):
        # Windows 64bits
        #LIB_PATH += "/LIBPATH:\""+NUMECA_DIR+"\\_lib_i\\_extlibs\\RogueWave\\T61.M51_rev3\\lib64_MD\" "
        LIB_PATH += "/LIBPATH:\""+NUMECA_DIR+"\\_lib_i\\_extlibs\\_mpich\\win64_2_1.2.1p1\\lib\" "
    else:
        # Windows 32bits
        #LIB_PATH += "/LIBPATH:\""+NUMECA_DIR+"\\_lib_i\\_extlibs\\RogueWave\\T61.M51_rev3\\lib32_MD\" "
        LIB_PATH += "/LIBPATH:\""+NUMECA_DIR+"\\_lib_i\\_extlibs\\_mpich\\win32_1_1.2_5\\lib\" "

    LIB_PATH += "/LIBPATH:\""+NUMECA_BIN+"\""

    HEXSTREAM_LIB = ""
    if (platform=="WIN64"):
        # Windows 64bits
        if   PRECISION=="double":  HEXSTREAM_LIB = "hexstreamlibdpx86_64.lib"
        elif PRECISION=="hybrid":  HEXSTREAM_LIB = "hexstreamlibhpx86_64.lib"
        #elif PRECISION=="single":  HEXSTREAM_LIB = "hexstreamlibspx86_64.lib"
    else:
        # Windows 32bits
        if   PRECISION=="double":  HEXSTREAM_LIB = "hexstreamlibdp.lib"
        elif PRECISION=="hybrid":  HEXSTREAM_LIB = "hexstreamlibhp.lib"
        #elif PRECISION=="single":  HEXSTREAM_LIB = "hexstreamlibsp.lib"

    EXTRA_LIB  = " "

    if (platform=="WIN64"):
        # Windows 64bits
        #EXTRA_LIB += "mpi.lib fmpich2.lib "
        EXTRA_LIB += " "
    else:
        # Windows 32bits
        EXTRA_LIB += "mpich.lib "

    EXTRA_LIB += "user32.lib"

    # Create link command to be executed
    CMD = VC_BIN+"\\link.exe /DLL /LTCG /NOLOGO /FORCE:UNRESOLVED /OUT:"+ "\""+LIB_FILE+"\"" +" "+"\""+OBJECT_FILE+"\""+" \
     /NODEFAULTLIB:\"libcpmt.lib\" /NODEFAULTLIB:\"libcpmtd.lib\" \
     /NODEFAULTLIB:\"LIBCMT.lib\"  /NODEFAULTLIB:\"LIBCMTD.lib\" "+LIB_PATH+" "+HEXSTREAM_LIB+" "+EXTRA_LIB
    flog.write(CMD+'\n')
    
    # Executing command, and retrieve any error message
    print '=== Linking...'
    p = Popen(CMD, shell=False, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=False)
    output = p.stdout.read()
    if (output != ''):
        print output
        flog.write(output)

    # ---------------------------
    # Check for link error
    # On windows, check for error "LNK1181:" (cannot open input file)
    # ---------------------------
    for word in output.split():
        if (word=="error:" or word=="LNK1181:" or word=="g++:"):
            print 'COMPILATION ERROR'
            flog.write('=== Abort.\n')
            return

    # ----------------------
    # Compilation successful
    # ----------------------
    print '=== Done.'
    flog.write('=== Library built successfully.\n')

    flog.close()
    return


# ----------------------------------------------------------------------------------
# WINDOWS platform: get Microsoft Visual Studio 2010 installation folder
# ----------------------------------------------------------------------------------
def getMicrosoftVisualStudioInstallationFolder_(platform):
    
    installPath=''
    isExpress = False;
    
    # -------------------------------
    # Search folder from registry key
    # Try first to get Standard VISUAL STUDIO 2012 installation path.
    # If not found, then try to get VISUAL STUDIO 2012 Express installation path.
    # -------------------------------

    aReg = _winreg.ConnectRegistry(None,_winreg.HKEY_LOCAL_MACHINE)

    if (platform=="WIN64"):

        # Try to get path for Visual Studio C++ 2015 Windows 64 bits
        targ = r"SOFTWARE\Wow6432Node\Microsoft\VisualStudio\14.0\Setup\VC\\"
        try:
            aKey = _winreg.OpenKey(aReg, targ)
            value,type = _winreg.QueryValueEx(aKey, "ProductDir")
            installPath = os.path.abspath(value)
            print 'Found VS2015 folder: ' + installPath
        except WindowsError:
            # Try to get path for Visual Studio C++ 2015 Express Windows 64 bits
            #targ = r"SOFTWARE\Wow6432Node\Microsoft\VCExpress\14.0\Setup\VC\\"
            #try:
            #    aKey = _winreg.OpenKey(aReg, targ)
            #    value,type = _winreg.QueryValueEx(aKey, "ProductDir")
            #    installPath = os.path.abspath(value)
            #    isExpress = True;
            #    print 'Found VS2015 Express folder: ' + installPath
            #except WindowsError:
            print 'Could not get Visual Studio 2015 installation directory.'

    else:

        # Try to get path for Visual Studio C++ 2015 Windows 32 bits
        targ = r"SOFTWARE\Microsoft\VisualStudio\14.0\Setup\VC\\"
        try:
            aKey = _winreg.OpenKey(aReg, targ)
            value,type = _winreg.QueryValueEx(aKey, "ProductDir")
            installPath = os.path.abspath(value)
            print 'Found VS2015 folder: ' + installPath
        except WindowsError:
            # Try to get path for Visual Studio C++ 2015 Express Windows 32 bits
            targ = r"SOFTWARE\Microsoft\VCExpress\14.0\Setup\VC\\"
            try:
                aKey = _winreg.OpenKey(aReg, targ)
                value,type = _winreg.QueryValueEx(aKey, "ProductDir")
                installPath = os.path.abspath(value)
                isExpress = True;
                print 'Found VS2015 Express folder: ' + installPath
            except WindowsError:
                print 'Could not get Visual Studio 2015 installation directory.'

    return installPath,isExpress



# ----------------------------------------------------------------------------------
# WINDOWS platform: get Microsoft SDKs installation folder
# ----------------------------------------------------------------------------------
def getMicrosoftSDKsInstallationFolder_(platform):
    
    installPath81=''
    installPath10=''
    installVersion=''

    # -------------------------------
    # Search folder from registry key.
    # On windows 64 bits:
    #   --> For VS2010 Express: SDK v7.1 package is required.
    #   --> For VS2010 Standard: SDK v7.0A or v7.1 package is required.
    #
    # On windows 32 bits:
    #   --> For VS2010 Express: SDK v7.0A or v7.1 package is required.
    #   --> For VS2010 Standard: SDK v7.0A or v7.1 package is required.
    # -------------------------------

    aReg = _winreg.ConnectRegistry(None,_winreg.HKEY_LOCAL_MACHINE)

    if (platform=="WIN64"):

        # Try to get SDK v10.0 path for Windows 64 bits
        targ = r"SOFTWARE\Wow6432Node\Microsoft\Microsoft SDKs\Windows\v10.0\\"
        try:
            aKey = _winreg.OpenKey(aReg, targ)
            ##value,type = _winreg.QueryValueEx(aKey, "CurrentInstallFolder")
            value,type = _winreg.QueryValueEx(aKey, "InstallationFolder")
            installPath10 = os.path.abspath(value)
            print 'Found SDKs folder: ' + installPath10 
            installVersion,type = _winreg.QueryValueEx(aKey, "ProductVersion")
            print '      SDKs version: ' + installVersion
        except WindowsError:
            # Try to get Windows Kits 10 for Windows 64 bits
            targ = r"SOFTWARE\Wow6432Node\Microsoft\Windows Kits\Installed Roots\\"
            try:
                aKey = _winreg.OpenKey(aReg, targ)
                ##value,type = _winreg.QueryValueEx(aKey, "CurrentInstallFolder")
                value,type = _winreg.QueryValueEx(aKey, "KitsRoot10")
                installPath10 = os.path.abspath(value)
                print 'Found Windows Kits 10 folder: ' + installPath10
            except WindowsError:
                print 'Cannot find Microsoft SDKs 10.0 or Windows Kits 10 installation folder.'

            #targ = r"SOFTWARE\Wow6432Node\Microsoft\Microsoft SDKs\Windows\v10.0A\\"
            #try:
            #    aKey = _winreg.OpenKey(aReg, targ)
            #    ##value,type = _winreg.QueryValueEx(aKey, "CurrentInstallFolder")
            #    value,type = _winreg.QueryValueEx(aKey, "InstallationFolder")
            #    installPath10 = os.path.abspath(value)
            #    print 'Found SDKs folder: ' + installPath10
            #    installVersion,type = _winreg.QueryValueEx(aKey, "ProductVersion")
            #    print '      SDKs version: ' + installVersion
            #except WindowsError:
            #    print 'Cannot find Microsoft SDKs 10.0 or Windows Kits 10 installation folder.'

        # Try to get v8.1 path for Windows 64 bits
        targ = r"SOFTWARE\Wow6432Node\Microsoft\Microsoft SDKs\Windows\v8.1\\"
        try:
            aKey = _winreg.OpenKey(aReg, targ)
            ##value,type = _winreg.QueryValueEx(aKey, "CurrentInstallFolder")
            value,type = _winreg.QueryValueEx(aKey, "InstallationFolder")
            installPath81 = os.path.abspath(value)
            print 'Found SDKs folder: ' + installPath81
        except WindowsError:
            targ = r"SOFTWARE\Wow6432Node\Microsoft\Microsoft SDKs\Windows\v8.1A\\"
            try:
                aKey = _winreg.OpenKey(aReg, targ)
                ##value,type = _winreg.QueryValueEx(aKey, "CurrentInstallFolder")
                value,type = _winreg.QueryValueEx(aKey, "InstallationFolder")
                installPath81 = os.path.abspath(value)
                print 'Found SDKs folder: ' + installPath81
            except WindowsError:
                if (installPath10==''):
                    print 'Cannot find Microsoft SDKs v8.1 installation folder.'

    else:
        print 'Windows 32 bit not supported'

    return installPath10,installPath81,installVersion


# ----------------------------------------------------------------------------------
# WINDOWS platform: get Windows Kits
# ----------------------------------------------------------------------------------
def getMicrosoftWindowsKitsInstallationFolder_(platform):
    
    installPath=''
    
    # -------------------------------
    # Search folder from registry key.
    # On windows 64 bits:
    #   --> For VS2010 Express: SDK v7.1 package is required.
    #   --> For VS2010 Standard: SDK v7.0A or v7.1 package is required.
    #
    # On windows 32 bits:
    #   --> For VS2010 Express: SDK v7.0A or v7.1 package is required.
    #   --> For VS2010 Standard: SDK v7.0A or v7.1 package is required.
    # -------------------------------

    aReg = _winreg.ConnectRegistry(None,_winreg.HKEY_LOCAL_MACHINE)

    if (platform=="WIN64"):

        # Try to get path for Windows 64 bits
        targ = r"SOFTWARE\Wow6432Node\Microsoft\Windows Kits\Installed Roots\\"
        try:
            aKey = _winreg.OpenKey(aReg, targ)
            ##value,type = _winreg.QueryValueEx(aKey, "CurrentInstallFolder")
            value,type = _winreg.QueryValueEx(aKey, "KitsRoot10")
            installPath = os.path.abspath(value)
            print 'Found Microsfot Kits folder: ' + installPath
	except WindowsError:
            print 'Windows kits not found'
    else:
         print 'Windows 32 bit not supported'

    return installPath
