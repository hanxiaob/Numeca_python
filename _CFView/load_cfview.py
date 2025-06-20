import os,sys,platform,pdb

NUMECA_DIR=os.getenv('NUMECA_DIR')
CUR_DIR=os.getenv('CUR_DIR')
DEBUG_MACRO=os.getenv('DEBUG_MACRO')
PDB_SET_TRACE=os.getenv('PDB_SET_TRACE')
CFView_args=sys.argv[1:]
interactiveGUI=CFView_args.count('-interactivegui')
loadMarineModule=CFView_args.count('MarineModule')
loadMarineModule+=CFView_args.count('MarineModule.py')

if CUR_DIR != None:
    if not os.path.exists(CUR_DIR):
        print 'Cannot find ',CUR_DIR
        CUR_DIR=None
    
DEBUG_FILE=DEBUG_MACRO
if DEBUG_MACRO != None:
    if not os.path.exists(DEBUG_FILE) and CUR_DIR != None:
        DEBUG_FILE=    CUR_DIR+'/'+DEBUG_FILE
        if not os.path.exists(DEBUG_FILE):
            DEBUG_MACRO=None

DEBUG_PATH=None
DEBUG_NAME=None
if DEBUG_MACRO != None:
    lst=DEBUG_MACRO.split('/')
    DEBUG_NAME=lst[len(lst)-1]
    DEBUG_PATH=os.path.dirname(DEBUG_MACRO)


INIT_CFVIEW_DEBUG_OK=1
START_CFV=1

if NUMECA_DIR != None:
    PLAT=platform.system()
    py_version=platform.python_version()
    ver=py_version[0:3]
    CFVIEW_MODULE_PATH=NUMECA_DIR+'/bin'
    CFVIEW_PYTHON_PATH=NUMECA_DIR+'/_python'
    arch=platform.architecture()[0]

    if PLAT == 'Windows':
        PY_MODULE_EXT='.pyd'
        if arch == '64bit':
            CFVIEW_MODULE_PATH+='64'
    elif PLAT == 'Linux' and arch == '64bit':
        PY_MODULE_EXT='.so'    
        CFVIEW_MODULE_PATH=NUMECA_DIR+'/LINUX/cfview'
    elif PLAT == 'AIX' and arch == '64bit':
        PY_MODULE_EXT='.so'    
        CFVIEW_MODULE_PATH=NUMECA_DIR+'/AIX5/cfview'
    else:
        print 'Platform ',PLAT,'(',arch,') is not supported by CFView Python module'
        INIT_CFVIEW_DEBUG_OK=0

    if INIT_CFVIEW_DEBUG_OK == 1:
        marine_py=CFVIEW_PYTHON_PATH+'/_fine/_marine'
        if os.path.exists(marine_py):
            sys.path.append(marine_py)
        else:
            if loadMarineModule >0:
                errMsg='Fine/Marine python directoty: '+marine_py+' not found'
                print errMsg
                
        CFVIEW_MODULE_FILE=CFVIEW_MODULE_PATH+'/cfv'+PY_MODULE_EXT
        if not os.path.exists(CFVIEW_MODULE_FILE):
            CFVIEW_MODULE_FILE=CFVIEW_MODULE_PATH+'/cfv_d'+PY_MODULE_EXT

        if os.path.exists(CFVIEW_MODULE_FILE):
            print 'Loading module:',CFVIEW_MODULE_FILE
            os.chdir(CFVIEW_MODULE_PATH)
            sys.path.append(CFVIEW_MODULE_PATH)
            if START_CFV == 1:
                from cfv import *
        else:
            print 'Cannot find CFView module: ',CFVIEW_MODULE_FILE
            INIT_CFVIEW_DEBUG_OK=0
else:    
    print 'NUMECA_DIR is not set for initialization of CFView Python module'
    INIT_CFVIEW_DEBUG_OK=0
    
def launch_cfview(CUR_DIR):
    if CUR_DIR != None:
        if os.path.exists(CUR_DIR):
            newArgs = [ '-cur_dir' , CUR_DIR ]
            CFView_args.extend(newArgs)
        else:
            print 'Cannot find ',CUR_DIR
            CUR_DIR=None
    if START_CFV == 1:
        if CFView_args != None:
            InitCFView(*CFView_args)
        else:
            InitCFView()
        

if DEBUG_MACRO == None and interactiveGUI == 0:
    print 'No valid python macro to debug'
else:
    launch_cfview(CUR_DIR)
    if PDB_SET_TRACE != None:
        pdb.set_trace()
    if DEBUG_MACRO != None:
        execfile(DEBUG_MACRO)











