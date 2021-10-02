import os
import FreeCADGui as Gui
import FreeCAD as App
from freecad.FCCam import ICONPATH


class FCCamWorkbench(Gui.Workbench):
    MenuText = "FCCam"
    ToolTip = "add mechanical cam shapes"
    Icon = os.path.join(ICONPATH, "camIcon.svg")
    toolbox = []

    def GetClassName(self):
        return "Gui::PythonWorkbench"

    def Initialize(self):
        from .FCCamTools import addAxialCamCmd
        Gui.addCommand("addAxialCamCmd", addAxialCamCmd())
        self.toolbox = ["addAxialCamCmd"]
        self.appendToolbar("CamWB", self.toolbox)
        self.appendMenu("CamWB", self.toolbox)
        pass

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
