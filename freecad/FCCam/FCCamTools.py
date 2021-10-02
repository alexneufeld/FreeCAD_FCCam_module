import os
import math as m
from math import pi as π
from matplotlib import pyplot as plt
import numpy as np
from freecad.FCCam import ICONPATH

import FreeCAD
import Part
import FreeCADGui as Gui


def uniform(β, L, θ):
    return L*(θ/β)


def parabolic(β, L, θ):
    return 2*L*(θ/β)**2*(θ < β/2)+L*(-1+4*(θ/β)-2*(θ/β)**2)*(θ >= β/2)


def harmonic(β, L, θ):
    return (L/2)*(1-np.cos(π*θ/β))


def cycloidal(β, L, θ):
    return L*(θ/β-np.sin((2*π*θ)/β)/(2*π))


def dwell(β, L, θ):
    return θ*0


def numericderivative(f, x, interval=1e-4):
    return (f(x+interval/2)-f(x-interval/2))/interval


def discrete_derivative(x, y):
    y2 = np.insert(y[1:], [len(y)-1], [y[0]])
    y1 = np.insert(y[:-1], [0], [y[-1]])
    x2 = np.insert(x[1:], [len(x)-1], [x[0]])
    x1 = np.insert(x[:-1], [0], [x[-1]])
    return (y2-y1)/(x2-x1)


def polar2xy(r, θ):
    return (r*np.cos(θ), r*np.sin(θ))


def knife_edge_translating_cam(r_b, θ, f_θ, S):
    R_0 = m.sqrt(r_b**2-S**2)
    fp = discrete_derivative(θ, f_θ)
    R = R_0 + f_θ
    r_c = np.sqrt(S**2+R**2)
    γ_c = π/2 - np.arctan2(S, R)
    φ = π/2 - γ_c - np.arctan2(R*fp, r_c**2)
    A = γ_c - θ
    return (r_c, A)


def roller_translating_cam(r_b, r_r, θ, f_θ, S):
    R_0 = m.sqrt((r_b+r_r)**2-S**2)
    R = R_0 + f_θ
    fp = discrete_derivative(θ, f_θ)
    φ = np.arctan2(fp-S, R)
    γ_c = π/2-np.arctan2(S+r_r*np.sin(φ), R-r_r*np.cos(φ))
    r_c = np.sqrt((R-r_r*np.cos(φ))**2-S**2)
    A = γ_c - θ
    return (r_c, A)


test = [
    # [type, end angle, lift]
    ["dwell", 60, 0],
    ["cycloidal", 120, 2],
    ["dwell", 240, 0],
    ["parabolic", 300, -2],
    ["dwell", 360, 0]
]

function_map = {
    "dwell": dwell,
    "uniform": uniform,
    "parabolic": parabolic,
    "harmonic": harmonic,
    "cycloidal": cycloidal
}


def displacement(data):
    split_angle = 0
    start_lift = 0
    x_total = np.array([])
    y_total = np.array([])
    for (ftype, end_angle, lift) in data:
        motion_f = function_map[ftype]
        x_vals = np.linspace(0, end_angle-split_angle, 10)[:-1]
        y_vals = motion_f(end_angle-split_angle, lift, x_vals)
        x_vals += split_angle
        y_vals += start_lift
        x_total = np.concatenate((x_total, x_vals))
        y_total = np.concatenate((y_total, y_vals))
        split_angle = end_angle
        start_lift += lift
    # plt.show()
    return (x_total, y_total)


def displacement_at(ang, data):
    split_angle = 0
    start_lift = 0
    for (ftype, end_angle, lift) in data:
        motion_f = function_map[ftype]
        if split_angle <= ang and ang <= end_angle:
            S = motion_f(end_angle-split_angle, lift, ang-split_angle)
            S += start_lift
        split_angle = end_angle
        start_lift += lift
    return S


def run_example():
    x, y = displacement(test)
    plt.plot(x, y, "-r")
    fp = discrete_derivative(x, y)
    fpp = discrete_derivative(x, fp)
    plt.plot(x, fp*25, "-b")
    plt.plot(x, fpp*300, "-g")
    plt.show()

    r_c, A = roller_translating_cam(6, 1, x, y, 0.5)
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
    ax.plot(A/360*2*π, r_c, '-r')
    ax.set_rmax(12)
    ax.set_rticks([2, 4, 6, 8, 10, 10])  # Less radial ticks
    ax.set_rlabel_position(-22.5)  # Move radial labels away from plotted line
    ax.grid(True)

    ax.set_title("cam profile", va='bottom')
    plt.show()


def getShapeOfCam(data, r_b):
    x, y = displacement(data)
    r_c, A = knife_edge_translating_cam(r_b, x, y, 0)
    x_array, y_array = polar2xy(r_c, A/360*2*π)
    # loop first point back to end
    x_array = np.insert(x_array, [len(x_array)], [x_array[0]])
    y_array = np.insert(y_array, [len(y_array)], [y_array[0]])
    curve = Part.BSplineCurve()
    segment = [FreeCAD.Base.Vector(x, y, 0) for x, y in zip(x_array, y_array)]
    curve.interpolate(segment)
    shape = Part.makeCompound([curve])  # Some have more than one segment
    return shape


class AxialCamObj:
    def __init__(self, obj):
        obj.addProperty("App::PropertyPythonObject", "Data")
        obj.addProperty("App::PropertyAngle", "ReferenceAngle")
        obj.addProperty("App::PropertyLength", "ReferenceDisplacement")
        obj.addProperty("App::PropertyLength", "BaseCircleRadius")
        obj.BaseCircleRadius = FreeCAD.Units.Quantity("6 mm")
        obj.Data = test
        obj.Shape = getShapeOfCam(obj.Data, float(
            obj.BaseCircleRadius.getValueAs('mm')))
        S = displacement_at(
            float(obj.ReferenceAngle.getValueAs('deg')), obj.Data)
        obj.ReferenceDisplacement = FreeCAD.Units.Quantity(str(S) + " mm")
        obj.Proxy = self

    def onChanged(self, obj, prop):
        if prop == "ReferenceAngle":
            S = displacement_at(
                float(obj.ReferenceAngle.getValueAs('deg')), obj.Data)
            obj.ReferenceDisplacement = FreeCAD.Units.Quantity(str(S) + " mm")
        if prop == "BaseCircleRadius" or prop == "Data":
            obj.Shape = getShapeOfCam(obj.Data, float(
                obj.BaseCircleRadius.getValueAs('mm')))
        pass

    def execute(self, obj):
        pass

class ViewProviderAxialCam:
    def __init__(self, vobj):
        vobj.Proxy = self

    def onChanged(self, vobj, prop):
        pass

    def getIcon(self):
        return os.path.join(ICONPATH, "camIcon.svg")


class addAxialCamCmd():
    def __init__(self):
        pass

    def GetResources(self):
        return {'Pixmap': os.path.join(ICONPATH,"camIcon.svg"),
                'MenuText': "Add Axial Cam",
                'ToolTip': "Add Axial Cam"}

    def Activated(self):
        doc = FreeCAD.ActiveDocument
        obj = doc.addObject("Part::Part2DObjectPython", "Cam")
        view = Gui.ActiveDocument.ActiveView
        activeBody = view.getActiveObject('pdbody')
        activeBody.addObject(obj)
        AxialCamObj(obj)
        ViewProviderAxialCam(obj.ViewObject)

    def IsActive(self):
        return True
