#--------------------------------------------------------------------------------------------#
#      Numeca International                                                                  #
#                                                                                            #
#      Plot data from TABGen/Chemistry output file                                           #
#      Version 1.1                                                                           #
#--------------------------------------------------------------------------------------------#
# Revisions:                                                                                 #
#                                                                                            #
#  DATE		IMPLEMENTATOR		TYPE OF MODIFICATION                                 #
#--------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------#


#-----------------
# Python libraries
#-----------------
import matplotlib.pyplot as plt
from   matplotlib.ticker import MultipleLocator, FormatStrFormatter

from pylab import *
from math  import *
from numpy import *
from Tk    import *

import sys

#-----------------
# TABGenPlot module
#-----------------
class TABGenPlot():

      # -----------------------------------------------
      # Variables definition
      # -----------------------------------------------

      # ... BLT graph widget
      widget           = None

      # ... Data points
      name_of_variable = 'unknown'
      units            = '[unknown]'
      XVector          = []
      YVector          = []

      # ... Any error message
      errMessage       = ''

      # -----------------------------------------------
      # Methods
      # -----------------------------------------------

      def __init__(self, graphWidget):
            self.widget = graphWidget

      def readData(self,*args):
            print 'TABGenPlot, readData() ... IN'
            print 'Arguments:'
            nArgs=len(args)
            for i in range(nArgs):
                  print '   -> ',args[i]

            self.errMessage = ''

            # ---
            # Initialize options from arguments
            # ---
            options = []
            self.read_calling_arguments(args,options)

            pathstring     = options[0]
            tablestring    = options[1]
            variablestring = options[2]
            ivariable      = options[3]
            itemperature   = options[4]
            idensity       = options[5]
            iviscosity     = options[6]
            ienthalpy      = options[7]
            imfvar         = options[8]
            iprogvar       = options[9]
            ifull          = options[10]
            istrain        = options[11]
            ihelp          = options[12]
            iprogvarplot   = options[13]
            imf            = options[14]
            indx_mf        = options[15]
            indx_mfvar     = options[16]
            indx_strain    = options[17]
            indx_progvar   = options[18]
            indx_enthalpy  = options[19]

            if ivariable:
                  self.name_of_variable = variablestring
            elif itemperature:
                  self.name_of_variable = 'Temperature'
            elif idensity: 
                  self.name_of_variable = 'Density'
            elif iviscosity:
                  self.name_of_variable = 'Viscosity'
            else:
                  print 'TABGenPlot.readData(): missing choice of dep. variable to plot.'
                  print 'Data reading aborted !'
                  return -1

            if ihelp:
                  # Display available options
                  self.printUsage()
                  return 0


            # ---
            # Initialize variable unit
            # ---
            if self.name_of_variable == 'Temperature':
                  self.units = 'K'

            elif self.name_of_variable == 'Density':
                  self.units = 'kg/m3'

            elif self.name_of_variable == 'Density':
                  self.units = 'Pa.s'

            else:
                  self.units = ''


            # ---
            # Open table for reading
            # ---
            FileOpen = open(tablestring, 'r')

            # ... Overread first line in combustion-table file
            FileOpen.readline()

            # ... Second line contains information on dimensions
            FileLineDimension = FileOpen.readline()
            # ... ... Call routine for reading dimensions
            outputlistDim = []
            rc = self.read_dimensions(FileLineDimension, outputlistDim)
            if (rc != 1):
                  print 'Data reading aborted !'
                  self.errMessage += 'Data reading aborted.'
                  self.showErrorMessage()
                  return -1
            
            infmean    = outputlistDim[0]
            infvar     = outputlistDim[1]
            insd       = outputlistDim[2]
            inprogvar1 = outputlistDim[3]
            ined       = outputlistDim[4]
            insl       = outputlistDim[5]
            nfmean     = outputlistDim[6]
            nfvar      = outputlistDim[7]
            nsd        = outputlistDim[8]
            nprogvar1  = outputlistDim[9]
            ned        = outputlistDim[10]
            nsl        = outputlistDim[11]

            # ... Third line contains information on the variable names
            FileLineVarNames = FileOpen.readline()
            # ... ... Call routine for reading variable position
            outputlistVar = []
            iposition = -1
            print self.name_of_variable
            self.read_position(FileLineVarNames, self.name_of_variable, outputlistVar)
            iposition = outputlistVar[0]
            if iposition == -1:
                  print 'TABGenPlot.readData(): dep. variable '+self.name_of_variable+' could not found.'
                  print 'Data reading aborted !'
                  return -2

            ni1=0
            nj1=0
            nk1=0
            nl1=0

            ni2=nfmean
            nj2=1
            nk2=1
            nl2=1

            indep_var_name=' '
            if ifull :
                  nl2=ned
                  nk2=max(nsd,nprogvar1)
                  nj2=nfvar
                  ni2=nfmean
                  if nfmean > 1:
                        indep_var_name = 'f'
                  if nfvar >1:
                        indep_var_name += ', fvar'
                  if nsd >1:
                        indep_var_name += ', strain'
                  if nprogvar1 >1:
                        indep_var_name += ', pv'
                  if ned >1:
                        indep_var_name += ', h'
            elif iprogvarplot:
                  indep_var_name = 'pv'
                  ni2=1
                  nk2=nprogvar1   
                  if imf and indx_mf == -1:
                        indep_var_name += ', f'
                        ni2=nfmean
                  if indx_mf != -1: 
                        ni1 = max(1,min(nfmean,indx_mf))-1
                        ni2 = ni1+1
            else :
                  #imf is active by default
                  if indx_mf == -1:
                        indep_var_name='f'
                        ni2=nfmean
                  else:
                        indep_var_name='f=const'      
                        ni1=max(1,min(nfmean,indx_mf))-1
                        ni2=ni1+1

                  if ienthalpy and indx_enthalpy == -1: 
                        indep_var_name += ', h'
                        nl2=ned
                  elif ienthalpy:
                        nl1=max(1,min(ned,indx_enthalpy))-1
                        nl2=nl1+1      

                  if imfvar and indx_mfvar == -1:
                        indep_var_name += ', fvar'
                        nj1=max(1,min(nfvar,indx_enthalpy))-1

                  if iprogvar and indx_progvar == -1:
                        indep_var_name += ', pv'
                        nk2=nprogvar1
                  elif iprogvar: 
                        nk1=max(1,min(nprogvar1,indx_progvar))-1
                        nk2=nk1+1

                  if istrain and indx_strain == -1:
                        indep_var_name += ', strain'
                        nk2=nsd
                  elif istrain: 
                        print indx_strain
                        nk1=max(1,min(nsd,indx_strain))-1
                        nk2=nk1+1






     
            # ... Read lines containing X,Y values to be plot
            self.XVector = []
            self.YVector = []
            YY = []
            PV = []
            YYY = []
            XXX = []

            if not iprogvarplot:
                  for l in range(ned):
                        FileLine = FileOpen.readline()
                        for k in range(max(nsd,nprogvar1)):
                              FileLine = FileOpen.readline()        
                              for j in range(nfvar):
                                    FileLine = FileOpen.readline()	 
                                    for i in range(nfmean):
                                          FileLine = FileOpen.readline()
                                          if (l >= nl1 and l < nl2 and k >= nk1 and k < nk2 and \
                                              j >= nj1 and j < nj2 and i >= ni1 and i < ni2):
                                                self.XVector.append(float(FileLine.split()[0]))
                                                self.YVector.append(float(FileLine.split()[iposition]))
            else:
                  #We are plotting using the progress variable as main indep. variable  
                  for l in range(ned):
                        FileLine = FileOpen.readline()
                        for k in range(max(nsd,nprogvar1)):
                              FileLine = FileOpen.readline()
                              #Read lines with 'PROGVAR1=value'. Convert = to blank, then split on blanks
                              a = FileLine.replace("="," ").split()
                              pvvalue = float(a[1])
                              for j in range(nfvar):
                                    FileLine = FileOpen.readline()
                                    for i in range(nfmean):
                                          FileLine = FileOpen.readline()
                                          YYY.append(float(FileLine.split()[iposition]))
                                          XXX.append(pvvalue)
                                          #Generate place for YY and PV
                                          YY.append(0.)
                                          PV.append(0.)
                  nx = nfmean
                  nxy = nfmean * nfvar
                  nxyz = nxy * max(nsd,nprogvar1)
                  # Copy field YYY and XXX into YY and PV switching from (i,j,k,l) to
                  # (k,j,i,l).  
                  for l in range(ned):
                        for k in range(max(nsd,nprogvar1)):
                              for j in range(nfvar):	
                                    for i in range(nfmean): 
                                          #Mind that the indices are shifted (starting from 0.)
                                          iiold = i+j*nx+k*nxy+l*nxyz
                                          #Change i and k index
                                          iinew = k+j*nx+i*nxy+l*nxyz
                                          #In the YY,PV fields the progress variable is the fastest variable
                                          YY[iinew] = YYY[iiold]
                                          PV[iinew] = XXX[iiold]
	            

                  #k is now the fastest running variable. This should be accounted for in 
                  #the index calcualtion
                  nx = max(nsd,nprogvar1)
                  nxy = max(nsd,nprogvar1) * nfvar
                  nxyz = nxy * nfmean
  
                  for l in range(nl1,nl2):
                        for i in range(ni1,ni2):
                              for j in range(nj1,nj2):	       
                                    for k in range(nk1,nk2):
                                          ii = k+j*nx+i*nxy+l*nxyz
                                          self.YVector.append(YY[ii])
                                          self.XVector.append(PV[ii])



            # ---
            # Close table filename
            # ---
            FileOpen.close()


      def getData(self):
            print 'TABGenPlot, getData() ... IN'
            print 'Number of X values: '+str(len(self.XVector))
            print 'Number of Y values: '+str(len(self.YVector))

            print 'X values: '+str(self.XVector)
            print 'Y values: '+str(self.YVector)

            print 'Get X,Y values:'
            nVal=len(self.XVector)
            for i in range(nVal):
                  print '   -> '+str(self.XVector[i])+'  ,  '+str(self.YVector[i])
                  eval_tcl_string( "global tabGen; lappend tabGen(XVector) \""+str(self.XVector[i])+"\"" )
                  eval_tcl_string( "global tabGen; lappend tabGen(YVector) \""+str(self.YVector[i])+"\"" )


      def preview(self):
            print 'TABGenPlot, preview() ... IN'

            if self.widget==None:
                  print 'No BLT graph defined.'
                  return
                  
            if self.XVector==[] or self.YVector==[]:
                  print 'No data to plot.'
                  return
            
            #==============================
            # TEST:
            #   . Transfer vectors to TCL
            #   . Plot data within BLT graph
            #==============================
            eval_tcl_string( "global tabGen; set tabGen(XVector) [list]" )
            eval_tcl_string( "global tabGen; set tabGen(YVector) [list]" )
            for i in range(len(self.XVector)):
                  eval_tcl_string( "global tabGen; lappend tabGen(XVector) \""+str(self.XVector[i])+"\"" )
                  eval_tcl_string( "global tabGen; lappend tabGen(YVector) \""+str(self.YVector[i])+"\"" )
            eval_tcl_string( "global tabGen; "+self.widget+" element configure graph1 -xdata $tabGen(XVector) -ydata $tabGen(YVector) -color blue" )

            # Set axis titles
            eval_tcl_string( self.widget + " xaxis configure -title " + "\"Mixture Fraction\"" )
            eval_tcl_string( self.widget + " yaxis configure -title " + "\""+ self.name_of_variable + str(" \[") + self.units + str("\]") +"\"")
            
            #Figaxis.set_ylabel(self.name_of_variable,  fontsize=Fontsize_label)
            #Figaxis.set_xlabel(u'Mixture Fraction',    fontsize=Fontsize_label)

            # Set axis ranges
            xmin = min(self.XVector)
            xmax = max(self.XVector)
            ymin = min(self.YVector)
            ymax = max(self.YVector)
            eval_tcl_string( self.widget + " xaxis configure -min "+str(xmin)+" -max "+str(xmax)+" -stepsize 0.2" )
            eval_tcl_string( self.widget + " yaxis configure -min "+str(ymin)+" -max "+str(ymax) )
            #==============================


      def plotData(self):
            print 'TABGenPlot, plotData() ... IN'

            width_inch  = 5.5
            height_inch = 5.5

            Fontsize_title = 12
            Fontsize_label = 10
            Fontsize_tick  = 8

            Figwindow = plt.figure(figsize=(width_inch, height_inch))

            subplots_adjust(bottom=0.1, right=0.95, left=0.1, top=0.95, hspace=0.25, wspace=0.2)

            Figaxis = Figwindow.add_subplot(111)

            Figaxis.plot(self.XVector, self.YVector, 'b-')

            Figaxis.set_ylabel(self.name_of_variable,  fontsize=Fontsize_label)
            Figaxis.set_xlabel(u'Mixture Fraction',    fontsize=Fontsize_label)

            xtext = Figaxis.get_xticklabels()
            ytext = Figaxis.get_yticklabels()
            setp(xtext, fontsize=Fontsize_tick)
            setp(ytext, fontsize=Fontsize_tick)

            #gca().yaxis.set_major_formatter(FormatStrFormatter('%2.1f'))

            xmin = min(self.XVector)
            xmax = max(self.XVector)
            ymin = min(self.YVector)
            ymax = max(self.YVector)
            AxisRange = [xmin, xmax, ymin, ymax]
            print AxisRange

            axis(AxisRange)

            grid(True)

            show()


      def showErrorMessage(self):
            print 'TABGenPlot, showErrorMessage() ... IN'

            if self.widget == None:
                  # Not Tk widget defined
                  return
            
            if self.errMessage != '':
                  # Refresh the GUI
                  eval_tcl_string( "update; after 100" )
                  # Show error message
                  cmd  = "ith_error "
                  cmd += "\""+self.errMessage+"\" "
                  cmd += "[winfo toplevel "+self.widget+"]"
                  ###eval_tcl_string( "ith_error \""+self.errMessage+"\" \""+self.widget+"\"" )
                  print 'executing: '+cmd
                  eval_tcl_string( cmd )


      # --------------------------------------------------------------------------------------
      #
      # Table read helpers
      #
      # --------------------------------------------------------------------------------------
      
      def read_dimensions(self,inputstring, outputlist):
            print 'TABGenPlot, read_dimensions() ... IN'

            a= inputstring.replace(","," ").replace("="," ").split()
            print a

            ilen=len(a)

            infmean=0
            infvar=0
            insd=0
            inprogvar1=0
            ined=0
            insl=0

            nfmean=0
            nfvar=0
            nsd=1
            nprogvar1=1
            ned=1
            nsl=1
            istop=0
            
            for i in range(ilen):
                  strtemp= a[i].lower()
                  if strtemp.find("nfmean") >= 0:
                        try: 
                              strtemp = a[i+1]
                              infmean =-1
                              nfmean  = int(strtemp)
                              infmean = 1
                        except:
                              break
                        
                  elif strtemp.find("nfvar") >= 0:
                        try:
                              strtemp = a[i+1]
                              infvar  =-1
                              nfvar   = int(strtemp)
                              infvar  = 1
                        except:
                              break

                  elif strtemp.find("nsd") >= 0:
                        try: 
                              strtemp = a[i+1]
                              insd    =-1
                              nsd     = int(strtemp)
                              insd    = 1
                        except: 
                              break
                        
                  elif (strtemp.find("nprogvar1") >= 0 or strtemp.find("n_progvar1") >= 0):
                        try:
                              strtemp    = a[i+1]
                              inprogvar1 =-1
                              nprogvar1  = int(strtemp)
                              inprogvar1 = 1
                        except:
                              break
                        
                  elif strtemp.find("ned") >= 0:
                        try:
                              strtemp = a[i+1]
                              ined    =-1
                              ned     = int(strtemp)          
                              ined    = 1
                        except:
                              break
                        
                  elif strtemp.find("nsl") >= 0:
                        try:
                              strtemp = a[i+1]
                              insl    =-1
                              nsl     = int(strtemp)
                              insl    = 1
                        except:
                              break
         
            # Checking identification of nfmean (points in mixture fraction)        
            if infmean == 0:
                  print 'Keyword nfmean is missing in header'
                  self.errMessage += 'ERROR: Keyword nfmean is missing in header.\n'
                  istop = 1
            elif infmean == -1:
                  print 'Keyword nfmean= should be followed by an integer number'
                  self.errMessage += 'ERROR: Keyword nfmean= should be followed by an integer number.\n'
                  istop = 1
            elif nfmean < 1: 
                  print 'nfmean must be equal or larger than unity'
                  self.errMessage += 'ERROR: nfmean must be >= 1\n'
                  istop = 1

            # Checking identification of nfvar (points in mixture fraction variance)        
            if infvar == 0 :
                  print 'Keyword nfvar is missing in header'
                  self.errMessage += 'ERROR: Keyword nfvar is missing in header.\n'
                  istop = 1
            elif infvar == -1:
                  print 'Keyword nfvar= should be followed by an integer number'
                  self.errMessage += 'ERROR: Keyword nfvar= should be followed by an integer number.\n'   
                  istop = 1
            elif nfvar < 1:
                  print 'nfvar must be equal or larger than unity'
                  self.errMessage += 'ERROR: nfvar must be >= 1\n'
                  istop = 1 

            # Checking nsd or nprogvar1 (points in strain rate / progress variable)        
            if insd == 0 and inprogvar1 == 0:
                  print 'Keyword nprogvar1 or nsd must be contained in the header'
                  self.errMessage += 'ERROR: Keyword nprogvar1 or nsd must be contained in the header.\n'
                  istop = 1
            elif insd == -1:
                  print 'Keyword nsd= should be followed by an integer number'
                  self.errMessage += 'ERROR: Keyword nsd= should be followed by an integer number.\n'
                  istop = 1
            elif inprogvar1 == -1:
                  print 'Keyword nprogvar1= should be followed by an integer number'
                  self.errMessage += 'ERROR: Keyword nprogvar1= should be followed by an integer number.\n'          
                  istop = 1
            elif inprogvar1 == 1 and nprogvar1 < 1: 
                  print 'nfprogvar1 must be equal or larger than unity'
                  self.errMessage += 'ERROR: nfprogvar1 must be >= 1\n'
                  istop = 1
            elif insd == 1 and nsd < 1: 
                  print 'nsd must be equal or larger than unity'
                  self.errMessage += 'ERROR: nsd must be >= 1\n'
                  istop = 1   

            # Checking identification of ned (points in the enthalpy defect)               
            if ined == 0 :
                  print 'Keyword ned is missing in header'
                  self.errMessage += 'ERROR: Keyword ned is missing in header.\n'
                  istop = 1 
            elif ined == -1:
                  print 'Keyword ned= should be followed by an integer number'
                  self.errMessage += 'ERROR: Keyword ned= should be followed by an integer number.\n'
                  istop = 1
            elif ned < 1: 
                  print 'ned must be equal or larger than unity'
                  self.errMessage += 'ERROR: ned must be equal or larger than unity.\n'
                  istop = 1

            # Checking identification of nsl (no. of scalars except the mixture fraction)               
            if insl == 0 :
                  print 'Keyword nsl is missing in header'
                  self.errMessage += 'ERROR: Keyword nsl is missing in header.\n'
                  istop = 1 
            elif ined == -1:
                  print 'Keyword nsl= should be followed by an integer number'
                  self.errMessage += 'ERROR: Keyword nsl= should be followed by an integer number.\n'
                  istop = 1
            elif nsl < 1: 
                  print 'nsl must be equal or larger than unity'
                  self.errMessage += 'ERROR: nsl must be equal or larger than unity.\n'
                  istop = 1
         
            # If the identification of the table dimensions failed, return error code
            if istop == 1:
                  print 'TABGenPlot.read_dimensions(): error detected due to wrong use and/or erroneous table.'
                  self.errMessage += 'Error detected due to wrong use and/or erroneous table.\n'
                  return -1
   
            outputlist.append(infmean)
            outputlist.append(infvar)
            outputlist.append(insd)
            outputlist.append(inprogvar1)
            outputlist.append(ined)
            outputlist.append(insl)
            outputlist.append(nfmean)
            outputlist.append(nfvar)
            outputlist.append(nsd)
            outputlist.append(nprogvar1)
            outputlist.append(ned)
            outputlist.append(nsl)
   
            return 1


      # ----------------------------------------------------------------------------------------------------------
      
      def read_position(self,inputstring, name_of_variable, outputlist):
            print 'TABGenPlot, read_position() ... IN'

            a= inputstring.lower().split()
            print a
            ilen = len(a)
   
            isearch=0
            # Trim off leading and trailing blanks. Convert to lower case letters.   
            name_lower = name_of_variable.lower().strip()
            if name_lower == 'temp'      or name_lower == 'temperature'                                 : isearch=1
            if name_lower == 'rho'       or name_lower == 'density'                                     : isearch=2
            if name_lower == 'visc'      or name_lower == 'viscosity' or name_lower =='dynamicviscosity': isearch=3 
            if name_lower == 'molarmass' or name_lower == 'mmw'                                         : isearch=4       
            if name_lower == 'cp'        or name_lower == 'heatcapacity'                                : isearch=5
   
            print 'isearch: '+str(isearch)

            iposition = -1
            if isearch == 0:   
                  for i in range(ilen):
                        strtmp = a[i]
                        if strtmp == 'Y_'+name_lower or strtmp == name_lower:
                              iposition = i-1
                              break
            elif isearch == 1:
                  for i in range(ilen):
                        strtmp = a[i]
                        if strtmp == 'temperature' or strtmp == 'temp':
                              iposition = i-1
                              break
            elif isearch == 2:
                  for i in range(ilen):
                        strtmp = a[i]
                        if strtmp == 'rho' or strtmp == 'density':
                              iposition = i-1
                              break
            elif isearch == 3:
                  for i in range(ilen):
                        strtmp = a[i]
                        if strtmp == 'visc' or strtmp == 'viscosity' or \
                               strtmp == 'dynamicviscosity' or strtmp == 'dynvisc':
                                          iposition = i-1
                                          print iposition
                                          break
            elif isearch == 4:
                  for i in range(ilen):
                        strtmp = a[i]
                        if strtmp == 'mmw' or strtmp == 'molarmass':
                              iposition = i-1
                              break 
            elif isearch == 5:
                  for i in range(ilen):
                        strtmp = a[i]
                        if strtmp == 'cp' or strtmp == 'heatcapacity':
                              iposition = i-1
                              break  	 
  
            if iposition == -1:
                  print "TABGenPlot.read_position(): ",name_of_variable," could nod be found in table."
      
            print 'Position:',iposition
            outputlist.append(iposition)
            return


      # ----------------------------------------------------------------------------------------------------------

      def read_calling_arguments(self,args,options):
            print 'TABGenPlot, read_calling_arguments() ... IN'

            ilen=len(args)
            for i in range(ilen):
                  print '   ',args[i]

            # Initialize local variables
            
            ipath         = False
            itable        = False
            ivariable     = False
            itemperature  = False
            idensity      = False
            iviscosity    = False
            ienthalpy     = False
            imfvar        = False
            iprogvar      = False
            ifull         = False
            istrain       = False
            ihelp         = False
            iprogvarplot  = False
            imf           = False
            ienthalpy     = False

            indx_mf       = -1
            indx_mfvar    = -1
            indx_strain   = -1
            indx_progvar  = -1
            indx_enthalpy = -1

            # Initialize strings
            pathstring = './'
            tablestring = ' '
            variablestring = ' '

            # Analyse all calling arguments
            ilen = len(args)
            for i in range(ilen):
                  string = args[i] 
                  # The first argument after the python script might be the filename      
                  if i == 1:
                        try:
                              if string.find("-") == -1:
                                    tablestring = string
                                    itable = True
                        except:
                              itable = False
                              
                  if(string.lower() == '-path'):
                        ipath = True
                        try:
                              strtmp = args[i+1]
                              if strtmp.find("-") >= 0   :
                                    print
                                    print "Valid argument missing after -path"
                                    print "Setting path to local directory './'"
                              else:
                                    pathstring = strtmp
                        except:
                              pathstring = './'
                              print
                              print "Valid argument missing after -path"
                              print "Setting path to local directory './'"

                  elif(string.lower() == '-table'):
                        itable = True
                        try:
                              strtmp = args[i+1]
                              print '----------------> '+strtmp[0]
                              if strtmp[0].find("-") >= 0:
                                    print
                                    print "Valid argument missing after -table"
                              else:
                                    tablestring = strtmp
                        except: 
                              print
                              print "Valid argument missing after -table"

                  elif(string.lower() == '-variable'):
                        ivariable = True
                        try:
                              strtmp = args[i+1]
                              if strtmp.find("-") >= 0:
                                    print
                                    print "Valid argument missing after -variable"
                                    print "Setting variable to 'Temperature'"
                                    itemperature = True
                                    ivariable = False
                              else:
                                    variablestring = strtmp             
                        except:
                              variablestring = 'temperature' 
                              ivariable = False         

                  elif(string.lower() == '-temperature'):
                        itemperature = True

                  elif(string.lower() == '-density'):
                        idensity = True

                  elif(string.lower() == '-viscosity'):
                        iviscosity = True

                  elif(string.lower() == '-enthalpy'):
                        ienthalpy = True
                        try:
                              strtmp = args[i+1]
                              if strtmp.find("-") == -1:
                                    indx_enthalpy = int(strtmp)
                        except:
                              indx_enthalpy = -1

                  elif(string.lower() == '-mfvar'):
                        imfvar = True          
                        try:
                              strtmp = args[i+1]
                              if strtmp.find("-") == -1:
                                    indx_mfvar = int(strtmp)
                        except:
                              indx_mfvar = -1

                  elif(string.lower() == '-progvar'):
                        iprogvar = True
                        try:
                              strtmp = args[i+1]
                              if strtmp.find("-") == -1:
                                    indx_progvar = int(strtmp)
                        except:
                              indx_progvar = -1

                  elif(string.lower() == '-full'):
                        ifull = True    

                  elif(string.lower() == '-strain'):
                        istrain = True
                        try:
                              strtmp = args[i+1]
                              if strtmp.find("-") == -1:
                                    indx_strain = int(strtmp)
                        except:
                              indx_strain = -1

                  elif(string.lower() == '-help'):
                        ihelp = True

                  elif(string.lower() == '-progvarplot'):
                        iprogvarplot = True

                  elif(string.lower() == '-mf'):
                        imf = True
                        try:
                              strtmp = args[i+1]
                              if strtmp.find("-") == -1:
                                    indx_mf = int(strtmp)
                        except:
                              indx_mf = -1
	     
	     


            # Exclude certain combinations
            if ivariable:
                  if itemperature or idensity or iviscosity:
                        print '-variable-option takes precedence'
                        itemperature = False
                        idensity     = False
                        iviscosity   = False
      
            if itemperature:
                  if idensity or iviscosity:
                        print '-temperature-option takes precedence'
                        idensity   = False
                        iviscosity = False
   
            if idensity:
                  if iviscosity:
                        print '-density-option takes precedence'
                        iviscosity = False
      
            if ifull:
                  ienthalpy = False
                  imfvar    = False
                  iprogvar  = False
                  istrain   = False
                  print '-full option detected'
   
            if not ivariable and not idensity and not iviscosity and not itemperature:
                  print 'NOTE: visualizing temperature by default.'
                  itemperature = True
   
            if not itable:
                  print 'Missing specification of table location.'
   
            options.append(pathstring)
            options.append(tablestring)
            options.append(variablestring)
            options.append(ivariable)
            options.append(itemperature)
            options.append(idensity)
            options.append(iviscosity)
            options.append(ienthalpy)
            options.append(imfvar)
            options.append(iprogvar)
            options.append(ifull)
            options.append(istrain)
            options.append(ihelp)
            options.append(iprogvarplot)
            options.append(imf)   
            options.append(indx_mf)
            options.append(indx_mfvar)
            options.append(indx_strain)
            options.append(indx_progvar)
            options.append(indx_enthalpy)
   
            return




# ----------------------------------------------------------------------------------------------------------
# End
# ----------------------------------------------------------------------------------------------------------
