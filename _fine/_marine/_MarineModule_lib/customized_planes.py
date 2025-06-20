#CFViewBackward(1210)
#_____________________________________________________________________________#
#                                                                             #
#                   Create user defined planes in CFView                      #
#_____________________________________________________________________________#
#
#	NUMECA International s.a
#
#	Implementator : Kevin VIDAL
#	Date: 2019
#______________________________________________________________________________
#
# Description: 	The script contains the GUI for launching the creation of the user defined plane
#              	User defined plane consists in shape defined plane in CFview
#		The plane can be propagated along an axis using an uniform distribution or a clustered one
#
# Changes:
#
# DATE			IMPLEMENTER			TYPE OF MODIFICATION
# 11-04-19		K vidal				Correction bugs 37236 & 37207
#
#______________________________________________________________________________

import os,sys,math,fileinput,string,time
from cfv import *
from Tk import *

def Customized_planes():
        pad = 1
        class CCPGui(DialogueBox):
            ### Begin GUI
            def __init__(self):
                DialogueBox.__init__(self, "Definition of the customized plane(s)")
                self.mainFrame = self.frame()
                self.mainFrame.pack(side="top",fill="both")
                ### Display general_page in main frame
                self.general_page(self.mainFrame)
                self.showCentered()

            def general_page(self,parentFrame):
                self.general_page_frame = parentFrame.frame()
                self.general_page_frame.pack(side="top",fill="both")

                #--------------------------------------------------
                # frame for center of coordinates
                centerPlane = self.general_page_frame.labelframe(label="Center")
                centerPlane.pack(side="top",fill="both")
                centerPlaneFrame = centerPlane.frame() 
                centerPlaneEntry = centerPlane.frame()
                centerPlaneFrame.pack(side="left",padx=pad,pady=pad)
                centerPlaneEntry.pack(side="left",padx=pad,pady=pad)
                #### X
                self.centerX = centerPlaneEntry.entry(label='  X ', width = 8, value = 0.0)\
                .pack(side = "left", anchor="w",padx=pad,pady=pad)
                #### Y
                self.centerY = centerPlaneEntry.entry(label='  Y ', width = 8, value = 0.0)\
                .pack(side = "left", anchor="w",padx=pad,pady=pad)
                #### Z
                self.centerZ = centerPlaneEntry.entry(label='  Z ', width = 8, value = 0.0)\
                .pack(side = "left", anchor="w",padx=pad,pady=pad)

                #--------------------------------------------------
                # frame for normals
                normalPlane = self.general_page_frame.labelframe(label="Normal")
                normalPlane.pack(side="top",fill="both")
                normalPlaneFrame = normalPlane.frame() 
                normalPlaneEntry = normalPlane.frame()
                normalPlaneFrame.pack(side="left",padx=pad,pady=pad)
                normalPlaneEntry.pack(side="left",padx=pad,pady=pad)
                #### X
                self.nx = normalPlaneEntry.entry(label='  X ', width = 8, value = 1.0)\
                .pack(side = "left", anchor="w",padx=pad,pady=pad)
                #### Y
                self.ny = normalPlaneEntry.entry(label='  Y ', width = 8, value = 0.0)\
                .pack(side = "left", anchor="w",padx=pad,pady=pad)
                #### Z
                self.nz = normalPlaneEntry.entry(label='  Z ', width = 8, value = 0.0)\
                .pack(side = "left", anchor="w",padx=pad,pady=pad)

                #--------------------------------------------------
                # Radius and discretization
                radiusPlane = self.general_page_frame.labelframe(label="Shape and size")
                radiusPlane.pack(side="top",fill="both")
                radiusPlaneFrame = radiusPlane.frame() 
                radiusPlaneEntry = radiusPlane.frame()
                radiusPlaneFrame.pack(side="left",padx=pad,pady=pad)
                radiusPlaneEntry.pack(side="left",padx=pad,pady=pad)
                #### R
                radiusPlaneFrame.label("Size").pack(side="top", fill = "x",padx=pad,pady=pad)
                self.R = radiusPlaneEntry.entry(width = 10, value = 0.0)
                self.R.pack( side = "top" , fill = "x" , expand = "yes", padx=pad,pady=pad)
                #### discretization
                # Show list of shape
                self.shapeFrame = radiusPlane.frame() 
                self.shapeFrame.pack(side="left",padx=pad)
                self.shapeFrame.label(text = ' Shape ').pack(side = "left", fill = "x", padx = pad)
                self.shape_model = [] ; self.shape_value = [] 
                self.shape_model.append("Square") ; self.shape_value.append(2)
                self.shape_model.append("Hexagon") ; self.shape_value.append(3)
                self.shape_model.append("Octagon") ; self.shape_value.append(4)
                self.shape_model.append("Decagon") ; self.shape_value.append(5)
                self.shape_model.append("Circle") ; self.shape_value.append(45)
                self.shape_model_index = self.shapeFrame.combobox(items=self.shape_model).pack(side = "left", fill = "x", expand="yes")

                #--------------------------------------------------
                # Distribution
                self.distribution = self.general_page_frame.labelframe(label="Distribution")
                self.distribution.pack(side="top",fill="both")
                # Activate button -> to activate distribution
                distributionActive = self.distribution.frame()
                distributionActive.pack(side="top", fill="both", padx = pad, pady = pad)
                self.activateDIST = distributionActive.checkbutton("Activate", 0, command = Command(self, CCPGui.distribution_mainFrame)).pack()
                # Show parameters settings 
                self.distribution_settings = self.distribution.frame()
                self.distribution_settings_1 = self.distribution_settings.frame().pack(side="top", fill="x", padx = pad, pady = pad)
                self.NBPlane = self.distribution_settings_1.entry(label = 'Total number of planes ', width = 8, value = 2)\
                .pack(side = "left", padx = pad)
                #### Distance of progression
                self.distance = self.distribution_settings_1.entry(label = 'Distance ', width = 8, value = 1)\
                .pack(side = "left", padx = pad+1)
                self.distribution_settings_2 = self.distribution_settings.frame().pack(side="top", fill="x", padx = pad, pady = pad)
                self.distribution_settings_2.label(text = 'Direction').pack(side = "left", anchor="w", padx = pad, pady = pad)
                #### Direction X
                self.dx = self.distribution_settings_2.entry(label=' X ', width = 8, value = 0.0)\
                .pack(side = "left", anchor="w",padx=pad,pady=pad)
                #### Direction Y
                self.dy = self.distribution_settings_2.entry(label=' Y ', width = 8, value = 0.0)\
                .pack(side = "left", anchor="w",padx=pad,pady=pad)
                #### Direction Z
                self.dz = self.distribution_settings_2.entry(label=' Z ', width = 8, value = 0.0)\
                .pack(side = "left", anchor = "se",padx=pad,pady=pad)
                # Activate button -> to select clustered distribution base on geometric progession
                DEFdistributionActive = self.distribution.frame()
                DEFdistributionActive.pack(side="top",fill="x", padx = pad, pady = pad)
                self.activateDEFDIST = DEFdistributionActive.checkbutton("Geometric distribution ", 0, command = Command(self, CCPGui.progression_mainFrame))
                # Show geometric progression settings
                self.progression_settings = self.distribution.frame()
                self.commonRatio = self.progression_settings.entry(label = 'Distribution ratio ', width = 8, value = 1)\
                .pack(side = "top", fill='x',padx = pad, pady = pad)

                #--------------------------------------------------
                # Main buttons of the GUI
                self.buttonsFrame = self.general_page_frame.frame()
                clean  = self.buttonsFrame.button(text="Remove all",command = Command(self,CCPGui.clean))
                undo  = self.buttonsFrame.button(text="Remove last",command = Command(self,CCPGui.undo))
                apply  = self.buttonsFrame.button(text="Apply",command = Command(self,CCPGui.apply))
                cancel  = self.buttonsFrame.button(text="Cancel",command = Command(self,DialogueBox.close))
                self.buttonsFrame.pack(side="top",anchor = "se" , expand = "yes" )
                cancel.pack(side="right")
                apply.pack(side="right")
                undo.pack(side="right")
                clean.pack(side="right")
                # pack for ,displaying error message in the GUI, not in a popup
                self.warning1 = self.general_page_frame.frame()
                self.warning1.label(text ='Non-real value entered,\nplease modify the settings').pack(side = "top", padx = pad+1)
                self.warning2 = self.general_page_frame.frame()
                self.warning2.label(text ='Normal not defined,\nplease modify the settings').pack(side = "top", padx = pad+1)
                self.warning3 = self.general_page_frame.frame()
                self.warning3.label(text ='Size must be higher than 0,\nplease modify the settings').pack(side = "top", padx = pad+1)
                self.warning4 = self.general_page_frame.frame()
                self.warning4.label(text ='Distance of distribution must be higher than 0,\nplease modify the settings').pack(side = "top", padx = pad+1)
                self.warning5 = self.general_page_frame.frame()
                self.warning5.label(text ='Distribution ratio must be higher than 0,\nplease modify the settings').pack(side = "top", padx = pad+1)
                self.warning6 = self.general_page_frame.frame() #BUG correction bug 37236 as it is now total number of planes (before additional planes)
                self.warning6.label(text ='Total number of planes must be equal or higher than 2,\nplease modify the settings').pack(side = "top", padx = pad+1)

            def distribution_mainFrame(self):
                if float(self.activateDIST.getState()) == 0.0:
                    self.distribution_settings.unpack()
                    self.activateDEFDIST.unpack()
                    self.progression_settings.unpack()
                elif float(self.activateDIST.getState()) == 1.0:
                    self.distribution_settings.pack(side = 'top', fill = "x", padx = pad, pady = pad)
                    self.activateDEFDIST.pack()
                    if float(self.activateDEFDIST.getState()) == 1.0:
                        CCPGui.progression_mainFrame(self)
                
            def progression_mainFrame(self):
                if float(self.activateDEFDIST.getState()) == 0.0: 
                    self.progression_settings.unpack()
                elif float(self.activateDEFDIST.getState()) == 1.0:
                    self.progression_settings.pack(side = "top", anchor = "w",  expand = "yes")
            ### End GUI

            ### Begin internal functions
            def check_values(self):
                '''function that check if all values are of real type and a type input output error
                return 0 if all tests are ok
                return 1 if non real value detected
                return 2 if normal not defined
                return 3 if radius <= 0
                return 4 if distribution settings not ok for total number of planes and distance
                return 5 if common ratio = 0
                return 6 if total number of plane is equal or below 1'''
                try:
                    #test all variables if one incorrect IOerror = 1 -> Non real value entered in the GUI
                    str(self.centerX.getFloatValue())
                    str(self.centerY.getFloatValue()) 
                    str(self.centerZ.getFloatValue())
                    str(self.nx.getFloatValue())
                    str(self.nz.getFloatValue())
                    str(self.R.getFloatValue())
                    str(self.shape_model_index.getValue())
                    float(self.activateDIST.getState())
                    float(self.activateDEFDIST.getState()) 
                    str(self.commonRatio.getFloatValue())
                    str(self.distance.getFloatValue())
                    str(self.distance.getFloatValue())
                    str(self.dx.getFloatValue())
                    str(self.dy.getFloatValue())
                    str(self.dz.getFloatValue())
                    str(self.nx.getFloatValue())
                    str(self.ny.getFloatValue())
                    str(self.nz.getFloatValue())
                    str(self.dx.getFloatValue())
                    str(self.dy.getFloatValue())
                    str(self.dz.getFloatValue())
                    str(int(self.NBPlane.getFloatValue()))
                    index_mode = self.shape_model.index(self.shape_model_index.getValue())
                    float(self.shape_value[index_mode])
                    if self.debug == True:
                        print ('-------------------------------------------------')
                        print ('>> center of the customized cut plane (CCP) is: ' + str(self.centerX.getFloatValue()) + ',' + \
                        str(self.centerY.getFloatValue()) + ',' + str(self.centerZ.getFloatValue()))
                        print ('>> normal of the customized cut plane (CCP) is: '+ str(self.nx.getFloatValue()) + ',' + \
                        str(self.ny.getFloatValue()) + ',' + str(self.nz.getFloatValue()))
                        print ('>> Size is %1.3f and shape is a %s '\
                        %((self.R.getFloatValue()),(self.shape_model_index.getValue())))
                        if float(self.activateDIST.getState()) == 1.0 :
                            if float(self.activateDEFDIST.getState()) == 1.0: 
                                print ('>> Geometric distribution of common ratio %1.3f and distance %1.3f'\
                                %(self.commonRatio.getFloatValue(),self.distance.getFloatValue()))
                            else:
                                print ('>> Uniform distribution with distance %1.3f'%(self.distance.getFloatValue()))
                            if self.dx.getFloatValue() == 0 and self.dy.getFloatValue()==0 and self.dz.getFloatValue() == 0:
                                print ('>> direction based on the normal of the main CCP')
                                print ('>> direction of the distribution is: ' +str(self.nx.getFloatValue()) + ',' + \
                                str(self.ny.getFloatValue()) + ',' + str(self.nz.getFloatValue()))
                            else:
                                print ('>> direction of the distribution is: '+ str(self.dx.getFloatValue()) + ',' + \
                                str(self.dy.getFloatValue()) + ',' + str(self.dz.getFloatValue()))
                            print ('>> Number of total planes %d'%(int(self.NBPlane.getFloatValue())))
                        index_mode = self.shape_model.index(self.shape_model_index.getValue())
                        self.nb_angles = float(self.shape_value[index_mode])
                        print ('-------------------------------------------------')
                    IOerror = 0
                except:
                    IOerror = 1
                if IOerror == 0:
                    if (self.nx.getFloatValue() == 0  and self.ny.getFloatValue() == 0 and self.nz.getFloatValue() == 0):
                        IOerror = 2
                    elif (self.R.getFloatValue()<=0):
                        IOerror = 3
                    elif float(self.activateDIST.getState()) == 1.0 :
                        if (int(self.NBPlane.getFloatValue()) > 1 and self.distance.getFloatValue()<=0):
                            IOerror = 4
                        elif float(self.activateDEFDIST.getState()) == 1.0: 
                            if (self.commonRatio.getFloatValue()<=0):
                                IOerror = 5
                        elif int(self.NBPlane.getFloatValue()) <= 1: #BUG correction bug 37236 as it is now total number of planes (before additional planes)
                            IOerror = 6
                return IOerror
            
            #### BUG correction bug 37207 get size and avoid creation of plane in case out of domain ###
            def GetDomaineSize(self):
                '''create x, y and z quantities to retrieve size of the domain
                first select all surfaces in CFV tree
                create quantities, then store the results in array 0=X, Y=1, Z=2'''
                DomainRange = [0,0,0]
                SelectTypeFromProject('')
                QntFieldDerived(0 ,'z length' ,'z' ,'' ,'0')
                QntFieldDerived(0 ,'x length' ,'x' ,'' ,'0')
                QntFieldDerived(0 ,'y length' ,'y' ,'' ,'0')
                QntFieldScalar('x length')
                rgx = QuantityRangeActiveSurfaces()
                QntFieldScalar('y length')
                rgy = QuantityRangeActiveSurfaces()
                QntFieldScalar('z length')
                rgz = QuantityRangeActiveSurfaces()
                QntFieldRemove('x length')
                QntFieldRemove('y length')
                QntFieldRemove('z length')
                DeleteAll()
                UnselectTypeFromView('')
                DomainRange[0] = rgx
                DomainRange[1] = rgy
                DomainRange[2] = rgz
                # BUG correction bug 37426  store size domain in variables
                self.X_min = DomainRange[0][0] 
                self.X_max = DomainRange[0][1]
                self.Y_min = DomainRange[1][0]
                self.Y_max = DomainRange[1][1]
                self.Z_min = DomainRange[2][0]
                self.Z_max = DomainRange[2][1]
                return DomainRange

            def apply(self):
                '''read the settings and create the plane or the planeS'''
                self.warning1.unpack()
                self.warning2.unpack()
                self.warning3.unpack()
                self.warning4.unpack()
                self.warning5.unpack()
                self.warning6.unpack()
                self.debug = True # activate debug
                CCPGui.check_values(self) # print debug in the console
                self.debug = False # deactivate debug no more debug -> hence only one debug in the console per apply 
                if (CCPGui.check_values(self)==1): #non real value detected
                    self.warning1.pack(side = "top", anchor = "se", padx = pad)
                    CFViewWarning('Non-real value entered,\nplease modify the settings')
                    return
                elif (CCPGui.check_values(self)==2): #normal not defined
                    self.warning2.pack(side = "top", anchor = "se", padx = pad)
                    CFViewWarning('Normal not defined,\nplease modify the settings')
                    return
                elif (CCPGui.check_values(self)==3): #radius <= 0
                    self.warning3.pack(side = "top", anchor = "se", padx = pad)
                    CFViewWarning('Size must be higher than 0,\nplease modify the settings')
                    return
                elif (CCPGui.check_values(self)==4): #distance not ok in case additional planes > 0
                    self.warning4.pack(side = "top", anchor = "se", padx = pad)
                    CFViewWarning('Distance of distribution must be higher than 0,\nplease modify the settings')
                    return
                elif (CCPGui.check_values(self)==5): #common ratio == 0
                    self.warning5.pack(side = "top", anchor = "se", padx = pad)
                    CFViewWarning('Distribution ratio must be higher than 0,\nplease modify the settings')
                    return
                elif (CCPGui.check_values(self)==6): #total number of planes =< 1 #BUG correction bug 37236 as it is now total number of planes (before additional planes)
                    self.warning6.pack(side = "top", anchor = "se", padx = pad)
                    CFViewWarning('Total number of planes must be equal or higher than 2,\nplease modify the settings')
                    return
                elif (CCPGui.check_values(self)==0): #tutto sotto controlo (IT) tudo bem (PT) todo bien (ESP) fieu ca marche (BEL) ce programe fonctionne divinement (FR) Fuck yeah (ENG)
                    # BUG correction bug 37426 domain size is computed only once 
                    try :
                        str(self.X_min)
                        print ('>> Domain size already computed')
                        print ('>> Size of the domain')
                        print ('>> Xrange: [' + str(self.X_min) +', ' + str(self.X_max) + ']')
                        print ('>> Yrange: [' + str(self.Y_min) +', ' + str(self.Y_max) + ']')
                        print ('>> Zrange: [' + str(self.Z_min) +', ' + str(self.Z_max) + ']')
                    except:
                        print ('>> Computting Domain size')
                        DomainSize = CCPGui.GetDomaineSize(self)
                        print ('>> Size of the domain [(Xmin,Xmax),(Ymin,Ymax),(Zmin,Zmax)]')
                        print DomainSize
                    #print self.X_max,self.X_min,self.Y_max,self.Y_min,self.Z_max,self.Z_min
                    cx = self.centerX.getFloatValue()
                    cy = self.centerY.getFloatValue()
                    cz = self.centerZ.getFloatValue()
                    R = self.R.getFloatValue()
                    Nx = self.nx.getFloatValue()
                    Ny = self.ny.getFloatValue()
                    Nz = self.nz.getFloatValue()
                    discretization = self.nb_angles
                    GroupCP = []
                    self.cleaning = False
                    indexG = CCPGui.cleanCCPs(self)[1]
                    indexP = CCPGui.cleanCCPs(self)[0]
                    if float(self.activateDIST.getState()) == 0.0: # single CCplane
                        CCP = CCPGui.CCP(self,cx,cy,cz,R,Nx,Ny,Nz,discretization,indexP)
                        GroupCP.append(CCP)
                    elif float(self.activateDIST.getState()) == 1.0: # several CCplanes
                        n = int(self.NBPlane.getFloatValue()) - 1 #BUG correction bug 37236 as it is now total number of planes (before additional planes)
                        if float(self.activateDEFDIST.getState()) == 1.0: # if geometric is active
                            ratio = self.commonRatio.getFloatValue()
                        else: # geometric not active, uniform
                            ratio = 1
                        CCPGui.Progression(self, n, ratio)
                        self.Distr =  [x * self.distance.getFloatValue() for x in self.Progress]
                        #print 'Distribution values'
                        #print self.Distr
                        if (self.dx.getFloatValue()==0 and self.dy.getFloatValue() == 0 and self.dz.getFloatValue()==0): # set direction of the distribution equal to normal of the plane
                            CCPGui.changeRefFrame(self,Nx,Ny,Nz,cx,cy,cz)
                            for i in range(len(self.Distr)):
                                CCP = CCPGui.CCP(self,self.refX[i],self.refY[i],self.refZ[i],R,Nx,Ny,Nz,discretization,indexP)
                                GroupCP.append(CCP)
                                indexP += 1
                        else: # direction are user defined in the GUI
                            CCPGui.changeRefFrame(self,self.dx.getFloatValue(),self.dy.getFloatValue(),self.dz.getFloatValue(),cx,cy,cz)
                            for i in range(len(self.Distr)):
                                CCP = CCPGui.CCP(self,self.refX[i],self.refY[i],self.refZ[i],R,Nx,Ny,Nz,discretization,indexP)
                                GroupCP.append(CCP)
                                indexP += 1 
                    if GroupCP[0]: # if first element is none, do not make any group
                        OK_GroupCP = [] # list for cleaning off 'none' in list
                        surfaces2removed = []  # list for cleaning off initial ccp in case of multi domains only keep CCP_*.D* and remove CCP*
                        for cp in GroupCP: 
                            if cp != None:
                                OK_GroupCP.append(cp) # when performing a propagation some plan can be created outside the domain and make CreateSurfaceGroup comand to fail -> remove the empty part of the list
                        for ccp in OK_GroupCP: # BUG correction bug 37210
                            for surface in GetProjectSurfaceList():
                                if surface.startswith(ccp) and surface != ccp : # store only CCP_*.D* this helps to identify multi domains config
                                    OK_GroupCP.append(surface)
                                    surfaces2removed.append(ccp) # store initial CCP_* surface
                        CreateSurfaceGroup('G' +str(indexG) + '_CCP' ,*OK_GroupCP)   
                        UnselectTypeFromView('')  # Unselect all
                        if surfaces2removed != []:
                            DeleteFromProject(*surfaces2removed) #remove CCP_* surface
                        SelectFromProject('G' +str(indexG) + '_CCP')
                        GmtToggleBoundary()  # select group and display in CFView
                        UnselectTypeFromView('') # Unselect all
                return

            def UpdateCFVGUI(self): #not working must check wiht CFV developper in order to make an update after CCP creation
                '''get current camera view and set the same in order to update it'''
                view = GetCamera()
                print view
                p1 = view[0][0] 
                p2 = view[0][1]  
                p3 = view[0][1]
                t1 = view[1][0] 
                t2 = view[1][1]  
                t3 = view[1][1] 
                v1 = view[2][0] 
                v2 = view[2][1]  
                v3 = view[2][1]
                w = view[3]
                h = view[4]
                print p1,p2,p3,t1,t2,t3,v1,v2,v3,w,h
                SetCamera(p1,p2,p3,t1,t2,t3,v1,v2,v3,w,h)
                return

            def changeRefFrame(self,dirX,dirY,dirZ,cX,cY,cZ):
                '''changeRefFrame to project the progression into cartesian axis
                arg dirX, dirY, dirZ     define the direction of the progression
                arg cX, cY, cZ           define the center of the inital CCplane
                return                   lists of cartesian coordinates'''
                #print self.Progress, self.Distr
                self.refX = [0 for x in range(len(self.Distr))]
                self.refY = [0 for x in range(len(self.Distr))]
                self.refZ = [0 for x in range(len(self.Distr))]
                angleTheta = CCPGui.angleXZ(self,abs(dirX),dirZ)
                anglePhi = CCPGui.angleXY(self,dirX,dirY)
                for i in range(len(self.Distr)):
                    self.refX[i] = self.Distr[i]*math.cos(angleTheta)*math.cos(anglePhi)+cX
                    self.refY[i] = self.Distr[i]*math.cos(angleTheta)*math.sin(anglePhi)+cY
                    self.refZ[i] = self.Distr[i]*math.sin(angleTheta)+cZ
                #print self.refX,self.refY,self.refZ
                return self.refX,self.refY,self.refZ

            def isInteger(self,value):
                # BUG correction bug 37210 function to check if an index of a surface is an integer, used in function cleanCCPs
                try:
                    int(value)
                    return True
                except:
                    return False

            def undo(self):
                '''get the index of the lastly created group and remove it'''
                self.cleaning = False
                indexG = CCPGui.cleanCCPs(self)[1] - 1 # cleanCCPs returns index of the plane + 1 (the increment)
                #print indexG
                if indexG>0:
                    DeleteSurface('G' +str(indexG) + '_CCP')
                else:
                    print('>> All customized planes are deleted')
                    CFViewWarning('All customized planes are deleted')
                return

            def clean(self):
                '''activate the function cleanCCPs() '''
                self.cleaning = True
                CCPGui.cleanCCPs(self)
                return

            def cleanCCPs(self):
                '''if self.cleaning = True ,    functon removes planes with name UDplane
                if self.cleaning = False,    return the index of the last plane created
                if the project is not open,  return none'''
                try:
                    indexSurface = 1
                    indexGroup = 1
                    for surface in GetProjectSurfaceList():
                        if surface.startswith('CCP'): # when multidomains CFV adds .D* hence the extracted index cannot be converted into integer -> Bug 37210
                            if CCPGui.isInteger(self,surface.split('_')[1]): # BUG correction bug 37210 a double check if performed to ensure the integer conversion is performed
                                indexSurface = int(surface.split('_')[1]) + 1
                        if surface.startswith('G') and surface.endswith('CCP') :
                            if self.cleaning:
                                DeleteSurface(surface)
                            else: 
                                if int(surface.split('_')[0][-1:]) > indexGroup:
                                    indexGroup = int(surface.split('_')[0][-1:])
                                indexGroup += 1
                    for surface in GetProjectSurfaceList(): #second deletion, look for only CCP plane after all Group CCP are removed
                        if surface.startswith('CCP'):
                            if self.cleaning:
                                DeleteSurface(surface)
                    return indexSurface,indexGroup
                except:
                    print("Warning no project is currently opened. Please open results in CFView and launch this plugin again!")
                    CFViewWarning("Warning no project is currently opened. Please open results in CFView and launch this plugin again!")
                    return None

            def angleXZ(self,nx,nz):
                '''artan(nz/nx) -> return angle in radian'''
                angle = math.atan2(nz,nx)
                return angle

            def angleXY(self,nx,ny):
                '''artan(ny/nx) -> return angle in radian'''
                angle = math.atan2(ny,nx)
                return angle  

            def Rad2Deg(self,angleRad): #not used, but useful for debug
                '''0.01745rad / pi/180 = 1deg'''
                angleDeg = angleRad / (math.pi/180.)
                return angleDeg

            def CCP(self,centerX,centerY,centerZ,R,nx,ny,nz,discretization,indexP):
                '''CCP for user defined function creates a shape defined plane
                arg centerX, centerY, centerZ     are the center of the plane
                arg R                             defines the size of the plane
                arg nx, ny, nz                    define the normal orientation
                arg discretization                defines the shape (2=square,3=hexagon,4=octagon,5=decagon,>5 tends to be a circle)
                arg indexP                        defines the index of the plane by default (ie CCP_1 when indexP=1)'''
                if (indexP==None): #None when there is not project open in CFV
                    return
                #### BUG correction bug 37207 get size and avoid creation of plane in case out of domain ###
                # BUG correction bug 37426 no more computation of the domain size inside CCP function it was problematic when having a distributon
                # DomainSize = CCPGui.GetDomaineSize(self)
                epsilon = 1e-04
                if self.X_min<centerX<self.X_max:
                    if self.Y_min<centerY<self.Y_max:
                        if self.Z_min<centerZ<self.Z_max:
                            # all components are inside the domain
                            pass
                        elif abs(self.Z_min-centerZ)<epsilon:
                            centerZ = centerZ+1e-06 # shift the coordinates in order to make sure the center is still located inside the domain
                        elif abs(self.Z_max-centerZ)<epsilon:
                            centerZ = centerZ-1e-06 # shift the coordinates in order to make sure the center is still located inside the domain
                        else:
                            print(">> Customized plane is not created because out of the domain")
                            CFViewWarning("Customized plane is not created because out of the domain")
                            return
                    elif abs(self.Y_min-centerY)<epsilon:
                        centerY = centerY+1e-06 # shift the coordinates in order to make sure the center is still located inside the domain
                    elif abs(self.Y_max-centerY)<epsilon:
                        centerY = centerY-1e-06 # shift the coordinates in order to make sure the center is still located inside the domain
                    else:
                        print(">> Customized plane is not created because out of the domain")
                        CFViewWarning("Customized plane is not created because out of the domain")
                        return
                elif abs(self.X_min-centerX)<epsilon:
                    centerX = centerX+1e-06 # shift the coordinates in order to make sure the center is still located inside the domain
                elif abs(self.X_max-centerX)<epsilon:
                    centerX = centerX-1e-06 # shift the coordinates in order to make sure the center is still located inside the domain
                else:
                    print(">> Customized plane is not created because out of the domain")
                    CFViewWarning("Customized plane is not created because out of the domain")
                    return

                # compute angle thanks to normal coordinates
                angleTheta = CCPGui.angleXZ(self,abs(nx),nz)
                anglePhi = CCPGui.angleXY(self,nx,ny)
                cutName =CutPlaneSave(centerX,centerY,centerZ,nx,ny,nz,0,"user_cut")
                SelectFromView(cutName)
                GmtToggleBoundary()
                names =[]
                DeltaAngle = math.pi/discretization
                for i in range(int(discretization)):
                    angle = i*DeltaAngle
                    # cutting plane 1 ----------------
                    y1 = -R*math.sin(angle)
                    z1 = R*math.cos(angle)
                    nx1 = z1*math.sin(angleTheta)*math.cos(anglePhi)-y1*math.sin(anglePhi)
                    ny1 = z1*math.sin(angleTheta)*math.sin(anglePhi)+y1*math.cos(anglePhi)
                    nz1 = -z1*math.cos(angleTheta)	
                    px1 = centerX + nx1
                    py1 = centerY + ny1
                    pz1 = centerZ + nz1	
                    # cutting plane 2 ---------------
                    y2 = R*math.sin(angle)
                    z2 = -R*math.cos(angle)	
                    nx2 = z2*math.sin(angleTheta)*math.cos(anglePhi)-y2*math.sin(anglePhi)
                    ny2 = z2*math.sin(angleTheta)*math.sin(anglePhi)+y2*math.cos(anglePhi)
                    nz2 = -z2*math.cos(angleTheta)		
                    px2 = centerX + nx2
                    py2 = centerY + ny2
                    pz2 = centerZ + nz2		
                    # create and get the name of the newly intermediate plane -------------
                    cutName_tmp =  CutSurfaceSave(px1,py1,pz1,nx1,ny1,nz1,0,px2,py2,pz2,nx2,ny2,nz2,0)
                    SelectFromProject(cutName_tmp)
                    names.append(cutName_tmp)
                    GmtToggleBoundary()
                    # delete intermediate plane to only keep final user defined plane -------------
                    if i == 0:
                        DeleteSurface(cutName)
                    else:
                        DeleteSurface(names[i-1])
                # create final user defined plane ------------------
                try:
                    SurfaceRename(names[i] ,'CCP_'+ str(indexP))
                    return 'CCP_'+ str(indexP)
                except:
                    print(">> Customized plane is not created")
                    CFViewWarning("Customized plane is not created")
                    return None

            def Progression(self, n, ratio):
                '''main function for defining geometric distribution list on [0,1] defined by n intervals
                arg n           defines the prescribed amount of intervals
                arg ratio       defines the ratio of the progression (between two successive intervals) when ratio=1, uniform distribution, the ratio !=0
                return Progress   defines the normalized size of the distribution vector as a list'''
                n = int(n)
                self.Progress = [0 for x in range(n+1)]
                if (abs(ratio-1.0) < 0.001): # uniform progession
                    for i in range(0,n+1):
                        self.Progress[i] = float(i)/float(n)
                else: # geometric progression
                    CR = 1.0 / (pow(ratio, n) - 1.0)
                    for i in range(0,n+1):
                        self.Progress[i] = (pow(ratio,i) - 1.0) * CR
                return self.Progress # return a list of normalized position of the different plane
            ### End internal functions

        #------------------------------------------------------------------
        z = CCPGui()
        #------------------------------------------------------------------