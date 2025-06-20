#                                                                             #
#                          Clear Computation directory                        #
#_____________________________________________________________________________#
#
#	NUMECA International s.a
#
#	Implementator : B. Mallol
#       Date	      : 23/05/2012
#______________________________________________________________________________
#
# Description: Clear Computation directory for Marine plugin in HEXPRESS
#______________________________________________________________________________

#!/bin/python

# for TCL windows
from Tk import *
import string

#import FM

# for classic commands
import os,sys,math,fileinput,string,time

print ''
print "---------------------------------------------------------"
print ">>>       SCRIPT TO CLEAR COMPUTATION DIRECTORY       <<<"
print '---------------------------------------------------------'
print ''

# get current project and computation info

project_path,project_name = get_project_file_name()
active_comp = get_active_computation()
comp_name = get_computation_name(active_comp)

print ' > Project path: ' + str(project_path)
print ' > Project name: ' + str(project_name)
print ' > Computation name: ' + str(comp_name)

class MyDialogue(DialogueBox):
	def __init__(self):
		DialogueBox.__init__(self, "Warning")
		self.show()
		self.mainFrame = self.frame()
		self.mainFrame.pack(side="top",fill="both")
		
		### Display general_page in main frame
		self.general_page(self.mainFrame)
		
		self.showUnderMouse()

	def general_page(self,parentFrame):
		
		self.general_page_frame = parentFrame.frame()
		self.general_page_frame.pack(side="top",fill="both")

		sentence_frame = self.general_page_frame.labelframe(label="The script is about to delete the active computation directory. Are you sure you want to proceed?")
		sentence_frame.pack(side="top",fill="x",padx = 2,pady = 3)
		
		self.closeB  = self.general_page_frame.button(text="No",command = Command(self,DialogueBox.close)).pack(side="right",padx=5,pady=5)
		apply = self.general_page_frame.button(text="Yes",command = Command(self,MyDialogue.apply)).pack(side="right",padx=5,pady=5)

	def apply(self):
		print ''
		print ' > Cleaning directory...'
		
		if sys.platform=='win32':
			os.system('rmdir /s /q '+str(project_path)+str(project_name[:-4])+'_'+str(comp_name))
		else:
			os.system('rm -fr '+str(project_path)+str(project_name[:-4])+'_'+str(comp_name))
		
		self.close()
		
		print ' > Cleaning done'
		print ''


### Instantiate the dialogue box
z = MyDialogue()