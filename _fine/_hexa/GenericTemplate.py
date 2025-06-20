# ##########################################
# GENERIC TEMPLATE CLASS:
#
# All project setup templates should inherit from this class
#
# VERSION 1.1
# (C) NUMECA INT
# ##########################################

import FHX

from Geom      import *
from IGGSystem import *
from Tk        import *

# ##########################################

class GenericTemplate():

    # ... General information
    author       = "Unknown"
    version      = "Unknown"
    description  = "No description."
    detail       = ""

    # ... Template execution status
    status       = "PENDING"


    # ---------------------------------
    # General methods :
    # used by the GUI to display general
    # information about the template (inherited class).
    # ---------------------------------
    def get_author(self):
        if not FHX.is_batch():
            ## INTERACTIVE MODE
            eval_tcl_string( "global presetter; set presetter(author) \""+self.author+"\"" )

    def get_version(self):
        if not FHX.is_batch():
            ## INTERACTIVE MODE
            eval_tcl_string( "global presetter; set presetter(version) \""+self.version+"\"" )

    def get_description(self):
        if not FHX.is_batch():
            ## INTERACTIVE MODE
            eval_tcl_string( "global presetter; set presetter(description) \""+self.description+"\"" )

    def get_detail(self):
        if not FHX.is_batch():
            ## INTERACTIVE MODE
            eval_tcl_string( "global presetter; set presetter(detail) \""+self.detail+"\"" )
        
    def get_status(self):
        if not FHX.is_batch():
            ## INTERACTIVE MODE
            eval_tcl_string( "global presetter; set presetter(status) \""+self.status+"\"" )

    
    # -----------------------------------
    # Apply() method :
    # must be implemented for each template.
    # ----------------------------------
    def apply(self):
        print 'ERROR: apply(self) method is not implemented !'
        self.status = "_NOT_IMPLEMENTED_"


# ##########################################
#
# END OF IMPLEMENTATION 
#
# ##########################################
