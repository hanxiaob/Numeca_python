igg_script_version(2.1)

import os

files_path = os.path.abspath ( os.path.dirname(__file__) )

import_catia_file( os.path.join(files_path,'input','r23sp4.CATPart') )

assert( len( get_all_surfaces() )  == 9 )

print "SCRIPT_RETURN_VALUE",1

