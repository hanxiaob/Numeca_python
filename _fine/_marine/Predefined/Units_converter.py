#                                                                             #
#                          	 Converter                                    #
#_____________________________________________________________________________#
#
#	NUMECA International s.a
#
#	Implementator : B. Mallol
#       Creation Date : 29/03/2012
#______________________________________________________________________________
#
# Description: Converter for Marine module for FM GUI
# 
# Changes:
# 29/5/2012 - convertion accuracy for speeds increased to 8 digits
#______________________________________________________________________________

#!/bin/python

# for TCL windows
from Tk import *
import string

# for classic commands
import os,sys,math,fileinput,string,time

pad = 2

class MyDialogue(DialogueBox):
	def __init__(self):
		DialogueBox.__init__(self, "Converter")
		self.show()
		
		self.mainFrame = self.frame()
		self.mainFrame.pack(side="top",fill="both")
		
		### Display general_page in main frame
		self.general_page(self.mainFrame)
		
		self.showUnderMouse()

	def general_page(self,parentFrame):
		
		# select speed conversion
		
		convertFrame = self.labelframe(label="Speed").pack(side="top",fill="x",padx=pad,pady=pad)
		self.selecConvert_speed = Variable(0)
		convertFrame.radiobutton("Kt >> m/s",self.selecConvert_speed, value=0, command=Command(self,MyDialogue.convertionInput)).pack(side="left",fill="x",padx=pad,pady=pad)
		convertFrame.radiobutton("m/s >> Kt",self.selecConvert_speed, value=1, command=Command(self,MyDialogue.convertionInput)).pack(side="left",fill="x",padx=pad,pady=pad)
		
		### user data
		
		speed_frame = self.frame()
		speed_frame.pack(side="top",fill="x",padx = pad,pady = pad)

		self.speed_kt = speed_frame.entry(label=" " , value = 0.0 , width = 10, unit = '\[Kt\]')
		self.speed_kt.pack( side = "top" , fill = "y" , padx = pad)
		self.speed_ms = speed_frame.entry(label=" " , value = 0.0 , width = 10, unit = '\[m/s\]')
		apply1 = speed_frame.button(text="Compute",command = Command(self,MyDialogue.apply1)).pack(side="bottom",padx=5,pady=5)
		
		# select angle conversion
		
		convertFrame2 = self.labelframe(label="Angle").pack(side="top",fill="x",padx=pad,pady=pad)
		self.selecConvert_angle = Variable(0)
		convertFrame2.radiobutton("deg >> rad",self.selecConvert_angle, value=0, command=Command(self,MyDialogue.convertionInput2)).pack(side="left",fill="x",padx=pad,pady=pad)
		convertFrame2.radiobutton("rad >> deg",self.selecConvert_angle, value=1, command=Command(self,MyDialogue.convertionInput2)).pack(side="left",fill="x",padx=pad,pady=pad)
		
		### user data
		
		angle_frame = self.frame()
		angle_frame.pack(side="top",fill="x",padx = pad,pady = pad)

		self.angle_deg = angle_frame.entry(label=" " , value = 0.0 , width = 10, unit = '\[deg\]')
		self.angle_deg.pack( side = "top" , fill = "y" , padx = pad)
		self.angle_rad = angle_frame.entry(label=" " , value = 0.0 , width = 10, unit = '\[rad\]')
		apply2 = angle_frame.button(text="Compute",command = Command(self,MyDialogue.apply2)).pack(side="bottom",padx=5,pady=5)
		
		# select fluid conversion
		
		convertFrame3 = self.labelframe(label="Fluid Properties").pack(side="top",fill="x",padx=pad,pady=pad)
		self.selecConvert_fluid = Variable(0)
		convertFrame3.radiobutton(">> Kinematic Viscosity",self.selecConvert_fluid, value=0, command=Command(self,MyDialogue.convertionInput3)).pack(side="left",fill="x",padx=pad,pady=pad)
		convertFrame3.radiobutton(">> Dynamic Viscosity",self.selecConvert_fluid, value=1, command=Command(self,MyDialogue.convertionInput3)).pack(side="left",fill="x",padx=pad,pady=pad)
		
		### user data
		
		fluid_frame = self.frame()
		fluid_frame.pack(side="top",fill="x",padx = pad,pady = pad)

		self.fluid_density = fluid_frame.entry(label=" Density" , value = 0.0 , width = 10, unit = '\[kg/m3\]')
		self.fluid_density.pack( side = "top" , fill = "y" , padx = pad)
		self.fluid_dyn = fluid_frame.entry(label=" Dynamic Viscosity" , value = 0.0 , width = 10, unit = '\[kg/(m.s)\]')
		self.fluid_dyn.pack( side = "top" , fill = "y" , padx = pad)
		self.fluid_kin = fluid_frame.entry(label=" Kinematic Viscosity" , value = 0.0 , width = 10, unit = '\[m2/s\]')
		apply3 = fluid_frame.button(text="Compute",command = Command(self,MyDialogue.apply3)).pack(side="bottom",padx=5,pady=5)
	
	def convertionInput(self):
		if self.selecConvert_speed.getValue() == "0":
			self.speed_kt.pack( side = "top" , fill = "y" , padx = pad)
			self.speed_ms.unpack()
		else:
			self.speed_kt.unpack()
			self.speed_ms.pack( side = "top" , fill = "y" , padx = pad)
			
	def convertionInput2(self):
		if self.selecConvert_angle.getValue() == "0":
			self.angle_deg.pack( side = "top" , fill = "y" , padx = pad)
			self.angle_rad.unpack()
		else:
			self.angle_deg.unpack()
			self.angle_rad.pack( side = "top" , fill = "y" , padx = pad)

	def convertionInput3(self):
		if self.selecConvert_fluid.getValue() == "0":
			self.fluid_dyn.pack( side = "top" , fill = "y" , padx = pad)
			self.fluid_density.pack( side = "top" , fill = "y" , padx = pad)
			self.fluid_kin.unpack()
		else:
			self.fluid_dyn.unpack()
			self.fluid_kin.pack( side = "top" , fill = "y" , padx = pad)
			
	def apply1(self):
		try:
			speed_kt_val = self.speed_kt.getFloatValue()
			speed_ms_val = self.speed_ms.getFloatValue()
		
		except ValueError:
			Warning("Wrong input value in at least one of the entries. Must be a float or an integer value")
			return
		
		speed_kt_val_ms = speed_kt_val*0.514444
		speed_ms_val_kt = speed_ms_val*1.943846
		
		dialogue = DialogueBox("Conversion Result")
		
		if self.selecConvert_speed.getValue() == "0":
			dialogue.label(str(speed_kt_val)+ "kt gives " + str('%4.4f'%(speed_kt_val_ms)) + "m/s").pack()
		else:
			dialogue.label(str(speed_ms_val)+ "m/s gives " + str('%4.4f'%(speed_ms_val_kt)) + " kt").pack()
		
		dialogue.button("Close", Command(dialogue,DialogueBox.close) ).pack()

	def apply2(self):
		try:
			angle_deg_val = self.angle_deg.getFloatValue()
			angle_rad_val = self.angle_rad.getFloatValue()
		
		except ValueError:
			Warning("Wrong input value in at least one of the entries. Must be a float or an integer value.")
			return
		
		angle_deg_val_rad = angle_deg_val*0.017453292519943
		angle_rad_val_rad = angle_rad_val*57.295779513082
		
		dialogue = DialogueBox("Conversion Result")
		
		if self.selecConvert_angle.getValue() == "0":
			dialogue.label(str(angle_deg_val)+ "deg gives " + str('%4.6f'%(angle_deg_val_rad)) + "rad").pack()
		else:
			dialogue.label(str(angle_rad_val)+ "rad gives " + str('%4.4f'%(angle_rad_val_rad)) + "deg").pack()
		
		dialogue.button("Close", Command(dialogue,DialogueBox.close) ).pack()

	def apply3(self):
		try:
			fluid_kin_val = self.fluid_kin.getFloatValue()
			fluid_dyn_val = self.fluid_dyn.getFloatValue()
			fluid_density_val = self.fluid_density.getFloatValue()
		
		except ValueError:
			Warning("Wrong input value in at least one of the entries. Must be a float or an integer value.")
			return
		
		if self.selecConvert_fluid.getValue() == "0":
			if (fluid_dyn_val <= 0 or fluid_density_val <= 0):
				Warning("Wrong input value in at least one of the entries. Must be a value stricly positive.")
				return
			else:
				fluid_kin_val = fluid_dyn_val/fluid_density_val
				dialogue = DialogueBox("Conversion Result")
				dialogue.label("Kinematic viscosity is equal to "+str('%6.6e'%(fluid_kin_val)) + "m2/s").pack()
				dialogue.button("Close", Command(dialogue,DialogueBox.close) ).pack()
		else:
			if (fluid_kin_val <= 0 or fluid_density_val <= 0):
				Warning("Wrong input value in at least one of the entries. Must be a value stricly positive.")
				return
			else:
				fluid_dyn_val = fluid_kin_val*fluid_density_val
				dialogue = DialogueBox("Conversion Result")
				dialogue.label("Dynamic viscosity is equal to "+str('%6.6e'%(fluid_dyn_val)) + "kg/(m.s)").pack()
				dialogue.button("Close", Command(dialogue,DialogueBox.close) ).pack()

### Instantiate the dialogue box
z = MyDialogue()