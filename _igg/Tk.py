#--------------------------------------------------------------------------------------------#
#      Numeca International                                                                  #
#         M.P.                                                           May 2010            #
#         F.A.                                                           Sep 2015            #
#--------------------------------------------------------------------------------------------#

import string,types

try:
    from IGGSystem import *
except:
    pass
try:
    from CFView import *
except:
    pass

#--------------------------------------------------------------------------------------------
# private function to quote a string

def _quote(strin):
    return '\"' + strin + '\"'

#--------------------------------------------------------------------------------------------

class Variable:
    # static member
    counter = 0

    def __init__(self, value = "" ):
        self.name = Variable._getDefaultName()
        Tcl_SetVar_( self.name, str(value) )

    def setValue(self, value):
        Tcl_SetVar_( self.name, str(value) )

    def getValue(self):
        return Tcl_GetVar_( self.name )

    def getName(self):
        return self.name

    @staticmethod
    def _getDefaultName():
        Variable.counter = Variable.counter + 1
        return '_NIprivVar' + str(Variable.counter)

#--------------------------------------------------------------------------------------------

class Command:
    # Constructor. if one arg passed, must be a function
    # If two args passed , must be an object + member function
    def __init__(self, *args ):
        if len(args) == 2:
            self.object   = args[0]
            self.function = args[1]
        elif len(args) == 1:
            self.object   = 0
            self.function = args[0]
        else:
            raise "Command, wrong number of args"

    def execute(self):
        if self.object != 0:
            self.function(self.object)
        else: self.function()

    def execute_1_arg(self,arg):
        if self.object != 0:
            self.function(self.object,arg)
        else: self.function(arg)

#--------------------------------------------------------------------------------------------

class Widget(object):
    #
    # static members
    curId   = 0
    objects = {}

    # -----------------------------------------------------

    def __init__(self,parent, command = "" ):
        self.parent  = parent
        self.id      = Widget._getUniqueId(self)
        self.command = ""

        if isinstance(command, Command):
            self.command = command
        elif type(command) == types.FunctionType:
            self.command = Command(command)

    # -----------------------------------------------------

    def pack(self,side="left",fill = "", expand = "no" , anchor = "", padx = 1, pady = 1):

        name = self._tclName()

        command = "pack "     + name   +\
                  " -side "   + side   +\
                  " -expand " + expand +\
                  " -padx   " + `padx` +\
                  " -pady   " + `pady`

        if fill != "":
            command += " -fill " + fill

        if anchor != "":
            command += " -anchor " + anchor

        eval_tcl_string( command )

        # allow chained calls
        return self

    def unpack(self):
        eval_tcl_string( "pack forget " + self._tclName() )
        return self

    @staticmethod
    def _getUniqueId(object):
        Widget.curId                 = Widget.curId + 1
        Widget.objects[Widget.curId] = object

        return Widget.curId

    @staticmethod
    def execute(objectID):
        object =  Widget.objects[objectID]
        object.command.execute()

    @staticmethod
    def execute_1_arg(objectID,arg):
        object =  Widget.objects[objectID]
        object.command.execute_1_arg(arg)

    def _tclName(self):

        name = self.parent._tclInsertName() + "." + str( self.id )

        return name

    def enable(self, state ):
        ''' Enable or disable the entry. state is a boolean '''
        if( state == False ):
            eval_tcl_string( self._tclName() + ' config -state disabled ' )
        else:
            eval_tcl_string( self._tclName() + ' config -state normal ' )

    def _tclInsertName(self):

        return self._tclName()

    def text(self, text="" ):
        b = Text(self, text = text )

        return b

    def button(self, text="", command=""  , image_path = ""):
        b = Button(self, text = text , command = command , image_path =image_path)
        return b

    def checkbutton(self, text="" , initValue=1, command="" ):
        b = CheckButton(self, text = text , initValue = initValue , command = command )

        return b

    def radiobutton(self, text="" , variable = "" , value = 0, command="" ):
        b = RadioButton(self, text=text , variable=variable, value=value, command=command )
        return b

    def label(self, text="", width = 5,anchor ='w'):
        b = Label(self, text=text, anchor = anchor )
        return b

    def image(self, image_path,anchor ='w'):
        b = Image(self, image_path,anchor)
        return b

    def entry(self, label = "", value = "" , command = "" , unit = -1 , width = 5 , labelwidth = -1, align ='left' ):
        b = Entry(self, label = label, value = value , command = command, unit = unit , width = width , labelwidth = labelwidth, align =align )
        return b

    def combobox(self, label = "", items = [] , command = "" ):
        b = ComboBox(self, label = label, items = items , command = command )
        return b

    def labelframe(self,label = "" ):
        b = LabelFrame(self,label = label)
        return b

    def notebook(self):
        b = NoteBook(self)
        return b

    def panedwindow(self):
        b = PanedWindow(self)
        return b

    def frame(self):
        b = Frame(self)
        return b

    def scrolled_frame(self,height=-1):
        b = ScrolledFrame(self,height)
        return b

    def list( self, items , selectCommand = "",width = 0, height = 0,multi_select = True):
        return List( self, items , selectCommand, width, height, multi_select )


#--------------------------------------------------------------------------------------------

class DialogueBox(Widget):
    def __init__(self,title = "", show = 0, enableBalloons = False ):
        Widget.__init__(self,0)
        self.title = title

        eval_tcl_string( " toplevel "   + self._tclName() )

        if show == 0:
            eval_tcl_string( "wm withdraw " + self._tclName() )

        if title != "":
            eval_tcl_string( "wm title "    + self._tclName() +  ' \"' + title +  '\"' )
        eval_tcl_string( "global app; wm transient " + self._tclName() + " $app(mainWin)" )

        if enableBalloons:
            # allows the dialog box to display tixBalloon widgets
            eval_tcl_string("set app(balloonHelp) [tixBalloon "+self._tclName()+".balloon -initwait 300]")


    def show(self):
        eval_tcl_string( "wm deiconify " + self._tclName() )

    def showUnderMouse(self):
        eval_tcl_string( "wm deiconify " + self._tclName() )
        eval_tcl_string("set absx [expr [winfo pointerx .] - 100] ; \
        set absy [expr [winfo pointery .] - 100] ; \
        wm geometry  " + self._tclName() + " \"+$absx+$absy\"")

    def showCentered(self, over=""):
        tclName = "$app(mainWin)"

        if over != "":
            tclName = over._tclName()

        eval_tcl_string("global app; wm transient " + self._tclName() + " " + tclName)
        eval_tcl_string("center_window " + self._tclName() + " " + tclName)
        eval_tcl_string("wm deiconify " + self._tclName())

    #@staticmethod
    def addBalloonToControl(self,control, msg):
        # links a tix balloon to the control. The parent window must have enabled this feature before
        # could be a member of Widget. But classes like DialogBox are Widget wich cannot use this function
        btn_tclName = control._tclName()
        eval_tcl_string('$app(balloonHelp) bind '+btn_tclName+' -msg \"'+msg+'\" -statusmsg \"'+msg+'\"')

    def close(self):
        eval_tcl_string( "destroy " + self._tclName() )

    def _tclName(self):
        return "." + `self.id`

#--------------------------------------------------------------------------------------------#

class Wizard(DialogueBox):
    def __init__(self,name = ""):
        DialogueBox.__init__(self,name)

        self.pages        = []
        self.curPageIndex = -1
        self.curPageFrame = -1
        self.frames       = {}

        self.mainFrame = self.frame()
        self.mainFrame.pack(side="top",fill="both")

    def addPage(self,page):
        self.pages.append( page )

    def addButtons(self,apply_text = "Apply"):

        buttonsFrame = self.frame()
        buttonsFrame.pack(side="top",anchor = "se" , expand = "yes" )

        self.prev    = buttonsFrame.button(text="Previous <<" ,command = Command(self,Wizard.gotoPreviousPage ) )
        self.next    = buttonsFrame.button(text="Next >>"     ,command = Command(self,Wizard.gotoNextPage ) )
        self.closeB  = buttonsFrame.button(text="Cancel"      ,command = Command(self,DialogueBox.close) )
        self.applyB  = buttonsFrame.button(text=apply_text    ,command = Command(self,Wizard._apply ) )

        self.prev  .pack(side="left").enable( False )
        self.next  .pack(side="left")
        self.closeB.pack(side="right")

        def startWizard(self):
            if len( self.pages ) == 0:
                raise "No page in Wizard"

            self.gotoNextPage()

        self.show()

    def gotoNextPage(self):

        nextPageIndex = self.curPageIndex + 1

        if self.curPageIndex != -1 and nextPageIndex < len( self.pages ) :
            self.frames[self.curPageIndex].unpack()
            self.prev.enable( True )

            if nextPageIndex < len( self.pages ) :
                self.curPageIndex = nextPageIndex

            if self.curPageIndex in self.frames:
                curPageFrame = self.frames[self.curPageIndex]
            else:
                curPageFrame = self.pages[self.curPageIndex]( self.mainFrame )
                self.frames[self.curPageIndex] = curPageFrame
            curPageFrame.pack(side="top",fill="both")

            if self.curPageIndex == len( self.pages ) - 1 :
                self.closeB.unpack()
                self.applyB.pack(side="right")
                self.next.enable( False )

    def gotoPreviousPage(self):

        previousPageIndex = self.curPageIndex - 1

        if self.curPageIndex != -1 and previousPageIndex >= 0 :
            self.frames[self.curPageIndex].unpack()
            self.next.enable( True )

            if previousPageIndex >= 0 :
                self.curPageIndex = previousPageIndex

            if self.curPageIndex in self.frames:
                curPageFrame = self.frames[self.curPageIndex]
                curPageFrame.pack()
            else:
                curPageFrame = self.pages[self.curPageIndex]( self.mainFrame )
                self.frames[self.curPageIndex] = curPageFrame
            curPageFrame.pack(side="top",fill="both")

            self.applyB.unpack()
            self.closeB.pack(side="right")

            if self.curPageIndex == 0 :
                self.prev.enable( False )

    def _apply(self):
        self.apply()
        self.close()


#--------------------------------------------------------------------------------------------
class ColumnCompatibleFrame:
    # main class defining functions required to configure a grid system for widgets in a frame
    def __init__(self, nbColumn = 1, nbLine = 1):
        self.nbColumn = nbColumn
        self.nbLine = nbLine

    def columnConfigure(self, column = 1, weight = 1, pad = 0, minsize = 0):
        eval_tcl_string('grid columnconfigure '+self._tclInsertName()+' '+str(column)+' -weight '+str(weight)+ ' -pad '+str(pad)+' -minsize '+str(minsize))

    def rowConfigure(self, row = 1, weight = 1, pad = 0, minsize = 0):
        eval_tcl_string('grid rowconfigure '+self._tclInsertName()+' '+str(row)+' -weight '+str(weight)+ ' -pad '+str(pad)+' -minsize '+str(minsize))

    @staticmethod
    def putOnGrid(control, column = 1, row = 1, sticky = 'snew', columnspan = 1):
        eval_tcl_string('grid config '+control._tclInsertName()+' -column '+str(column)+' -row '+str(row)+' -sticky \"'+sticky+'\" -columnspan '+str(columnspan))

#--------------------------------------------------------------------------------------------

class Frame(ColumnCompatibleFrame, Widget):
    def __init__(self,parent):
        ColumnCompatibleFrame.__init__(self)
        Widget.__init__(self,parent)

        eval_tcl_string( "frame " + self._tclName() )

#--------------------------------------------------------------------------------------------

class ScrolledFrame(ColumnCompatibleFrame, Widget):
    def __init__(self,parent,height=-1):
        ColumnCompatibleFrame.__init__(self)
        Widget.__init__(self,parent)

        command = "tixScrolledWindow " + self._tclName() + " -scrollbar auto "
        if height !=1:
            command += " -height " + str(height)
        eval_tcl_string( command )
        tclWidget = eval_tcl_string( self._tclName() + ' subwidget window')


    def _tclInsertName(self):
        
        name = self._tclName() + ".f2.window"
        return name

#--------------------------------------------------------------------------------------------

class PrivateFrame(ColumnCompatibleFrame, Widget):
    ''' Represents a frame whose tclName is automatically consructed by tcl and passed to the constructor '''
    def __init__(self,tclName):
        ColumnCompatibleFrame.__init__(self)
        Widget.__init__(self,0)
        self.tclName = tclName

    def _tclName(self):
        return self.tclName

#--------------------------------------------------------------------------------------------

class LabelFrame(ColumnCompatibleFrame, Widget):
    def __init__(self,parent, label="" ):
        ColumnCompatibleFrame.__init__(self)
        Widget.__init__( self,parent )

        eval_tcl_string( "tixLabelFrame " + self._tclName() + " -label " + '\"' + label + '\"' )

    def _tclInsertName(self):

        name = self._tclName() + ".border.frame"

        return name

#--------------------------------------------------------------------------------------------

class NoteBook(Widget):
    def __init__(self,parent):
        Widget.__init__( self,parent )

        eval_tcl_string( "tixNoteBook " + self._tclInsertName() + ' -ipadx 3 -ipady 3 ' )

    def addPage(self, label ):

        # page name may not contain white spaces nor start with an uppercase letter
        page_name = string.lower( label )
        page_name = string.replace(page_name , ' ','')

        tclWidget = eval_tcl_string( self._tclInsertName() + ' add ' + page_name + ' -label ' +  '\"' + label  + '\"'  )
        tclWidget = eval_tcl_string( self._tclInsertName() + ' subwidget ' + page_name )

        return PrivateFrame( tclWidget )

#--------------------------------------------------------------------------------------------

class PanedWindow(Widget):
    def __init__(self,parent):
        Widget.__init__( self,parent )

        eval_tcl_string( "tixPanedWindow " + self._tclInsertName() + ' -paneborderwidth 1 -separatorbg gray50 -orientation horizontal ' )

        self.leftFrame  = eval_tcl_string( self._tclInsertName() + ' add left'  )
        self.rightFrame = eval_tcl_string( self._tclInsertName() + ' add right' )

    def getLeftFrame(self):
        return PrivateFrame(self.leftFrame)

    def getRightFrame(self):
        return PrivateFrame(self.rightFrame)

#--------------------------------------------------------------------------------------------

class Label(Widget):

    def __init__(self,parent,text="",font="", anchor ='w'):
        Widget.__init__(self, parent)

        name = self._tclInsertName()

        if font == "":
            theCommand = "label " + name + ' -text \"' + text + '\"'
        else:
            theCommand = "global nifonts; label " + name + ' -text \"' + text + '\"' \
                + ' -font \"nifonts(' + font + ')\"'


        eval_tcl_string( theCommand )
        eval_tcl_string( name + ' config -anchor ' + anchor )

    def updateLabel(self,text):
        tclname = self._tclName()
	theCommand = tclname + ' configure -text \"'+ text+'\"'
        eval_tcl_string( theCommand )

#--------------------------------------------------------------------------------------------

class Image(Widget):

    def __init__(self,parent,image_path, anchor ='w'):
        Widget.__init__(self, parent)

        name = self._tclInsertName()

        theCommand = "label " + name + " -image [image create photo -file " + image_path + "]"

        eval_tcl_string( theCommand )

        eval_tcl_string( name + ' config -anchor ' + anchor )


#--------------------------------------------------------------------------------------------

class Button(Widget):

    def __init__(self,parent,text="",command="", image_path = ""):
        Widget.__init__(self, parent, command )

        name = self._tclInsertName()

        theCommand = "button " + name
        if image_path <> "":
            theCommand +=" -image [image create photo"
            theCommand += " -file " + image_path + "]"

        if text == "":
            if image_path == "":
                theCommand +=' -text \"\" '
        else:
            theCommand +=' -text \"' + text + '\"'


        if command != "":
            theCommand += " -command " + '\"' + " System:run_python " + " Widget.execute ( " +`self.id`  + " ) " + '\"'

        eval_tcl_string( theCommand )

    def enable(self, state ):
        ''' Enable or disable the button. state is a boolean '''
        if( state == False ):
            eval_tcl_string( self._tclName() + ' config -state disabled ' )
        else:
            eval_tcl_string( self._tclName() + ' config -state normal ' )

    def setText(self, text = ""):
        tclname = self._tclName()
	eval_tcl_string(tclname+ ' configure -text \"'+ text+'\"')

#--------------------------------------------------------------------------------------------

class CheckButton(Widget):

    def __init__(self, parent,text="" , initValue=1 , command="" ):
        Widget.__init__(self, parent, command )

        if initValue !=0 and initValue != 1:
            raise 'CheckButton initValue error. Must be 0 or 1'

        name = self._tclInsertName()

        self.variable = Variable()

        self.variable.setValue( str(initValue) )

        theCommand = "checkbutton " + name + ' -text \"' + text + '\"' + ' -variable ' + self.variable.getName()

        if command != "":
            theCommand += " -command " + '\"' + " System:run_python " + " Widget.execute ( " +`self.id`  + " ) " + '\"'

        eval_tcl_string( theCommand )

    def getState(self):
        ''' returns 0 or 1 '''
        return string.atoi( self.variable.getValue() )

    def enable(self, state):
        ''' Enable or disable the check button. state is a boolean '''

        if state:
            eval_tcl_string( 'global nicolors; ' + self._tclName() +
            	' config -state normal -selectcolor $nicolors(checkbox,select)' )
        else:
            eval_tcl_string( 'global nicolors; ' + self._tclName() +
            	' config -state disabled -selectcolor $nicolors(checkbox,disabled)' )

#--------------------------------------------------------------------------------------------

class RadioButton(Widget):

    def __init__(self, parent, text = "" , variable = "" , value = 0, command="" ):
        Widget.__init__(self, parent, command )

        self.variable = variable

        if variable == "":
            self.variable = Variable()

        name = self._tclInsertName()

        theCommand = "radiobutton " + name + ' -text \"' + text + '\"' + ' -variable ' + self.variable.getName() + ' -value ' + str(value)

        if command != "":
            theCommand += " -command " + '\"' + " System:run_python " + " Widget.execute ( " +`self.id`  + " ) " + '\"'

        eval_tcl_string( theCommand )

    def enable(self, state):
        ''' Enable or disable the radio button. state is a boolean '''

        if state:
            eval_tcl_string( 'global nicolors; ' + self._tclName() +
            	' config -state normal -selectcolor $nicolors(checkbox,select)' )
        else:
            eval_tcl_string( 'global nicolors; ' + self._tclName() +
            	' config -state disabled -selectcolor $nicolors(checkbox,disabled)' )
#--------------------------------------------------------------------------------------------

class Entry(Widget):

    def __init__( self,parent, label="", value = "" , command="" , unit = -1 , width = 5 , labelwidth = -1, align ='left' ):
        Widget.__init__( self, parent, command )

        # Create container frame
        framename = self._tclName()
        eval_tcl_string( 'frame ' + framename )

        name = self._tclName() + '.entry'

        eval_tcl_string ( "tixLabelEntry " + name + " -label " + '\"' + label + '\"' )
        eval_tcl_string ( 'pack ' + self._tclName() + '.entry'  + ' -side left -fill x -expand 1' )

        eval_tcl_string( self._getEntry() + ' config -width ' + str(width) )

        eval_tcl_string( self._getEntry() + ' config -justify ' + align )

        if labelwidth != 1:
            eval_tcl_string( self._getLabel() + ' config -width ' + str(labelwidth) )

        if value != "":
            eval_tcl_string( self._getEntry() + ' insert end ' + str(value) )

        if command != "":

            theCommand = "bind [" + name + " subwidget entry] <Return> " +\
                         '\"' + " System:run_python " + " Widget.execute ( " +`self.id`  + " ) " + '\"'
            eval_tcl_string( theCommand )

        self.unit = ""

        if unit != -1:
            self.unit = unit
            unitname = framename + '.unit'
            self.unit_tkname = unitname
            eval_tcl_string ( "label " + unitname + " -text " + '\" ' + unit + '\"' )
            eval_tcl_string ( 'pack '  + unitname + ' -fill x -expand 1' )

    def changeUnit(self,unit):
        _unit = self._tclName() + '.unit'
        eval_tcl_string ( _unit + ' config -text ' + unit )

    def selectAll(self):
        eval_tcl_string(self._getEntry() + " select range 0 end" )

    def focus(self):
        eval_tcl_string("focus " +  self._getEntry() )

    def setValue(self,value):
        eval_tcl_string( self._getEntry() + ' delete 0 end ' )
        eval_tcl_string( self._getEntry() + ' insert 0 ' + _quote( str(value) ) )

    def enable(self, state ):
        ''' Enable or disable the entry. state is a boolean '''

        if state:
            eval_tcl_string( 'global nicolors; ' + self._getEntry() + ' config -state normal ' +
                '-bg $nicolors(background,normal_state) -fg $nicolors(foreground)' )
            eval_tcl_string( 'global nicolors; ' + self._getLabel() +
                ' config -fg $nicolors(foreground)' )

            if self.unit != "":
                eval_tcl_string( self.unit_tkname + ' config -fg $::nicolors(foreground)' )
        else:
            eval_tcl_string( 'global nicolors; ' + self._getEntry() + ' config -state disabled ' +
                '-bg $nicolors(background,disabled_state) -fg $nicolors(foreground,disabled_state)' )
            eval_tcl_string( 'global nicolors; ' + self._getLabel() +
                ' config -fg $nicolors(foreground,disabled_state)')

            if self.unit != "":
                eval_tcl_string( self.unit_tkname + ' config -fg $::nicolors(foreground,disabled_state)' )

    def setUnit(self, newUnit):
        ''' Change the unit. '''
        unitlabel = self._tclName() + '.unit'
        eval_tcl_string( 'if {[winfo exists ' + unitlabel + ']} {' + unitlabel + ' config -text "' + newUnit + '"}' )


    # -----------------------------------------------------

    def getStringValue(self):

        name = self._getEntryWidgetName()

        command = "[" + name + " subwidget entry] get "

        strin =  eval_tcl_string( command )
        values = strin.split()

        if len(values) == 0:
            return ""

        return ' '.join( values )

    def getFloatValue(self):
        name = self._getEntryWidgetName()

        command = "[" + name + " subwidget entry] get "

        strin =  eval_tcl_string( command )
        values = strin.split()

        if len(values) == 0:

            raise ValueError

        try:
            a =  string.atof( values[0] )
        except:
            raise ValueError

        return string.atof( values[0] )

    def getIntValue(self):

        name = self._getEntryWidgetName()

        command = "[" + name + " subwidget entry] get "

        strin =  eval_tcl_string( command )
        values = strin.split()

        if len(values) == 0:
            raise ValueError

        return string.atoi(strin)

    def getFloatValues(self):

        name = self._getEntryWidgetName()

        command = "[" + name + " subwidget entry] get "

        strin =  eval_tcl_string( command )
        values = strin.split()

        retVal = []
        for val in values:
            retVal.append( string.atof(strin) )

        return retVal

    def _getEntryWidgetName(self):
        return self._tclName() + '.entry'

    def _getEntry(self):
        return '[' + self._getEntryWidgetName() + ' subwidget entry] '

    def _getLabel(self):
        return '[' + self._getEntryWidgetName() + ' subwidget label] '

#--------------------------------------------------------------------------------------------

class Text(Widget):

    def __init__( self,parent, text = "" , command="" ,width = 500):
        Widget.__init__( self, parent, command )

        name = self._tclName()

        theCommand = "tixScrolledText " + name + " -scrollbar y  -bg white -width " + str(width)
        eval_tcl_string( theCommand )

        self.append(text)

    def append(self,text):
        text = str(text) + "\n"
        command = self._getTextWidget() + ' insert end ' + '\"' + text + '\"'
        eval_tcl_string( command )

    def clear(self):
        command = self._getTextWidget() + ' delete 0.0 end '
        eval_tcl_string( command )

    def _getTextWidget(self):
        return '[' + self._tclName() + ' subwidget text] '

#--------------------------------------------------------------------------------------------

class Warning:
    def __init__(self, message, parent = None):
        cmd = 'okMessage {' + message + '} Error'

        if parent is not None:
            cmd += ' CENTER ' + parent._tclName()

        eval_tcl_string(cmd)

#--------------------------------------------------------------------------------------------

class FileChooserRead(Widget):

    def __init__(self,message , filter = "*.*" , command = "", parent_dialogue = None):
        Widget.__init__(self, 0, command )
        com = '"' + " System:run_python_1_tcl_arg Widget.execute_1_arg ( " +`self.id`  + " ) "  + '"'
        tclCommand = ' FileChooser:selectRead ' + '"' + message + '" ' + filter + ' ' + com

        if parent_dialogue is not None:
            tclCommand += ' "" -1 "" ' + parent_dialogue._tclName()

        eval_tcl_string( tclCommand )

#--------------------------------------------------------------------------------------------

class FileChooserWrite(Widget):

    def __init__(self,message , command = "", filter = "*.*", parent_dialogue = None):
        Widget.__init__(self, 0, command )
        com = '"' + " System:run_python_1_tcl_arg Widget.execute_1_arg ( " +`self.id`  + " ) "  + '"'
        tclCommand = ' FileChooser:selectWrite ' + '"' + message + '" ' + filter + ' ' + com

        if parent_dialogue is not None:
            tclCommand += ' "" -1 "" ' + parent_dialogue._tclName()

        eval_tcl_string( tclCommand )

#--------------------------------------------------------------------------------------------

class List(Widget):

    def __init__( self, parent, items , selectCommand = "",width = 0,height = 0,multi_select = True ):
        Widget.__init__(self,parent, selectCommand )

        name = self._tclName()

        theCommand = "tixTree " + name
        eval_tcl_string( theCommand )

        if selectCommand != "":
            theCommand = name + ' config -browsecmd ' +\
                         '\{' + " System:run_python_1_tcl_arg \" Widget.execute_1_arg ( " +`self.id`  + " ) \"" + '\}'
            eval_tcl_string( theCommand )

        hlist = "[" + self._tclName() + " subwidget hlist ]"

        if multi_select == True:
            eval_tcl_string( hlist + " config -selectmode extended " )

        if width >0:
            eval_tcl_string( hlist + ' config -width ' + str(width) )

        if height >0:
            eval_tcl_string( hlist + ' config -height ' + str(height) )

#                theCommand = hlist + "add 0 -bitmap $hexa(tree_ck_on) "
#                eval_tcl_string( theCommand )

        for item in items:
            theCommand = hlist + ' addchild "" -text ' +  '\"' + item +  '\"'
            eval_tcl_string( theCommand )

    def appendItem(self,itemText):

        return eval_tcl_string( self._getHList() + ' addchild "" -text ' +  '\"' + itemText +  '\"' )

    def removeItem(self,itemId):

        eval_tcl_string( self._getHList() + ' delete entry ' +  str(itemId) )

    def renameItem(self, itemId, newName ):
        eval_tcl_string( self._getHList() + ' entryconfigure ' + str(itemId) + ' -text ' + newName )

    def getItems(self):
        items = []

        itemIds =  eval_tcl_string( self._getHList() + ' info children ' )
        for itemId in itemIds.split():
            item = eval_tcl_string( self._getHList() + ' item cget ' + itemId + ' 0 -text ' )
            items.append( item )
        return items

    def getItemFromId(self,id):
        return eval_tcl_string( self._getHList() + ' item cget ' + str(id) + ' 0 -text ' )

    def getSelection(self):

        hlist = self._getHList()
        theCommand = hlist + ' selection get '

        # get selection from tcl. Output is of the form "0 2 3"
        selection = eval_tcl_string( theCommand )

        rList = []
        for item in string.split(selection):
            rList.append( int(item) )
        return rList

    def _getHList(self):
        return "[" + self._tclName() + " subwidget hlist ]"

    def enable(self, state ):
        if( state == False ):
            command = 'foreach item [' + self._getHList() + ' info children] { ' + self._getHList() + ' entryconfigure $item -state disabled }'
            eval_tcl_string( command )
        else:
            command = 'foreach item [' + self._getHList() + ' info children] { ' + self._getHList() + ' entryconfigure $item -state normal }'

            eval_tcl_string( command )


#--------------------------------------------------------------------------------------------

class ComboBox(Widget):

    def __init__( self, parent, label = "", items = [] , command = "" ):
        Widget.__init__(self,parent, command )

        self.variable = Variable()

        theCommand = "tixComboBox " + self._tclName() + ' -label ' + _quote(label) + ' -variable ' + self.variable.getName()

        if command != "":
            theCommand += " -command " + '\"' + " System:run_python_1_tcl_arg Widget.execute_1_arg ( " +`self.id`  + " ) " + '\"'

        eval_tcl_string( theCommand )

        for item in items:
            eval_tcl_string( self._getListBox() + ' insert end ' + _quote( str(item) ) )

        if len(items) > 0:
            self.setValue( items[0] )

    def getValue(self):
        return self.variable.getValue()

    def setValue(self, value ):
        self.variable.setValue( value )

    def _getListBox(self):
        return '[' + self._tclName() + ' subwidget listbox] '

    def _getEntry(self):
        return '[' + self._tclName() + ' subwidget entry] '

#--------------------------------------------------------------------------------------------



#--------------------------------------------------------------------------------------------

class FileEntry(Widget):

    def __init__( self,parent, label="", title="", openMode = "r",  value = "" , variable = "", filter = "*.*",  command="" ,  width = 5 , labelwidth = -1 ):
        Widget.__init__( self, parent, command )

        # parent     : parent widget
        # label      : text displayed next to the input field
        # title      : title of the window selecting a file
        # openMode   : r|w (read or write)
        # value      : initial value of the entry
        # variable   : variable to update with the value of the entry
        # filter    : file formats filters
        # command    : callback with one parameter
        # width      : width of the entry
        # labelwidth : width of the label

        self.variable = variable

        if variable == "":
            self.variable = Variable()

        # Create container frame
        name = self._tclName()

        theCommand = "nitixFileEntry " + name
        if label != "":
            theCommand +=" -label " + '\"' + label + '\"'

        if title != "":
            theCommand +=' -title \"'+title+'\"'

        theCommand +=' -filters '+filter

        theCommand +=' -openmode \"'+openMode+'\"'
        theCommand += ' -variable ' + self.variable.getName()

        if command != "":
            theCommand += " -command " + '\"' + " System:run_python_1_tcl_arg Widget.execute_1_arg ( " +`self.id`  + " ) " + '\"'

        eval_tcl_string(theCommand)

        eval_tcl_string( self._getEntry() + ' config -width ' + str(width) )

        if labelwidth != 1:
            eval_tcl_string( self._getLabel() + ' config -width ' + str(labelwidth) )

        if value != "":
            eval_tcl_string( self._getEntry() + ' insert end ' + str(value) )


    def focus(self):
        eval_tcl_string("focus " +  self._getEntry() )

    def setValue(self,value):
        eval_tcl_string( self._getEntry() + ' delete 0 end ' )
        eval_tcl_string( self._getEntry() + ' insert 0 ' +'\"' +  str(value) + '\"')

    def getValue(self):
        return self.variable.getValue()

    def enable(self, state ):
        ''' Enable or disable the entry. state is a boolean '''
        if( state == False ):
            eval_tcl_string( self._tclName() + ' config -state disabled ' )
        else:
            eval_tcl_string( self._tclName() + ' config -state normal ' )

    def getFileName(self):
        return self.variable.getValue()

    # -----------------------------------------------------

    def _getEntryWidgetName(self):
        return self._tclName()

    def _getEntry(self):
        return '[' + self._getEntryWidgetName() + ' subwidget entry] '

    def _getLabel(self):
        return '[' + self._getEntryWidgetName() + ' subwidget label] '

#--------------------------------------------------------------------------------------------

class ReliefButton(Widget):

    def __init__(self,parent,text="", command=""):
        Widget.__init__(self, parent, command )

        name = self._tclInsertName()

        theCommand = "relief_button " + name

        if text == "":
            if image_path == "":
                theCommand +=' \"\" '
        else:
            theCommand +=' \"' + text + '\"'


        if command != "":
            theCommand += ' \"System:run_python Widget.execute ( ' + str(self.id)  + ' ) \"'

        theCommand += ' \"black\"'

        eval_tcl_string( theCommand )

    def enable(self, state ):
        ''' Enable or disable the entry. state is a boolean '''
        if( state == False ):
            eval_tcl_string( self._tclName() + ' config -state disabled ' )
        else:
            eval_tcl_string( self._tclName() + ' config -state normal ' )
