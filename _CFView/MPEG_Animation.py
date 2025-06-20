#--------------------------------------------------------------------------------------------#
#                       MPEG_Animation.py                                                    #
#--------------------------------------------------------------------------------------------#
#      Numeca International                                                                  #
#         Etienne Robin                                                          Feb 2001    #
#--------------------------------------------------------------------------------------------#
# Description : interface for the creation of mpeg animation                                 #
#--------------------------------------------------------------------------------------------#

import CFView

import os

#--------------------------------------------------------------------------------------------#

class MPEG_Animation:
    
    mpeg_exe = os.environ['NUMECA_BIN']+'/cfview/mpeg'
    
    # constructor 
    def __init__(self, name, outputPath, tmp_dir):
	self.__numOfPictures = 0
	self.__animationName = name
	self.__outputPath    = outputPath
	self.__tmpDir        = tmp_dir

    def addPicture(self):
	CFView.NTSCSave(self.__tmpDir+'/'+self.__animationName+`self.__numOfPictures`)
	self.__numOfPictures = self.__numOfPictures +1

    def saveAnimation(self):
	self.__numOfPictures = self.__numOfPictures-1;
	os.system(self.mpeg_exe+' -a 0 -b '+`self.__numOfPictures`+' '+self.__tmpDir+'/'+self.__animationName)
	if (os.name == 'posix'):
	    os.system('mv '+self.__tmpDir+'/'+self.__animationName+'.mpg '+self.__outputPath+'/'+self.__animationName+'.mpg')
	elif (os.name == 'dos'):
	    os.system('move '+self.__tmpDir+'/'+self.__animationName+'.mpg '+self.__outputPath+'/'+self.__animationName+'.mpg')
	for i in range(0,self.__numOfPictures+1):
	    os.remove(self.__tmpDir+'/'+self.__animationName+`i`+'.Y')
	    os.remove(self.__tmpDir+'/'+self.__animationName+`i`+'.U')
	    os.remove(self.__tmpDir+'/'+self.__animationName+`i`+'.V')
