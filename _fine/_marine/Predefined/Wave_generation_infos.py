#                                                                             #
#                          Mesh setup for wave generation                     #
#_____________________________________________________________________________#
#
#	NUMECA International s.a
#
#	Implementator : B. Mallol
#       Date	      : 23/05/2012
#______________________________________________________________________________
#
# Description: Mesh setup for wave generation for Marine module for HEXPRESS
#______________________________________________________________________________

#!/bin/python

# for TCL windows
from Tk import *
import string

# for classic commands
import os,sys,math,fileinput,string,time

# for HEXPRESS
import HXP

class MyDialogue(DialogueBox):
	def __init__(self):
		DialogueBox.__init__(self, "Infos for wave generation")
		self.show()
		
		self.mainFrame = self.frame()
		self.mainFrame.pack(side="top",fill="both")
		
		### Display general_page in main frame
		self.general_page(self.mainFrame)
		
		self.showUnderMouse()

	def general_page(self,parentFrame):
		self.general_page_frame = parentFrame.frame()
		self.general_page_frame.pack(side="top",fill="both")

		### user data
		
		ship_frame = self.general_page_frame.labelframe(label="Ship data").pack(side="top",fill="x",padx = 2,pady = 3)
		self.ship_length = ship_frame.entry(label="Ship length ",value = 1.0,width = 8,unit = '\[m\]' ).pack(side= "left",padx = 2)
		self.ship_speed = ship_frame.entry(label=" Ship speed ",value = 1.0,width = 8, unit = '\[m/s\]' ).pack(side= "left",padx = 2)
		
		wave_frame = self.general_page_frame.labelframe(label="Wave data").pack(side="top",fill="x",padx = 2,pady = 3)
		
		frame1 = wave_frame.frame().pack(side="top")
		self.wave_length = frame1.entry(label="Wave length (0 if unknown) ",value = 1.0,width = 8,unit='\[m\]' ).pack(side= "left",padx = 2)
		self.wave_period = frame1.entry(label="Wave period (0 if unknown) ",value = 1.0,width = 8,unit='\[s\]' ).pack(side= "left",padx = 2)
		
		frame2 = wave_frame.frame().pack(side="top")
		self.wave_height = frame2.entry(label="Wave height H (= 2A) ",value = 0.5,width = 8,labelwidth = 18, unit='\[m\]' ).pack(side= "left",padx = 2)
		self.wave_direction = frame2.entry(label="Wave direction ",value = 180.0,width = 8,labelwidth = 18, unit='\[m\]' ).pack(side= "left",padx = 2)
		
		frame3 = wave_frame.frame().pack(side="left")
		self.free_surface = frame3.entry(label="Free surface location ",value = 0.0,width = 8,unit='\[m\]' ).pack(side= "left",padx = 2)
		
		flow_frame = self.general_page_frame.labelframe(label="Flow data").pack(side="top",fill="x",padx = 2,pady = 3)
		frame4 = flow_frame.frame().pack(side="top")
		self.dyn_visc = frame4.entry(label="Dynamic viscosity (water) ",value = 0.00104362,width =10,unit='\[m2/s\]' ).pack(side= "left",padx = 2)
		self.water_density = frame4.entry(label="Density (water) ",value = 998.4,width = 8,unit='\[kg/m3\]' ).pack(side= "left",padx = 2)
		
		frame5 = flow_frame.frame().pack(side="left")
		self.gravity = frame5.entry(label="Gravity Intensity",value = 9.81,width = 8, unit='\[m2/s\]' ).pack(side = "left",padx = 2)
		
		default_frame = self.general_page_frame.labelframe(label="Time discretization").pack(side="top",fill="x",padx = 2,pady = 3)
		self.dt_wave_period = default_frame.entry(label="Nbr of time steps per wave period ",value = 80,width = 8)
		self.dt_wave_period.pack(side = "left",padx = 2)
		
		apply = self.general_page_frame.button(text="Compute",command = Command(self,MyDialogue.apply)).pack(side="right",padx=5,pady=5)

	def apply(self):
		try:
			ship_length = self.ship_length.getFloatValue()
			ship_speed = self.ship_speed.getFloatValue()
			wave_length = self.wave_length.getFloatValue()
			wave_period = self.wave_period.getFloatValue()
			wave_height = self.wave_height.getFloatValue()
			wave_direction = self.wave_direction.getFloatValue()
			free_surface = self.free_surface.getFloatValue()
			gravity = self.gravity.getFloatValue()
			dyn_visc = self.dyn_visc.getFloatValue()
			water_density = self.water_density.getFloatValue()
			dt_wave_period = self.dt_wave_period.getFloatValue()
			
		except ValueError:
			Warning("Wrong input value in at least one of the entries. Must be a float or integer value")
			return
		
		### variables definition
		text = ''
		
		#computed
		reynolds_number = water_density * ship_speed  * ship_length / dyn_visc
		froude_number   = ship_speed / ( sqrt( gravity * ship_length ) )

		if (wave_length == (0 or 0.0 or 0.)) and (wave_period == (0 or 0.0 or 0.)):
			Warning("The wave length or the wave period should be known")
			return
		else:
			if wave_length == (0 or 0.0 or 0.):
				wave_length = gravity*wave_period*wave_period/2/(math.pi)
			if wave_period == (0 or 0.0 or 0.):
				wave_period = sqrt(2*(math.pi)*wave_length/gravity)
		wave_steepness = 2*(math.pi)*(wave_height/2)/wave_length
		wave_celerity = wave_length/wave_period
		
		wave_freq = 1/wave_period
		adv_freq = cos(wave_direction/360*2*math.pi-math.pi)*ship_speed/wave_length
		encounter_freq = wave_freq+adv_freq
		encounter_period = 1/encounter_freq
		if wave_period == 0:
			part_vel = 0
		else:
			part_vel = math.pi*wave_height/wave_period
		if ship_speed == 0:
			time_step = encounter_period/dt_wave_period
		else:
			if [0.005*ship_length/ship_speed] > [encounter_period/dt_wave_period]:
				time_step = encounter_period/dt_wave_period
			else:
				time_step = 0.005*ship_length/ship_speed

		free_surf_DZ = 0.001*ship_length

		# CREATE REPORT

		text = text + 'Wave generation infos\n'
		text = text + '--------------------------------\n\n'
		text = text + "Wave length: "+str('%4.6f'%(wave_length))+" m - Wave period: "+str('%4.6f'%(wave_period))+" s\n"
		text = text + "Wave steepness: "+str('%4.6f'%(wave_steepness))+" - Wave celerity: "+str('%4.6f'%(wave_celerity))+" m/s\n\n"
		text = text + "Wave frequency: "+str('%4.6f'%(wave_freq))+" Hz - Advance frequency: "+str('%4.6f'%(adv_freq))+" Hz\n\n"
		text = text + "Encounter frequency: "+str('%4.6f'%(encounter_freq))+" Hz - Encounter period: "+str('%4.6f'%(encounter_period))+" s\n\n"
		text = text + "Max of particle velocity: "+str('%4.6f'%(part_vel))+" m/s - Suggested time step: "+str('%4.6f'%(time_step))+" s\n\n"
		
		text_message_box(text)


### Instantiate the dialogue box
z = MyDialogue()

