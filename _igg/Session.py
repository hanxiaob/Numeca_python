#--------------------------------------------------------------------------------------------#
#      Numeca International                                                                  #
#         M.P.                                                           Jan 2001            #
#--------------------------------------------------------------------------------------------#

import os,sys

from Project import *
class IGGOutput:
	def write(self,string):
		eval_tcl_string("python_stdout \"" + string + "\" \n" )

#sys.stdout  = IGGOutput()
#sys.stderr  = sys.stdout 

#--------------------------------------------------------------------------------------------#

def error_handler():
#	print 'Error type',sys.exc_info()[0],arg
	print 'Error type',sys.exc_type,sys.exc_value

#--------------------------------------------------------------------------------------------#

def get_igg_version():
	return get_igg_version_()

#--------------------------------------------------------------------------------------------#
#
# By changing the value of "context", all new geometry and grid entities created will have
# a name starting with "context#"

context = ""

class Context:
       	level = []
	def __init__(self,name):
		Context.level.append(name)
		print "Construct",Context.level[-1]
	def __del__(self):
		print "Destruct"

#--------------------------------------------------------------------------------------------#
# Given a name, return the contextual name
#
def get_context_name(name):
	if context == "": return name
	else: return context+"#"+name

#--------------------------------------------------------------------------------------------#

def remove_project_from_disk(proj_name):
    root_name = proj_name[:-4]
    extension = proj_name[-4:]

    if extension != ".igg":
        raise "In remove_project_from_disk: Project name must end with .igg"
    
    os.remove(root_name+".igg")
    os.remove(root_name+".geom")
    os.remove(root_name+".cgns")
    os.remove(root_name+".bcs")
    try:    os.remove(root_name+".meridional")
    except: pass
    try:    os.remove(root_name+".igg.bak")
    except: pass
    try: os.remove(root_name+".geom.bak")
    except: pass
    try: os.remove(root_name+".autosave.igg")
    except: pass
    try: os.remove(root_name+".autosave.geom")
    except: pass

#--------------------------------------------------------------------------------------------#


