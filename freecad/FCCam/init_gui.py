import os
import FreeCADGui as Gui
import FreeCAD as App
from freecad.FCCam import ICONPATH


class FCCamWorkbench(Gui.Workbench):
    MenuText = "FCCam workbench"
    ToolTip = "add mechanical cam shapes"
    Icon = os.path.join(ICONPATH, "camIcon.svg")
    toolbox = []

    def GetClassName(self):
        return "Gui::PythonWorkbench"

    def Initialize(self):
        pas

    def Activated(self):
        '''
        code which should be computed when a user switch to this workbench
        '''
        pass

    def Deactivated(self):
        '''
        code which should be computed when this workbench is deactivated
        '''
        pass


Gui.addWorkbench(FCCamWorkbench())
