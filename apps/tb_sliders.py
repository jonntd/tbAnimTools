'''TB Animation Tools is a toolset for animators

*******************************************************************************
    License and Copyright
    Copyright 2020-Tom Bailey
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    send issues/ requests to brimblashman@gmail.com
    visit https://tbanimtools.blogspot.com/ for "stuff"


*******************************************************************************
'''

import pymel.core as pm
import pymel.core.datatypes as dt
import maya.cmds as cmds

import maya.OpenMayaUI as omUI
import maya.api.OpenMaya as om2
import maya.api.OpenMayaAnim as oma2
from maya.api import OpenMaya

fn_SMOOTH = 'Smooth'
fn_BLOAT = 'Bloat'
fn_BREAKDOWN = 'Tween'
fn_BREAKDOWNGROUP = 'TweenGrp'

qtVersion = pm.about(qtVersion=True)
margin = 2
from random import randint
from Abstract import *
import maya
import maya.OpenMayaUI as omui

maya.utils.loadStringResourcesForModule(__name__)
QTVERSION = int(qtVersion.split('.')[0])
if QTVERSION < 5:
    from PySide.QtGui import *
    from PySide.QtCore import *
    # from pysideuic import *
    from shiboken import wrapInstance
else:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    # from pyside2uic import *
    from shiboken2 import wrapInstance
import sys, os
import tb_functions as funcs

scriptLocation = os.path.dirname(os.path.realpath(__file__))
IconPath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Icons'))

baseIconFile = 'iceCream.png'
hoverIconFile = 'iceCreamInverse.png'
activeIconFile = 'iceCream.png'
inactiveIconFile = 'blank.png'
dotSmallIconFile = 'dotSmall.png'
barSmallIconFile = 'barSmall.png'

noTint = QColor(0, 0, 0)
hoverTint = QColor(0, 128, 0)
dragTint = QColor(0, 128, 0)

translateAttributes = ['tx', 'ty', 'tz']
rotateAttributes = ['rx', 'ry', 'rz']
scaleAttributes = ['sx', 'sy', 'sz']


class hotkeys(hotKeyAbstractFactory):
    def createHotkeyCommands(self):
        self.setCategory(self.helpStrings.category.get('sliders'))
        self.commandList = list()
        self.addCommand(self.tb_hkey(name='showControlTweener', annotation='',
                                     help=maya.stringTable['tbCommand.inbetweenSliderRelease'],
                                     category=self.category, command=['SlideTools.showXformInbetween()']))
        self.addCommand(self.tb_hkey(name='showKeyTweener', annotation='',
                                     help=maya.stringTable['tbCommand.inbetweenSliderRelease'],
                                     category=self.category, command=['SlideTools.showKeyInbetween()']))

        self.addCommand(self.tb_hkey(name='inbetweenSliderPress', annotation='',
                                     help=maya.stringTable['tbCommand.inbetweenSliderPress'],
                                     category=self.category, command=['SlideTools.inbetweenSlidePress()']))
        self.addCommand(self.tb_hkey(name='inbetweenSliderRelease', annotation='',
                                     help=maya.stringTable['tbCommand.inbetweenSliderRelease'],
                                     category=self.category, command=['SlideTools.inbetweenSlideRelease()']))

        return self.commandList

    def assignHotkeys(self):
        return


class tweenBase(object):
    ## Get the current UI Unit
    keyboardModifier = None
    labelText = 'base class'

    instance = None

    baseLabel = 'baseLabel'
    shiftLabel = 'shiftLabel'
    controlLabel = 'controlLabel'
    controlShiftLabel = 'controlShiftLabel'
    altLabel = 'altLabel'
    filterdAttributes = list()

    def __init__(self):
        self.keyState = pm.autoKeyframe(query=True, state=True)
        self.affectedObjects = list()
        self.alpha = 0

    def apply(self):
        pm.autoKeyframe(state=self.keyState)
        self.updateAlpha(self.alpha, disableAutoKey=False)

    @staticmethod
    def iterSelection():
        """
        generator style iterator over current Maya active selection
        :return: [MObject) an MObject for each item in the selection
        """
        sel = om2.MGlobal.getActiveSelectionList()
        for i in range(sel.length()):
            yield sel.getDependNode(i)

    def startDrag(self):
        cmds.warning('tween class start drag')

    def updateDrag(self, value):
        cmds.warning('tween class update drag', value)

    def endDrag(self, value):
        cmds.warning('tween class end drag', value)

    def setAffectedObjects(self):
        """
        set the affected objects/keys
        :return:
        """

    def cacheValues(self):
        """
        Cache the initial values/plugs to keep the speed high
        :return:
        """
        self.get_modifier()

    def get_modifier(self):
        self.keyboardModifier = {0: None,
                                 1: 'shift',
                                 4: 'ctrl',
                                 5: 'ctrlShift',
                                 8: 'alt',
                                 9: 'alt',  # actually 'shiftAlt',
                                 12: 'alt',  # actually 'ctrlAlt',
                                 13: 'alt',  # actually  'ctrlShiftAlt'
                                 }[cmds.getModifiers()]

    def filterAffectedChannels(self):
        '''
        0: None,
                                 1: 'shift',
                                 4: 'ctrl',
                                 5: 'ctrlShift',
                                 8: 'alt',
                                 9: 'alt',  # actually 'shiftAlt',
                                 12: 'alt',  # actually 'ctrlAlt',
                                 13: 'alt',  #
        :return:
        '''
        self.get_modifier()
        if self.keyboardModifier == 'alt':
            self.filterdAttributes = funcs.functions().getChannels()
        elif self.keyboardModifier == 'shift':
            self.filterdAttributes = translateAttributes
        elif self.keyboardModifier == 'ctrl':
            self.filterdAttributes = rotateAttributes
        elif self.keyboardModifier == 'ctrlShift':
            self.filterdAttributes = rotateAttributes + translateAttributes
        else:
            self.filterdAttributes = list()

    def updateAlpha(self, alpha, disableAutoKey=True):
        """
        perform the update calculation here that affects the objects/keys
        :param alpha:
        :param disableAutoKey:
        :return:
        """
        pass
        # print self.keyboardModifier

    def om_plug_at_time(self, dep_node, plug, mdg):
        '''
        Getting the plug from openMaya.
        Then create a time mdgContext and evaluate it.
        This is the fastest with layer compatability... however i suspect there to be issues when doing complex simulations.

        :param dep_node: object string name i.e. "pSphere1"
        :param attr: the attribute to check i.e. "tx"
        :return: a list of values per frame.
        '''

        objMfn = OpenMaya.MFnDependencyNode(dep_node)
        ## Get the plug of the node. (networkedplug = False, as it no longer profides a speed improvement)
        value = objMfn.findPlug(plug, False).asDouble(mdg)

        return value

    def om_plug_worldMatrix_at_time(self, matrix, dep_node, mdg):
        '''
        Getting the plug from openMaya.
        Then create a time mdgContext and evaluate it.
        This is the fastest with layer compatability... however i suspect there to be issues when doing complex simulations.

        :param dep_node: object string name i.e. "pSphere1"
        :param attr: the attribute to check i.e. "tx"
        :return: a list of values per frame.
        '''

        objMfn = OpenMaya.MFnDependencyNode(dep_node)
        ## Get the plug of the node. (networkedplug = False, as it no longer profides a speed improvement)
        plug = objMfn.findPlug(matrix, False).elementByLogicalIndex(0)

        value = om2.MFnMatrixData(plug.asMObject(mdg)).matrix()

        return value


class WorldSpaceTween(tweenBase):
    labelText = 'worldSpaceTween'
    ignoredAttributeNames = ['translateX',
                             'translateY',
                             'translateZ',
                             'rotateX',
                             'rotateY',
                             'rotateZ',
                             'scaleX',
                             'scaleY',
                             'scaleZ']
    ignoredAttributeTypes = ['bool', 'enum', 'message']

    baseLabel = 'All attributes'
    shiftLabel = 'Translate Only'
    controlLabel = 'Rotate Only'
    controlShiftLabel = 'Translate And Rotate Only'
    altLabel = 'ChannelBox Only'

    def __init__(self):
        super(WorldSpaceTween, self).__init__()
        self.keyState = pm.autoKeyframe(query=True, state=True)
        self.affectedObjects = list()
        self.alpha = 0
        self.currentTime = float()
        self.startkeyTimes = dict()
        self.startTransforms = dict()
        self.endKeyTimes = dict()
        self.endTransforms = dict()

        # store mfp dependency nodes
        self.mfnDepNodes = dict()
        self.attrPlugs = dict()
        # store matrix values here
        self.currentMTransformationMatrix = dict()
        self.currentParentInverseMTransformationMatrix = dict()
        self.prevMTransformationMatrix = dict()
        self.nextMTransformationMatrix = dict()

        # store the user attributes here
        self.currentAttrData = dict()
        self.prevAttrData = dict()
        self.nextAttrData = dict()

    def apply(self):
        super(WorldSpaceTween, self).apply()

    def startDrag(self, value):
        self.keyState = pm.autoKeyframe(query=True, state=True)
        pm.autoKeyframe(state=False)
        sel = cmds.ls(sl=True, type='transform')
        if not sel:
            self.affectedObjects = list()
            return
        self.affectedObjects = sel
        self.cacheValues()
        self.filterAffectedChannels()
        self.updateDrag(value)

    def updateDrag(self, value):
        self.updateAlpha(value * 0.01, disableAutoKey=True)

    def endDrag(self, value):
        # print ('WorldSpaceTween class end drag', value)
        pm.autoKeyframe(state=self.keyState)
        if not self.affectedObjects:
            return
        cmds.setKeyframe(self.affectedObjects)

    @staticmethod
    def iterSelection():
        """
        generator style iterator over current Maya active selection
        :return: [MObject) an MObject for each item in the selection
        """
        # TODO - bug here where the active seleciton list is curves, although the graph editor is closed
        sel = om2.MGlobal.getActiveSelectionList()
        for i in range(sel.length()):
            yield sel.getDependNode(i)

    def setAffectedObjects(self):
        sel = cmds.ls(sl=True)
        keys = cmds.keyframe(query=True, selected=True)

        if sel:
            self.affectedObjects = sel

    def cacheValues(self):
        super(WorldSpaceTween, self).cacheValues()
        cmds.warning('cacheValues', self.keyboardModifier)
        # print 'affectedObjects', self.affectedObjects
        # just get one objects next and previous transforms
        thisTime = cmds.currentTime(query=True)

        for obj in self.affectedObjects:
            self.startkeyTimes[obj] = cmds.findKeyframe(obj, time=(thisTime, thisTime), which="previous")
            self.endKeyTimes[obj] = cmds.findKeyframe(obj, time=(thisTime, thisTime), which="next")
            allAttrs = cmds.listAttr(obj, keyable=True, scalar=True, settable=True, inUse=True)
            validAttrs = list()
            for attr in allAttrs:
                if attr in self.ignoredAttributeNames:
                    continue
                attrType = cmds.getAttr(obj + '.' + attr, type=True)
                if attrType in self.ignoredAttributeTypes:
                    continue
                if cmds.getAttr(obj + '.' + attr, lock=True):
                    continue
                if not cmds.getAttr(obj + '.' + attr, keyable=True):
                    continue
                validAttrs.append(cmds.attributeName(obj + '.' + attr, s=True))

            if len(validAttrs):
                cmds.warning('validAttrs', validAttrs)
                self.currentAttrData[obj] = attrData(validAttrs)
                self.prevAttrData[obj] = attrData(validAttrs)
                self.nextAttrData[obj] = attrData(validAttrs)
                self.attrPlugs[obj] = dict()
        # print 'start times', self.startkeyTimes
        # print 'end times', self.endKeyTimes
        for obj in self.affectedObjects:
            eachMob = getMObject(obj)
            obj_dag_path = om2.MDagPath.getAPathTo(eachMob)
            objMfn = OpenMaya.MFnDependencyNode(eachMob)
            obj = str(obj_dag_path)
            self.mfnDepNodes[str(obj_dag_path)] = objMfn
            # print objMfn
            currentMDG = OpenMaya.MDGContext(OpenMaya.MTime(thisTime, om2.MTime.uiUnit()))
            currentTransform = self.om_plug_worldMatrix_at_time('worldMatrix', eachMob, currentMDG)
            self.currentMTransformationMatrix[str(obj_dag_path)] = om2.MTransformationMatrix(currentTransform)
            currentParentInverseTransform = self.om_plug_worldMatrix_at_time('parentInverseMatrix', eachMob, currentMDG)
            self.currentParentInverseMTransformationMatrix[str(obj_dag_path)] = om2.MTransformationMatrix(
                currentParentInverseTransform)

            prevMDG = OpenMaya.MDGContext(OpenMaya.MTime(self.startkeyTimes[obj], om2.MTime.uiUnit()))
            previousTransform = self.om_plug_worldMatrix_at_time('worldMatrix', eachMob, prevMDG)
            self.prevMTransformationMatrix[str(obj_dag_path)] = om2.MTransformationMatrix(previousTransform)

            nextMDG = OpenMaya.MDGContext(OpenMaya.MTime(self.endKeyTimes[obj], om2.MTime.uiUnit()))
            nextTransform = self.om_plug_worldMatrix_at_time('worldMatrix', eachMob, nextMDG)
            self.nextMTransformationMatrix[str(obj_dag_path)] = om2.MTransformationMatrix(nextTransform)

            if not self.currentAttrData.get(obj):
                continue
            for attribute, value in self.currentAttrData[obj].attributes.items():
                self.currentAttrData[obj].attributes[attribute] = self.om_plug_at_time(eachMob, attribute, currentMDG)
                self.attrPlugs[obj][attribute] = objMfn.findPlug(attribute, False)

            for attribute, value in self.prevAttrData[obj].attributes.items():
                currentMDG = OpenMaya.MDGContext(OpenMaya.MTime(self.startkeyTimes[obj], om2.MTime.uiUnit()))
                self.prevAttrData[obj].attributes[attribute] = self.om_plug_at_time(eachMob, attribute, currentMDG)

            for attribute, value in self.prevAttrData[obj].attributes.items():
                currentMDG = OpenMaya.MDGContext(OpenMaya.MTime(self.endKeyTimes[obj], om2.MTime.uiUnit()))
                self.nextAttrData[obj].attributes[attribute] = self.om_plug_at_time(eachMob, attribute,
                                                                                    currentMDG)

    def updateAlpha(self, alpha, disableAutoKey=True):
        super(WorldSpaceTween, self).updateAlpha(alpha, disableAutoKey=disableAutoKey)
        # pm.autoKeyframe(state=not disableAutoKey)
        self.alpha = alpha

        for obj in self.affectedObjects:
            translation = self.prevMTransformationMatrix[obj].translation(om2.MSpace.kWorld)
            translation = self.nextMTransformationMatrix[obj].translation(om2.MSpace.kWorld)
            rotation = self.prevMTransformationMatrix[obj].rotation(asQuaternion=False)
            rotation = self.nextMTransformationMatrix[obj].rotation(asQuaternion=False)
            outAlpha = 0
            if self.alpha >= 0:
                # lerp to next
                currentTranslation = self.currentMTransformationMatrix[obj].translation(om2.MSpace.kWorld)
                targetTranslation = self.nextMTransformationMatrix[obj].translation(om2.MSpace.kWorld)

                currentRotation = self.currentMTransformationMatrix[obj].rotation(asQuaternion=True)
                targetRotation = self.nextMTransformationMatrix[obj].rotation(asQuaternion=True)

                currentScale = self.currentMTransformationMatrix[obj].scale(om2.MSpace.kWorld)
                targetScale = self.nextMTransformationMatrix[obj].scale(om2.MSpace.kWorld)
                outAlpha = alpha
            else:
                # lerp to prev
                currentTranslation = self.currentMTransformationMatrix[obj].translation(om2.MSpace.kWorld)
                targetTranslation = self.prevMTransformationMatrix[obj].translation(om2.MSpace.kWorld)

                currentRotation = self.currentMTransformationMatrix[obj].rotation(asQuaternion=True)
                targetRotation = self.prevMTransformationMatrix[obj].rotation(asQuaternion=True)

                currentScale = self.currentMTransformationMatrix[obj].scale(om2.MSpace.kWorld)
                targetScale = self.prevMTransformationMatrix[obj].scale(om2.MSpace.kWorld)

                outAlpha = alpha * -1
            lerpedWorldTranslation = lerpMVector(currentTranslation, targetTranslation, outAlpha)
            lerpedWorldRotation = om2.MQuaternion.slerp(currentRotation, targetRotation, outAlpha)
            lerpedWorlScale = lerpMVector(om2.MVector(currentScale), om2.MVector(targetScale), outAlpha)

            lerpedWorldMatrix = om2.MTransformationMatrix()
            lerpedWorldMatrix.setTranslation(lerpedWorldTranslation, om2.MSpace.kWorld)
            lerpedWorldMatrix.setRotation(lerpedWorldRotation)
            lerpedWorldMatrix.setScale(lerpedWorlScale, om2.MSpace.kWorld)
            resultMatrix = lerpedWorldMatrix.asMatrix() * self.currentParentInverseMTransformationMatrix[obj].asMatrix()
            transformMatrixObj = om2.MTransformationMatrix(resultMatrix)
            resultTranslate = transformMatrixObj.translation(om2.MSpace.kWorld)
            resultRotate = transformMatrixObj.rotation(asQuaternion=False)
            resultScale = transformMatrixObj.scale(om2.MSpace.kWorld)
            rotateOrder = self.mfnDepNodes[obj].findPlug('rotateOrder', False).asInt()

            resultRotate.reorderIt(rotateOrder)
            translateNames = ['tx', 'ty', 'tz']  # , 'rx','ry', 'rz', 'sx', 'sy', 'sz', ]
            if self.filterdAttributes:
                translateNames = [x for x in translateNames if x in self.filterdAttributes]

            translatePlugs = [self.mfnDepNodes[obj].findPlug(eachName, False) for eachName in translateNames]
            rotateNames = ['rx', 'ry', 'rz']
            if self.filterdAttributes:
                rotateNames = [x for x in rotateNames if x in self.filterdAttributes]

            rotatePlugs = [self.mfnDepNodes[obj].findPlug(eachName, False) for eachName in rotateNames]

            scaleNames = ['sx', 'sy', 'sz']
            if self.filterdAttributes:
                scaleNames = [x for x in scaleNames if x in self.filterdAttributes]

            scalePlugs = [self.mfnDepNodes[obj].findPlug(eachName, False) for eachName in scaleNames]

            for index, plug in enumerate(translatePlugs):
                if not plug.isLocked:
                    plug.setFloat(resultTranslate[index])
            for index, plug in enumerate(rotatePlugs):
                if not plug.isLocked:
                    plug.setFloat(resultRotate[index])
            for index, plug in enumerate(scalePlugs):
                if not plug.isLocked:
                    plug.setFloat(resultScale[index])

            for obj in self.affectedObjects:
                if obj not in self.currentAttrData.keys():
                    continue
                for attribute in self.currentAttrData[obj].attributes.keys():
                    if self.filterdAttributes:
                        if attribute not in self.filterdAttributes:
                            continue
                    if attribute in translateAttributes:
                        continue
                    if attribute in rotateAttributes:
                        continue
                    if attribute in scaleAttributes:
                        continue
                    outAlpha = 0
                    currentValue = self.currentAttrData[obj].attributes[attribute]
                    if self.alpha >= 0:
                        # lerp to next
                        targetValue = self.nextAttrData[obj].attributes[attribute]
                        outAlpha = alpha
                    else:
                        # lerp to prev
                        targetValue = self.prevAttrData[obj].attributes[attribute]
                        outAlpha = alpha * -1
                    lerpedResult = lerpFloat(targetValue, currentValue, outAlpha)

                    plug = self.attrPlugs[obj][attribute]
                    if not plug.isLocked:
                        plug.setFloat(lerpedResult)


class LocalSpaceTween(tweenBase):
    labelText = 'localSpaceTween'
    ignoredAttributeNames = ['translateX',
                             'translateY',
                             'translateZ',
                             'rotateX',
                             'rotateY',
                             'rotateZ',
                             'scaleX',
                             'scaleY',
                             'scaleZ']
    ignoredAttributeTypes = ['bool', 'enum', 'message']

    baseLabel = 'All attributes'
    shiftLabel = 'Translate Only'
    controlLabel = 'Rotate Only'
    controlShiftLabel = 'Translate And Rotate Only'
    altLabel = 'ChannelBox Only'

    def __init__(self):
        super(LocalSpaceTween, self).__init__()
        self.keyState = pm.autoKeyframe(query=True, state=True)
        self.affectedObjects = list()
        self.alpha = 0
        self.currentTime = float()
        self.startkeyTimes = dict()
        self.startTransforms = dict()
        self.endKeyTimes = dict()
        self.endTransforms = dict()

        # store mfp dependency nodes
        self.mfnDepNodes = dict()
        self.attrPlugs = dict()
        # store matrix values here
        self.currentMTransformationMatrix = dict()
        self.currentParentInverseMTransformationMatrix = dict()
        self.prevMTransformationMatrix = dict()
        self.nextMTransformationMatrix = dict()

        # store the user attributes here
        self.currentAttrData = dict()
        self.prevAttrData = dict()
        self.nextAttrData = dict()

    def filterAffectedChannels(self):
        '''
        0: None,
                                 1: 'shift',
                                 4: 'ctrl',
                                 5: 'ctrlShift',
                                 8: 'alt',
                                 9: 'alt',  # actually 'shiftAlt',
                                 12: 'alt',  # actually 'ctrlAlt',
                                 13: 'alt',  #
        :return:
        '''
        self.get_modifier()
        if self.keyboardModifier == 'alt':
            self.filterdAttributes = funcs.functions().getChannels()
        elif self.keyboardModifier == 'shift':
            self.filterdAttributes = translateAttributes
        elif self.keyboardModifier == 'ctrl':
            self.filterdAttributes = rotateAttributes
        elif self.keyboardModifier == 'ctrlShift':
            self.filterdAttributes = rotateAttributes + translateAttributes
        else:
            self.filterdAttributes = list()

    def apply(self):
        super(LocalSpaceTween, self).apply()

    def startDrag(self, value):
        self.keyState = pm.autoKeyframe(query=True, state=True)
        pm.autoKeyframe(state=False)
        sel = cmds.ls(sl=True, type='transform')
        if not sel:
            self.affectedObjects = list()
            return
        self.affectedObjects = sel
        self.filterAffectedChannels()
        self.cacheValues()
        self.updateDrag(value)

    def updateDrag(self, value):
        self.updateAlpha(value * 0.01, disableAutoKey=True)

    def endDrag(self, value):
        # print ('WorldSpaceTween class end drag', value)
        pm.autoKeyframe(state=self.keyState)
        if not self.affectedObjects:
            return
        cmds.setKeyframe(self.affectedObjects)

    @staticmethod
    def iterSelection():
        """
        generator style iterator over current Maya active selection
        :return: [MObject) an MObject for each item in the selection
        """
        # TODO - bug here where the active seleciton list is curves, although the graph editor is closed
        sel = om2.MGlobal.getActiveSelectionList()
        for i in range(sel.length()):
            yield sel.getDependNode(i)

    def setAffectedObjects(self):
        sel = cmds.ls(sl=True)
        keys = cmds.keyframe(query=True, selected=True)

        if sel:
            self.affectedObjects = sel

    def cacheValues(self):
        super(LocalSpaceTween, self).cacheValues()
        self.mfnDepNodes = dict()
        self.attrPlugs = dict()
        self.currentAttrData = dict()
        self.prevAttrData = dict()
        self.nextAttrData = dict()

        # print 'affectedObjects', self.affectedObjects
        # just get one objects next and previous transforms
        thisTime = cmds.currentTime(query=True)

        for obj in self.affectedObjects:
            # TODO - make this look for individual key times?
            self.startkeyTimes[obj] = cmds.findKeyframe(obj, time=(thisTime, thisTime), which="previous")
            self.endKeyTimes[obj] = cmds.findKeyframe(obj, time=(thisTime, thisTime), which="next")
            allAttrs = cmds.listAttr(obj, keyable=True, scalar=True, settable=True, inUse=True)
            validAttrs = list()
            for attr in allAttrs:
                '''
                if attr in self.ignoredAttributeNames:
                    continue
                '''
                attrType = cmds.getAttr(obj + '.' + attr, type=True)
                if attrType in self.ignoredAttributeTypes:
                    continue
                if cmds.getAttr(obj + '.' + attr, lock=True):
                    continue
                if not cmds.getAttr(obj + '.' + attr, keyable=True):
                    continue
                validAttrs.append(cmds.attributeName(obj + '.' + attr, s=True))

            if len(validAttrs):
                self.currentAttrData[obj] = attrData(validAttrs)
                self.prevAttrData[obj] = attrData(validAttrs)
                self.nextAttrData[obj] = attrData(validAttrs)
                self.attrPlugs[obj] = dict()

        # print 'start times', self.startkeyTimes
        # print 'end times', self.endKeyTimes
        for obj in self.affectedObjects:
            MObj = getMObject(obj)
            # obj_dag_path = om2.MDagPath.getAPathTo(eachMob)
            # print ('obj_dag_path', str(obj_dag_path))
            # obj = str(obj_dag_path)
            objMfn = OpenMaya.MFnDependencyNode(MObj)

            self.mfnDepNodes[obj] = objMfn

            # print objMfn
            currentMDG = OpenMaya.MDGContext(OpenMaya.MTime(thisTime, om2.MTime.uiUnit()))
            # get all attribute values at prev, current and next

            for attribute, value in self.currentAttrData[obj].attributes.items():
                self.currentAttrData[obj].attributes[attribute] = self.om_plug_at_time(MObj, attribute, currentMDG)
                self.attrPlugs[obj][attribute] = objMfn.findPlug(attribute, False)

            for attribute, value in self.prevAttrData[obj].attributes.items():
                currentMDG = OpenMaya.MDGContext(OpenMaya.MTime(self.startkeyTimes[obj], om2.MTime.uiUnit()))
                self.prevAttrData[obj].attributes[attribute] = self.om_plug_at_time(MObj, attribute, currentMDG)

            for attribute, value in self.prevAttrData[obj].attributes.items():
                currentMDG = OpenMaya.MDGContext(OpenMaya.MTime(self.endKeyTimes[obj], om2.MTime.uiUnit()))
                self.nextAttrData[obj].attributes[attribute] = self.om_plug_at_time(MObj, attribute,
                                                                                    currentMDG)

    def updateAlpha(self, alpha, disableAutoKey=True):
        super(LocalSpaceTween, self).updateAlpha(alpha, disableAutoKey=disableAutoKey)
        # pm.autoKeyframe(state=not disableAutoKey)
        self.alpha = alpha

        for obj in self.affectedObjects:
            for attribute in self.currentAttrData[obj].attributes.keys():
                if self.filterdAttributes:
                    if attribute not in self.filterdAttributes:
                        continue
                outAlpha = 0
                currentValue = self.currentAttrData[obj].attributes[attribute]
                if self.alpha >= 0:
                    # lerp to next
                    targetValue = self.nextAttrData[obj].attributes[attribute]
                    outAlpha = alpha
                else:
                    # lerp to prev
                    targetValue = self.prevAttrData[obj].attributes[attribute]
                    outAlpha = alpha * -1
                lerpedResult = lerpFloat(targetValue, currentValue, outAlpha)

                plug = self.attrPlugs[obj][attribute]
                if not plug.isLocked:
                    plug.setFloat(lerpedResult)


class keyframeTween(tweenBase):
    labelText = 'keyframeTween'

    def __init__(self):
        super(keyframeTween, self).__init__()
        self.keyState = pm.autoKeyframe(query=True, state=True)
        self.affectedObjects = list()
        self.alpha = 0
        self.currentTime = float()
        self.selectedKeyTimes = dict()
        self.selectedKeyIndexes = dict()
        self.selectedKeyValues = dict()
        self.curvePreviousValues = dict()
        self.curveNextValues = dict()

        import tb_functions as funcs
        reload(funcs)
        self.funcs = funcs.functions()

    def apply(self):
        super(keyframeTween, self).apply()
        self.cacheValues()

    def setAffectedObjects(self):
        self.affectedObjects = self.funcs.get_selected_curves()

    def cacheValues(self):
        # just get one objects next and previous transforms
        thisTime = cmds.currentTime(query=True)
        if not self.affectedObjects:
            return
        for curve in self.affectedObjects:
            self.selectedKeyTimes[curve] = self.funcs.get_key_times(curve)
            self.selectedKeyIndexes[curve] = self.funcs.get_selected_key_indexes(curve)
            self.selectedKeyValues[curve] = self.funcs.get_key_values(curve)
            curvePreviousValues = list()
            curveNextValues = list()
            for index, indexVal in enumerate(self.selectedKeyIndexes[curve]):
                previousValue = self.funcs.get_prev_key_values_from_index(curve, indexVal)
                nextValue = self.funcs.get_next_key_values_from_index(curve, indexVal)
                curvePreviousValues.append(previousValue[0])
                curveNextValues.append(nextValue[0])
            self.curvePreviousValues[curve] = curvePreviousValues
            self.curveNextValues[curve] = curveNextValues

    def updateAlpha(self, alpha, disableAutoKey=True):
        super(keyframeTween, self).updateAlpha(alpha, disableAutoKey=disableAutoKey)
        pm.autoKeyframe(state=not disableAutoKey)
        self.alpha = alpha
        if self.keyboardModifier == 'shift':
            # print 'just shift'
            for curve in self.affectedObjects:
                for index, indexVal in enumerate(self.selectedKeyIndexes[curve]):
                    if self.alpha >= 0:
                        # lerp to next
                        targetValue = self.curveNextValues[curve][-1]
                        outAlpha = alpha
                    else:
                        # lerp to prev
                        targetValue = self.curvePreviousValues[curve][0]
                        outAlpha = alpha * -1

                    lerpedValue = lerpFloat(targetValue, self.selectedKeyValues[curve][index], outAlpha)
                    cmds.keyframe(curve, edit=True, valueChange=lerpedValue, index=((indexVal),))
            return
        if self.keyboardModifier == 'ctrl':
            # print 'just control'
            for curve in self.affectedObjects:
                for index, indexVal in enumerate(self.selectedKeyIndexes[curve]):
                    if self.alpha >= 0:
                        # lerp to next
                        targetValueA = self.curveNextValues[curve][index]
                        targetValueB = self.curvePreviousValues[curve][index]
                        targetValue = (targetValueA + targetValueB) / 2.0
                        outAlpha = alpha
                    else:
                        # lerp to prev
                        targetValue = self.curvePreviousValues[curve][0]
                        outAlpha = alpha * -1

                    lerpedValue = lerpFloat(targetValue, self.selectedKeyValues[curve][index], outAlpha)
                    cmds.keyframe(curve, edit=True, valueChange=lerpedValue, index=((indexVal),))
            return
        for curve in self.affectedObjects:
            if self.alpha >= 0:
                # lerp to next
                targetValue = self.curveNextValues[curve][-1]
                baseValue = self.selectedKeyValues[curve][-1]
                outAlpha = alpha
            else:
                # lerp to prev
                targetValue = self.curvePreviousValues[curve][0]
                baseValue = self.selectedKeyValues[curve][0]
                outAlpha = alpha * -1
            lerpedValue = lerpFloat(targetValue - baseValue, 0, outAlpha)
            # print 'outAlpha', outAlpha, 'lerpedValue', lerpedValue
            for index, indexVal in enumerate(self.selectedKeyIndexes[curve]):
                # print self.selectedKeyValues[curve][index]
                outValue = self.selectedKeyValues[curve][index] + lerpedValue

                cmds.keyframe(curve, edit=True, valueChange=outValue, index=((indexVal),))


class SlideTools(toolAbstractFactory):
    """
    Use this as a base for toolAbstractFactory classes
    """
    # __metaclass__ = abc.ABCMeta
    __instance = None
    toolName = 'SlideTools'
    hotkeyClass = hotkeys()
    funcs = functions()
    app = None
    dependentPlugins = ["tbKeyTween.py"]
    slideUI = None

    keyPressHandler = None
    selectionChangedCallback = -1

    xformTweenDict = {'World': WorldSpaceTween,
                      'Local': LocalSpaceTween,
                      }
    xformTweenClasses = {'World': None,
                         'Local': None,
                         }
    # stop here, maybe put anim cache in each mode?
    keyTweenDict = {'World': WorldSpaceTween,
                    'Local': LocalSpaceTween,
                    }
    keyTweenMethods = {}
    xformWidget = None
    keyWidget = None
    graphEditKeyWidget = None

    animCurveChange = None
    keyframeData = None
    keyframeRefData = None  # used on multiple iterations of smooths etc
    selectedCurveDict = None

    def __new__(cls):
        if SlideTools.__instance is None:
            SlideTools.__instance = object.__new__(cls)

        SlideTools.__instance.val = cls.toolName
        SlideTools.__instance.app = QApplication.instance()
        SlideTools.__instance.keyTweenMethods = {
            fn_BREAKDOWN: SlideTools.__instance.tweenPreviousCurrentNext,
            fn_BREAKDOWNGROUP: SlideTools.__instance.tweenPreviousNextGroup,
            fn_BLOAT: SlideTools.__instance.tweenBloat,
            fn_SMOOTH: SlideTools.__instance.tweenSmoothNeighbours
        }
        # slideTools.__instance.xformWidget = XformSliderWidget()

        return SlideTools.__instance

    def __init__(self):
        self.hotkeyClass = hotkeys()
        self.funcs = functions()

    """
    Declare an interface for operations that create abstract product
    objects.
    """

    def optionUI(self):
        super(SlideTools, self).optionUI()
        return None

    def showUI(self):
        return cmds.warning(self, 'optionUI', ' function not implemented')

    def drawMenuBar(self, parentMenu):
        return None

    def pickInbetweenClass(self):
        # TODO - don't pick the slider class like this, pick it in init for UI
        selectedKeys = cmds.keyframe(query=True, selected=True)
        selectedObjects = cmds.ls(sl=True, type='transform')
        geState = getGraphEditorState()
        if not geState:
            return WorldSpaceTween()
        else:
            if selectedKeys:
                return keyframeTween()
            elif selectedObjects:
                return WorldSpaceTween()
        return tweenBase()

    def showXformInbetween(self):
        # check tween classes
        for key, value in self.xformTweenDict.items():
            if not self.xformTweenClasses[key]:
                self.xformTweenClasses[key] = value()
            if not self.xformTweenClasses[key].instance:
                self.xformTweenClasses[key].instance = value()

        if not self.xformWidget:
            self.xformWidget = XformSliderWidget()
            self.xformWidget.sliderBeginSignal.connect(self.xformSliderBeginSignal)
            self.xformWidget.sliderUpdateSignal.connect(self.xformSliderUpdateSignal)
            self.xformWidget.sliderEndedSignal.connect(self.xformSliderEndSignal)
            self.xformWidget.modeChangedSignal.connect(self.xformSliderModeChangeSignal)

        # move to mouse if unlocked
        if not self.xformWidget.lockState:
            self.xformWidget.moveToCursor()
        self.xformWidget.show()
        self.xformWidget.raise_()

        self.keyPressHandler = keypressHandler(None, self.xformWidget)
        self.app.installEventFilter(self.keyPressHandler)

    def xformSliderBeginSignal(self, key, value):
        self.xformTweenClasses[key].startDrag(value)

    def xformSliderUpdateSignal(self, key, value):
        self.xformTweenClasses[key].updateDrag(value)

    def xformSliderEndSignal(self, key, value):
        self.xformTweenClasses[key].endDrag(value)

    def xformSliderModeChangeSignal(self, key):
        self.xformWidget.baseLabel = self.xformTweenClasses[key].baseLabel
        self.xformWidget.shiftLabel = self.xformTweenClasses[key].shiftLabel
        self.xformWidget.controlLabel = self.xformTweenClasses[key].controlLabel
        self.xformWidget.controlShiftLabel = self.xformTweenClasses[key].controlShiftLabel
        self.xformWidget.altLabel = self.xformTweenClasses[key].altLabel

    # graphed key tween
    def showGraphEdKeyInbetween(self, graphEditor):
        # check tween classes
        '''

        :return:
        '''
        '''
        for key, value in self.keyTweenDict.items():
            if not self.keyTweenMethods[key]:
                self.keyTweenMethods[key] = value()
            if not self.keyTweenMethods[key].instance:
                self.keyTweenMethods[key].instance = value()
        '''
        if not hasattr(graphEditor, 'hasSlider'):
            setattr(graphEditor, 'hasSlider', False)
        if getattr(graphEditor, 'hasSlider'):
            return

        graphEditKeyWidget = GraphEdKeySliderWidget()
        graphEditKeyWidget.sliderBeginSignal.connect(self.keySliderBeginSignal)
        graphEditKeyWidget.sliderUpdateSignal.connect(self.keySliderUpdateSignal)
        graphEditKeyWidget.sliderEndedSignal.connect(self.keySliderEndSignal)
        graphEditKeyWidget.sliderCancelSignal.connect(self.keySliderCancelSignal)
        graphEditKeyWidget.modeChangedSignal.connect(self.graphEditKeySliderModeChangeSignal)
        uiButton = "curvesPostInfinityCycleOffsetButton"
        PControl = wrapInstance(int(omui.MQtUtil.findControl(uiButton)), QPushButton)

        UIParent = PControl.parent()
        UIParent.objectName()

        phLayout = wrapInstance(int(omui.MQtUtil.findControl(UIParent.objectName())), QWidget)

        graphEditKeyWidget.setParent(phLayout)
        graphEditKeyWidget.move(PControl.pos().x() + PControl.width() + 8, 2)

        graphEditKeyWidget.show()
        graphEditKeyWidget.raise_()


    def graphEditKeySliderModeChangeSignal(self, key):
        return
        self.graphEditKeyWidget.baseLabel = self.keyTweenMethods[key].baseLabel
        self.graphEditKeyWidget.shiftLabel = self.keyTweenMethods[key].shiftLabel
        self.graphEditKeyWidget.controlLabel = self.keyTweenMethods[key].controlLabel
        self.graphEditKeyWidget.controlShiftLabel = self.keyTweenMethods[key].controlShiftLabel
        self.graphEditKeyWidget.altLabel = self.keyTweenMethods[key].altLabel

    # key tween
    def showKeyInbetween(self):
        # check tween classes
        '''

        :return:
        '''
        '''
        for key, value in self.keyTweenDict.items():
            if not self.keyTweenMethods[key]:
                self.keyTweenMethods[key] = value()
            if not self.keyTweenMethods[key].instance:
                self.keyTweenMethods[key].instance = value()
        '''
        if not self.keyWidget:
            #print ('new instance')
            self.keyWidget = KeySliderWidget()
            self.keyWidget.sliderBeginSignal.connect(self.keySliderBeginSignal)
            self.keyWidget.sliderUpdateSignal.connect(self.keySliderUpdateSignal)
            self.keyWidget.sliderEndedSignal.connect(self.keySliderEndSignal)
            self.keyWidget.sliderCancelSignal.connect(self.keySliderCancelSignal)
            self.keyWidget.modeChangedSignal.connect(self.keySliderModeChangeSignal)

        # move to mouse if unlocked
        if not self.keyWidget.lockState:
            self.keyWidget.moveToCursor()
        self.keyWidget.show()
        self.keyWidget.raise_()

        self.keyKeyPressHandler = keypressHandler(None, self.keyWidget)
        self.app.installEventFilter(self.keyKeyPressHandler)

    def keySliderBeginSignal(self, key, value):
        cmds.undoInfo(openChunk=True, chunkName="tbInbetween")
        cmds.tbKeyTween(alpha=value, blendMode=str(key), clearCache=True)
        # self.keyTweenClasses[key].startDrag(value)

    def keySliderUpdateSignal(self, key, value):
        cmds.undoInfo(stateWithoutFlush=False)
        cmds.tbKeyTween(alpha=value, blendMode=str(key), clearCache=False)
        cmds.undoInfo(stateWithoutFlush=True)

    def keySliderEndSignal(self, key, value):
        cmds.tbKeyTween(alpha=value, blendMode=str(key), clearCache=False)
        cmds.undoInfo(closeChunk=True)

    def keySliderCancelSignal(self):
        # cmds.tbKeyTween(alpha=value, blendMode=str(key), clearCache=False)
        cmds.undoInfo(closeChunk=True)
        cmds.undo()

    def keySliderModeChangeSignal(self, key):
        return
        self.keyWidget.baseLabel = self.keyTweenMethods[key].baseLabel
        self.keyWidget.shiftLabel = self.keyTweenMethods[key].shiftLabel
        self.keyWidget.controlLabel = self.keyTweenMethods[key].controlLabel
        self.keyWidget.controlShiftLabel = self.keyTweenMethods[key].controlShiftLabel
        self.keyWidget.altLabel = self.keyTweenMethods[key].altLabel

    def inbetweenSlidePress(self):
        try:
            self.slideUI.close()
            self.slideUI.deleteLater()
            self.app.removeEventFilter(self.keyPressHandler)
        except:
            self.app.removeEventFilter(self.keyPressHandler)

        self.tweenClass = self.pickInbetweenClass()

        self.slideUI = sliderWidget(self.funcs.getWidgetAtCursor(), tweemClass=self.tweenClass, funcs=self.funcs)
        self.slideUI.showUI()
        try:
            cmds.scriptJob(kill=self.selectionChangedCallback)
        except:
            pass
        self.selectionChangedCallback = self.slideUI.createSelectionChangedScriptJob()

        self.keyPressHandler = keypressHandler(self.tweenClass, self.slideUI)
        self.app.installEventFilter(self.keyPressHandler)

    def inbetweenSlideRelease(self):
        try:
            self.slideUI.close()
            self.slideUI.deleteLater()
            self.app.removeEventFilter(self.keyPressHandler)
        except:
            self.app.removeEventFilter(self.keyPressHandler)

    def removeKeyPressHandlers(self):
        self.app.removeEventFilter(self.keyPressHandler)

    def cacheKeyData(self):
        self.selectedCurveDict = dict()
        isHighlighted = self.funcs.isTimelineHighlighted()
        if isHighlighted:
            minTime, maxTime = self.funcs.getTimelineHighlightedRange()
        else:
            minTime = cmds.playbackOptions(query=True, min=True)
            maxTime = cmds.playbackOptions(query=True, max=True)

        selectedCurves = self.funcs.graphEdKeysSelected()

        if selectedCurves:
            self.selectedCurveDict = self.getAnimCurveSelectionAPI()
        else:
            selectedObjects = self.funcs.getSelectedTransforms()
            if not selectedObjects:
                return
            curves, plugs = self.funcs.getAnimCurvesForObjectsAPI(selectedObjects)
            for c in curves:
                node = oma2.MFnAnimCurve(c.object())
                self.selectedCurveDict[node.absoluteName()] = node

        if not self.selectedCurveDict.values():
            self.keyframeData = None
            self.selectedCurveDict = None
            return
        self.keyframeData, self.keyframeRefData = self.getAnimCurveData(self.selectedCurveDict, minTime, maxTime)

    def normalizeAlpha(self, alpha, minVal, maxVal, range=[0, 1]):
        """
        takes the alpha and returns 0-1 range
        :param alpha:
        :param minVal:
        :param maxVal:
        :return:
        """
        return range[0] + (range[1] - range[0]) * ((alpha - minVal) / (maxVal - minVal))

    def doKeyTween(self, alpha=float(), mode=str()):
        self.keyTweenMethods[mode](alpha)

    def tweenPreviousNextGroup(self, alpha):
        if not self.keyframeData.items():
            return
        alpha = self.normalizeAlpha(alpha, -100, 100, range=[-1, 1])
        for curve, keyframeData in self.keyframeData.iteritems():
            for i in range(len(keyframeData.keyIndexes)):
                outValue = self.tweenPreviousNextGroupKey(alpha=alpha,
                                                          currentValue=keyframeData.keyValues[i],
                                                          previousValue=keyframeData.previousValues[keyframeData.keyIndexes[0]],
                                                          nextValue=keyframeData.nextValues[keyframeData.keyIndexes[-1]],
                                                          startValue=keyframeData.keyValues[0],
                                                          endValue=keyframeData.keyValues[-1])
                self.selectedCurveDict[curve].setValue(keyframeData.keyIndexes[i], outValue,
                                                       change=self.animCurveChange)
        '''
        for curve, keyframeData in self.keyframeData.iteritems():
            for i in range(len(keyframeData.keyIndexes)):
                outValue = lerpFloat(keyframeData.keyValues[i], self.keyframeRefData[curve].keyValues[i], alpha)
                self.selectedCurveDict[curve].setValue(keyframeData.keyIndexes[i], outValue,
                                                       change=self.animCurveChange)
        '''

    def tweenPreviousCurrentNext(self, alpha):
        if not self.keyframeData.items():
            return
        for curve, keyframeData in self.keyframeData.iteritems():
            for i in range(len(keyframeData.keyIndexes)):
                outValue = self.tweenPreviousCurrentNextKey(alpha,
                                                            keyframeData.previousValues[keyframeData.keyIndexes[i]],
                                                            keyframeData.keyValues[i],
                                                            keyframeData.nextValues[keyframeData.keyIndexes[i]])
                self.selectedCurveDict[curve].setValue(keyframeData.keyIndexes[i], outValue,
                                                       change=self.animCurveChange)

    def tweenBloat(self, alpha):
        if not self.keyframeData.items():
            return
        for curve, keyframeData in self.keyframeData.iteritems():
            firstIndex = keyframeData.keyIndexes[0]
            lastIndex = keyframeData.keyIndexes[-1]
            for i in range(len(keyframeData.keyIndexes)):
                # index = keyframeData.keyIndexes[i]
                currentIndex = keyframeData.keyIndexes[i]
                outValue = self.tweenBloatKey(alpha=alpha,
                                              firstValue=keyframeData.previousValues[firstIndex],
                                              lastValue=keyframeData.nextValues[lastIndex],
                                              firstTime=keyframeData.previousKeyTimes[firstIndex],
                                              lastTime=keyframeData.nextKeyTimes[lastIndex],
                                              currentValue=keyframeData.keyValues[i],
                                              currentTime=keyframeData.keyTimes[i])
                self.selectedCurveDict[curve].setValue(keyframeData.keyIndexes[i], outValue,
                                                       change=self.animCurveChange)

    def tweenSmoothNeighbours(self, alpha):
        """
        # TODO - actually do it
        Smooths keys to nearest neighbours, taking spacing into account
        :param alpha:
        :return:
        """
        # self.keyframeRefData
        # smooth iteration pass
        alpha = self.normalizeAlpha(alpha, -100, 100, range=[-1, 1])
        if not self.keyframeData:
            return
        for x in range(200):
            for curve, keyframeData in self.keyframeData.iteritems():
                smoothList = [0.0] * len(keyframeData.keyIndexes)
                for i in range(len(keyframeData.keyIndexes)):
                    """
                    Smooth values towards midpoint of nearest neighbours +/-
                    Smooth the key values based on their spacing, 
                    also update the previous/next values for the next iteration
                    """
                    # full weight target inbetween previous and next keys, lerp current towards that?
                    # make this take into account the time between keys
                    average = self.tweenPreviousNextKey(0.5,
                                                        keyframeData.previousValues[keyframeData.keyIndexes[i]],
                                                        keyframeData.nextValues[keyframeData.keyIndexes[i]])
                    smoothList[i] = lerpFloat(average, keyframeData.keyValues[i], 0.5)

                keyframeData.keyValues = smoothList
                for i in range(len(keyframeData.keyIndexes)):
                    if keyframeData.keyIndexes[i] in keyframeData.previouskeyIndexes.keys():
                        keyframeData.previousValues[keyframeData.keyIndexes[i]] = keyframeData.keyValues[i]
                    if keyframeData.keyIndexes[i] in keyframeData.nextkeyIndexes.keys():
                        keyframeData.nextValues[keyframeData.keyIndexes[i]] = keyframeData.keyValues[i]
                self.tweenSmoothNeighboursKey(keyframeData=keyframeData)

        for curve, keyframeData in self.keyframeData.iteritems():
            for i in range(len(keyframeData.keyIndexes)):
                outValue = lerpFloat(keyframeData.keyValues[i], self.keyframeRefData[curve].keyValues[i], alpha)
                self.selectedCurveDict[curve].setValue(keyframeData.keyIndexes[i], outValue,
                                                       change=self.animCurveChange)

    def tweenSmoothNeighboursKey(self, keyframeData):
        """
        Update the previous and next values based on the smoothed list
        :param keyframeData:
        :return:
        """

    def tweenPreviousNextGroupKey(self, alpha=0.5, currentValue=0, previousValue=0, nextValue=0, startValue=0, endValue=0):
        """

        :param alpha:
        :param currentValue:
        :param previousValue:
        :param nextValue:
        :param startValue:
        :param endValue:
        :return:
        """
        if alpha < 0.0:
            return currentValue - ((startValue - previousValue) * (alpha * -1))
        return currentValue + ((nextValue - endValue) * alpha)

    def tweenPreviousNextKey(self, alpha, previousValue, nextValue):
        """

        :param alpha:
        :param previousValue:
        :param nextValue:
        :return:
        """
        alpha = self.normalizeAlpha(alpha, -100, 100)
        return previousValue + (nextValue - previousValue) * alpha

    def tweenPreviousCurrentNextKey(self, alpha, previousValue, currentValue, nextValue):
        """

        :param alpha:
        :param previousValue:
        :param nextValue:
        :return:
        """
        alpha = self.normalizeAlpha(alpha, -100, 100, range=[-1, 1])
        if alpha < 0.0:
            return currentValue + (previousValue - currentValue) * (alpha * -1)
        return currentValue + (nextValue - currentValue) * alpha

    def tweenBloatKey(self, alpha=float(),
                      firstValue=float(),
                      lastValue=float(),
                      firstTime=float(),
                      lastTime=float(),
                      currentValue=float(),
                      currentTime=float()):
        """
        :param alpha:
        :param previousValue:
        :param nextValue:
        :return:
        """
        alpha = self.normalizeAlpha(alpha, -100, 100, range=[-1, 1])
        t = 1 - ((currentTime - firstTime) / (lastTime - firstTime))
        baseValue = lastValue + (firstValue - lastValue) * t
        if alpha < 0.0:  # blend to linear
            return currentValue + (baseValue - currentValue) * (alpha * -1)

        return currentValue + (currentValue - baseValue) * alpha

    def testLerp(self):
        for curve, keyframeData in self.keyframeData.iteritems():
            for i in range(len(keyframeData.keyIndexes)):
                # print (keyframeData.keyValues[i])
                newValue = keyframeData.keyValues[i] + 1
                '''
                new_value = lerp_towards(keyframeData.prev_value[i],
                                         keyframeData.next_value[i], t,
                                         keyframeData.value[i])
                '''
                self.selectedCurveDict[curve].setValue(keyframeData.keyIndexes[i], newValue,
                                                       change=self.animCurveChange)

    def getAnimCurveSelectionAPI(self):
        om2SelectionList = om2.MGlobal.getActiveSelectionList()
        selectionIterator = om2.MItSelectionList(om2SelectionList, om2.MFn.kAnimCurve)

        selectedAnimCurveDict = {}

        while not selectionIterator.isDone():
            if selectionIterator.itemType() in self.funcs.getAnimCurveSelectionAPI():
                obj = selectionIterator.getDependNode()
                if obj.apiType() in self.funcs.getAnimCurveTypesAPI():
                    # get the dependency node
                    node = oma2.MFnAnimCurve(obj)
                    selectedAnimCurveDict[node.absoluteName()] = node

            selectionIterator.next()

        return selectedAnimCurveDict  # .values()

    def getAnimCurveData(self, selectedAnimCurveDict, minTime, maxTime):
        curveDataDict = {}
        curveRefDataDict = {}
        for curveName, curve in selectedAnimCurveDict.iteritems():
            keyTimes = list()
            keyValues = list()
            keyIndexes = cmds.keyframe(curveName, q=True, selected=True, indexValue=True)
            allkeyIndexes = cmds.keyframe(curveName, q=True, indexValue=True)
            # print (curveName, keyIndexes)

            previousKeyTimes = dict()
            previousValues = dict()
            previouskeyIndexes = dict()
            nextKeyTimes = dict()
            nextKeyValues = dict()
            nextkeyIndexes = dict()

            inTangents = list()
            outTangents = list()
            bezierTangents = list()

            # change this to figure out selected keys or not,
            # get the indexes it should work on and then run the same code whatever

            if not keyIndexes:
                keyIndexes = cmds.keyframe(curveName, query=True, indexValue=True, time=(minTime, maxTime))

            # keys are selected
            previouskeyIndexes = {x: max(x - 1, 0) for x in keyIndexes}
            nextkeyIndexes = {x: min(x + 1, allkeyIndexes[-1]) for x in keyIndexes}

            for index, i in enumerate(keyIndexes):
                keyTimes.append(curve.input(keyIndexes[index]).asUnits(om2.MTime.kSeconds))
                keyValues.append(curve.value(keyIndexes[index]))
                previousValues[i] = curve.value(previouskeyIndexes[i])
                nextKeyValues[i] = curve.value(nextkeyIndexes[i])
                previousKeyTimes[i] = curve.input(previouskeyIndexes[i]).asUnits(om2.MTime.kSeconds)
                nextKeyTimes[i] = curve.input(nextkeyIndexes[i]).asUnits(om2.MTime.kSeconds)
                inTangents.append(curve.getTangentXY(keyIndexes[index], True))
                outTangents.append(curve.getTangentXY(keyIndexes[index], False))
            for index, i in enumerate(keyIndexes):
                if index == 0:
                    tangents = self.getBezierTangentPoints(keyTimes[0],
                                                           keyValues[0],
                                                           outTangents[0],
                                                           nextKeyTimes[keyIndexes[0]],
                                                           nextKeyValues[keyIndexes[0]],
                                                           inTangents[min(len(keyIndexes) - 1, 1)])
                    bezierTangents.append([None, tangents])
                elif index == len(keyIndexes) - 1:
                    tangents = self.getBezierTangentPoints(previousKeyTimes[keyIndexes[-1]],
                                                           previousValues[keyIndexes[-1]],
                                                           inTangents[0],
                                                           keyTimes[0],
                                                           keyValues[0],
                                                           outTangents[index - 1])
                    bezierTangents.append([tangents, None])
                else:
                    leftTangent = self.getBezierTangentPoints(keyTimes[index],
                                                              keyValues[index],
                                                              outTangents[index],
                                                              nextKeyTimes[i],
                                                              nextKeyValues[i],
                                                              inTangents[index])
                    rightTangent = self.getBezierTangentPoints(previousKeyTimes[i],
                                                               previousValues[i],
                                                               inTangents[0],
                                                               keyTimes[0],
                                                               keyValues[0],
                                                               outTangents[index - 1])
                    bezierTangents.append([leftTangent, rightTangent])

            keyframeData = KeyframeData(keyTimes=keyTimes,
                                        keyValues=keyValues,
                                        keyIndexes=keyIndexes,
                                        previousKeyTimes=previousKeyTimes,
                                        previousValues=previousValues,
                                        previouskeyIndexes=previouskeyIndexes,
                                        nextKeyTimes=nextKeyTimes,
                                        nextValues=nextKeyValues,
                                        nextkeyIndexes=nextkeyIndexes,
                                        defaultValue=None,
                                        inTangents=inTangents,
                                        outTangents=outTangents,
                                        bezierTangents=bezierTangents)
            # duplicate of the data, to use for multiple iterations of smoothing
            keyframeRefData = KeyframeData(keyTimes=[x for x in keyTimes],
                                           keyValues=[x for x in keyValues],
                                           keyIndexes=[x for x in keyIndexes],
                                           previousKeyTimes={k: v for k, v in previousKeyTimes.items()},
                                           previousValues={k: v for k, v in previousValues.items()},
                                           previouskeyIndexes={k: v for k, v in previouskeyIndexes.items()},
                                           nextKeyTimes={k: v for k, v in nextKeyTimes.items()},
                                           nextValues={k: v for k, v in nextKeyValues.items()},
                                           nextkeyIndexes={k: v for k, v in nextkeyIndexes.items()},
                                           defaultValue=None,
                                           inTangents=[x for x in inTangents],
                                           outTangents=[x for x in outTangents],
                                           bezierTangents=[x for x in bezierTangents])
            curveDataDict[curveName] = keyframeData
            curveRefDataDict[curveName] = keyframeRefData
        return curveDataDict, curveRefDataDict

    def getBezierTangentPoints(self, startTime, startValue, startTangent, endTime, endValue, endTangent):
        """
        Thanks stackOverflow
        :param curve:
        :param startIndex:
        :param endIndex:
        :return:
        """
        b1 = om2.MPoint(startTime, startValue)
        b4 = om2.MPoint(endTime, endValue)
        b2 = om2.MPoint(b1.x + startTangent[0] / 3.0, b1.y + startTangent[1] / 3.0)
        b3 = om2.MPoint(b4.x - endTangent[0] / 3.0, b4.y - endTangent[1] / 3.0)

        return [b1, b2, b3, b4]


class KeyframeData(object):
    """
    Used to cache values to refer to during update.
    Store all the info that might be needed by the inbetween classes here
    """

    def __init__(self,
                 keyTimes=list(),
                 keyValues=list(),
                 keyIndexes=list(),

                 previousKeyTimes=dict(),
                 previousValues=list(),
                 previouskeyIndexes=dict(),

                 nextKeyTimes=dict(),
                 nextValues=dict(),
                 nextkeyIndexes=dict(),

                 defaultValue=None,
                 inTangents=list(),
                 outTangents=list(),
                 bezierTangents=list()):
        self.keyTimes = keyTimes
        self.keyValues = keyValues
        self.keyIndexes = keyIndexes

        self.previousKeyTimes = previousKeyTimes
        self.previousValues = previousValues
        self.previouskeyIndexes = previouskeyIndexes

        self.nextKeyTimes = nextKeyTimes
        self.nextValues = nextValues
        self.nextkeyIndexes = nextkeyIndexes

        self.defaultValue = defaultValue

        self.inTangents = inTangents
        self.outTangents = outTangents
        self.bezierTangents = bezierTangents


class keypressHandler(QObject):

    def __init__(self, tweenClass=None, UI=None):
        super(keypressHandler, self).__init__()
        self.tweenClass = tweenClass
        self.UI = UI

    def eventFilter(self, target, event):
        if event.type() == event.KeyRelease:
            if event.isAutoRepeat():
                return True
            self.UI.keyReleaseEvent(event)
            return False
        elif event.type() == event.KeyPress:
            self.UI.keyPressEvent(event)
            return False
        return False
        # return super(keypressHandler, self).eventFilter(target, event)


class attrData(object):
    """
    Dict contains attr names as key, value as value
    """
    attributes = dict()

    def __init__(self, attributes):
        self.attributes = dict.fromkeys(attributes, None)


def lerpMVector(vecA, vecB, alpha):
    return vecB * alpha + vecA * (1.0 - alpha)


def lerpFloat(a, b, alpha):
    return a * alpha + b * (1.0 - alpha)


class DragButton(QLabel):
    label = str()
    xMin = 0
    xMax = 100
    restPoint = QPoint(0, 0)
    clickOffset = QPoint(0, 0)
    __mousePressPos = None
    __mouseMovePos = None
    restX = 0
    restY = 0
    halfWidth = 10
    uiParent = None
    percent = 50
    draggable = True
    masterDragger = None

    baseIcon = baseIconFile
    hoverIcon = hoverIconFile
    activeIcon = activeIconFile
    inactiveIcon = inactiveIconFile

    minButtonPos = 0
    maxButtonPos = 100

    def __init__(self, label, draggable=True,
                 percent=50,
                 xMin=0,
                 xMax=200,
                 parent=None,
                 uiParent=None,
                 masterDragger=None,
                 baseIcon=baseIconFile,
                 hoverIcon=hoverIconFile,
                 activeIcon=activeIconFile,
                 inactiveIcon=inactiveIconFile,
                 width=16,
                 height=16,
                 ):
        QLabel.__init__(self, parent)
        self.shouldDraw = True
        self.drawWidth = width
        self.drawHeight = height
        sp_retain = QSizePolicy()
        sp_retain.setRetainSizeWhenHidden(True)
        self.setSizePolicy(sp_retain)
        self.uiParent = uiParent
        self.masterDragger = masterDragger
        self.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.setFixedSize(20, 20)
        self.halfWidth = (0.5 * self.width())
        self.baseIcon = QPixmap(os.path.join(IconPath, baseIcon))
        self.hoverIcon = QPixmap(os.path.join(IconPath, hoverIcon))
        self.activeIcon = QPixmap(os.path.join(IconPath, activeIcon))
        self.inactiveIcon = QPixmap(os.path.join(IconPath, inactiveIcon))
        self.setPixmap(self.baseIcon)
        self.draggable = draggable
        self.percent = percent
        self.xMin = xMin
        self.xMax = xMax
        self.setNonHoverSS()
        if self.percent <= 0:
            self.restX = xMin
        elif self.percent >= 100:
            self.restX = xMax - self.width()
        else:
            self.restX = (0.5 * self.width()) + ((xMax - xMin - self.width()) / (100 / self.percent))

        self.minButtonPos = self.xMin
        self.maxButtonPos = self.xMax - self.width()

        self.restY = 7
        self.restPoint = QPoint(self.restX, self.restY)
        self.move(self.restPoint)
        shadow = QGraphicsDropShadowEffect()
        shadow.setOffset(1)
        shadow.setBlurRadius(3)
        self.setGraphicsEffect(shadow)

        self.HoverlineColor = QColor(128, 255, 128, 128)
        self.NonHoverlineColor = QColor(128, 128, 128, 128)

        self.innerLineColour = self.NonHoverlineColor

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        if not self.shouldDraw:
            qp.setCompositionMode(QPainter.CompositionMode_Clear)
            qp.end()
        fillColor = QColor(255, 165, 0, 180)
        lineColor = QColor(64, 64, 64, 128)

        qp.drawRoundedRect(QRect(0.5 * (self.width() - self.drawWidth - 1),
                                 0.5 * (self.height() - self.drawHeight - 1),
                                 self.drawWidth + 2,
                                 self.drawHeight + 2), 2, 2)
        sideEdge = (1.0 / self.rect().width()) * 10
        topEdge = (1.0 / self.rect().height()) * 10

        qp.setRenderHint(QPainter.Antialiasing)
        qp.setCompositionMode(QPainter.CompositionMode_HardLight)
        orange = QColor(255, 160, 47, 64)
        darkOrange = QColor(215, 128, 26, 64)

        qp.setPen(QPen(QBrush(self.innerLineColour), 2))
        grad = QLinearGradient(200, 0, 200, 32)
        grad.setColorAt(0, orange)
        grad.setColorAt(1, darkOrange)
        qp.setBrush(QBrush(grad))

        qp.drawRoundedRect(
            QRect(0.5 * (self.width() - self.drawWidth), 0.5 * (self.height() - self.drawHeight), self.drawWidth,
                  self.drawHeight), 4, 4)

        qp.end()

    def updateAlpha(self):
        """
        sends the alpha value back to the ui parent class
        :return:
        """
        range = (self.xMax) - (self.xMin) - self.width()

        pos = self.pos().x() - (0.5 * self.width())
        alpha = -1 * (1.0 - (pos / (range * 0.5)))
        # print alpha
        if self.uiParent is not None:
            self.uiParent.updateAlpha(alpha)

    def setButtonPosition(self, position):
        self.move(position)
        self.updateAlpha()

    def setButtonToRestPosition(self):
        self.move(self.restPoint)

    def setNonHoverSS(self):
        self.setStyleSheet("""
      QWidget{
          background-color: rgba(50, 50, 50, 0);
          color : rgba(50, 50, 50, 255);

          font-weight: bold;
          border-radius: 6px;
      }
      """)
        # background-image: url('%s\iceCream.png');

    def setHoverSS(self):
        self.setStyleSheet("""
      QWidget{
          background-color: rgba(50, 50, 50, 0);
          color : rgba(50, 50, 50, 255);
          font-weight: bold;
          border-radius: 6px;
      }
      """)

    def setIconStateInactive(self):
        self.shouldDraw = False
        self.setPixmap(self.inactiveIcon)

    def setIconStateBase(self):
        self.shouldDraw = True
        self.setPixmap(self.baseIcon)

    def setIconStateHover(self):
        self.setPixmap(self.hoverIcon)

    def mousePressEvent(self, event):
        self.__mousePressPos = None
        self.__mouseMovePos = None
        if self.uiParent.isDragging:
            #print ('mousePressEvent when already dragging')
            return super(DragButton, self).mousePressEvent(event)
        else:
            self.uiParent.startDrag(event.button())

        if event.button() == Qt.RightButton:
            cmds.warning('RIGHT BUTTON PRESS')

        if event.button() == Qt.LeftButton or event.button() == Qt.RightButton or event.button() == Qt.MiddleButton:
            self.__mousePressPos = event.globalPos()
            self.__mouseMovePos = event.globalPos()
            self.clickOffset = self.mapFromGlobal(event.globalPos())
            self.dragStart = self.mapFromGlobal(event.globalPos())

            self.updatePosition(event.globalPos())

            if self.masterDragger:
                self.masterDragger.setPositionFromSlider(self.pos() + QPoint(self.halfWidth, 0))
            else:
                self.uiParent.hideAllAnchors()
            # self.uiParent.hideAllAnchors()
        super(DragButton, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.RightButton:
            cmds.warning('RIGHT BUTTON MOVE')
        if not self.uiParent.dragButton:
            return super(DragButton, self).mouseMoveEvent(event)
        if event.buttons() == Qt.LeftButton or event.buttons() == Qt.RightButton or event.buttons() == Qt.MiddleButton:
            if not self.draggable:
                if self.masterDragger:
                    # dragging one of those dot controls
                    self.setIconStateInactive()
                    self.masterDragger.setPositionFromSlider(self.pos() + QPoint(self.halfWidth, 0))
                    # TODO - make the drag snap to the other anchors
                    # print self.uiParent.anchorButtons
                    # TODO - maybe split the get new position/alpha and the move
                else:
                    self.uiParent.hideAllAnchors()
            # adjust offset from clicked point to origin of widget
            else:
                self.updatePosition(event.globalPos())

        super(DragButton, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.setIconStateBase()
        self.uiParent.endDrag()
        if self.__mousePressPos is not None:
            moved = event.globalPos() - self.__mousePressPos
            if moved.manhattanLength() > 3:
                event.ignore()
                return

        super(DragButton, self).mouseReleaseEvent(event)

    def updatePosition(self, globalPos):
        if not self.__mousePressPos:
            self.__mousePressPos = globalPos
        if not self.__mouseMovePos:
            self.__mouseMovePos = globalPos
        currPos = self.mapToGlobal(self.pos())

        ScreenVal = self.mapToParent(globalPos).x() - self.clickOffset.x()

        diff = globalPos - self.__mouseMovePos
        diff.setY(0)
        newPos = self.mapFromGlobal(currPos + diff)

        if ScreenVal < self.mapToGlobal(QPoint(self.xMin, 0)).x():
            newPos.setX(self.minButtonPos)
        if ScreenVal >= self.mapToGlobal(QPoint(self.xMax - self.width(), 0)).x():
            # print 'here'
            newPos.setX(self.maxButtonPos)
        # if current mouse position out of slider range, diff = 0

        # print 'new pos', newPos, self.minButtonPos, self.maxButtonPos
        newPos.setX(int(max(newPos.x(), self.minButtonPos)))
        newPos.setX(int(min(newPos.x(), self.maxButtonPos)))
        self.move(newPos)
        self.updateAlpha()
        self.uiParent.setWidgetVisibilityDuringDrag()
        self.__mouseMovePos = globalPos

    def setPositionFromSlider(self, position):
        position.setY(self.restY)
        position.setX(position.x() - self.halfWidth)
        if position.x() <= self.minButtonPos:
            position.setX(self.minButtonPos)
        if position.x() >= self.maxButtonPos:
            position.setX(self.maxButtonPos)
        self.move(position)
        self.updateAlpha()
        self.uiParent.setWidgetVisibilityDuringDrag()

    def enterEvent(self, event):
        # self.setHoverSS()
        self.setHoverTint()
        return super(DragButton, self).enterEvent(event)

    def leaveEvent(self, event):
        self.setNoTint()
        return super(DragButton, self).enterEvent(event)

    def setHoverTint(self):
        self.innerLineColour = self.HoverlineColor
        self.update()

    def setNoTint(self):
        self.innerLineColour = self.NonHoverlineColor
        self.update()

    def setTintEffect(self):
        if self.graphicsEffect() is None:
            self.effect = QGraphicsColorizeEffect(self)
            self.effect.setStrength(0.6)
            self.setGraphicsEffect(self.effect)


class sliderBar(QLabel):
    uiParent = None
    barWidth = 303

    def __init__(self, uiParent, width):
        QLabel.__init__(self)
        self.barWidth = width - 1
        self.uiParent = uiParent
        self.setFixedSize(self.barWidth, 24)
        self.setAlignment(Qt.AlignCenter)
        # self.setStyleSheet("QLabel {background-color: rgba(128, 128, 128, 128);}")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(5)
        self.setGraphicsEffect(shadow)

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)

        fillColor = QColor(255, 165, 0, 180)
        fillColorClear = QColor(255, 165, 0, 0)
        lineColor = QColor(64, 64, 64, 128)
        lineColor2 = QColor(128, 128, 128, 128)
        alpha = 128
        sideEdge = (1.0 / self.rect().width()) * 10
        topEdge = (1.0 / self.rect().height()) * 10
        # qp.setCompositionMode(qp.CompositionMode_Clear)
        # qp.setCompositionMode(qp.CompositionMode_Source)
        qp.setRenderHint(QPainter.Antialiasing)
        orange = QColor(255, 160, 47, alpha)
        darkOrange = QColor(215, 128, 26, alpha)
        grey = QColor(98, 98, 98, alpha)
        qp.setPen(QPen(QBrush(lineColor), 2))
        grad = QLinearGradient(200, 0, 200, alpha)
        grad.setColorAt(0, grey)
        grad.setColorAt(1, grey)
        qp.setBrush(QBrush(grad))
        qp.drawRoundedRect(QRect(0, 2, self.barWidth, 20), 4, 4)
        qp.setPen(QPen(QBrush(lineColor), 4))
        qp.setBrush(QBrush(fillColorClear))

        font = QFont()
        # font.setStrikeOut(True)
        font.setStyleHint(QFont.Helvetica, QFont.PreferAntialias)
        font.setPointSize(12)
        qp.setBrush(Qt.black)
        qp.setFont(font)

        textPath = QPainterPath()
        qp.setPen(QColor(255, 160, 47, 255))
        qp.setBrush(QColor(255, 128, 78, 255))
        textPath.addText(5, 18, font, "Feedback>")
        # qp.drawPath(textPath)

        qp.end()
        return
        # qp.setCompositionMode(qp.CompositionMode_Overlay)
        # qp.setCompositionMode(qp.CompositionMode_Darken)
        qp.setPen(QPen(QBrush(lineColor), 4))
        grad = QLinearGradient(200, 0, 200, 32)
        grad.setColorAt(0, QColor(0, 0, 0, alpha))
        grad.setColorAt(topEdge, QColor(255, 255, 255, alpha * 0.5))
        grad.setColorAt(1 - topEdge, QColor(255, 255, 255, alpha * 0.5))
        grad.setColorAt(1, QColor(0, 0, 0, alpha))
        qp.setBrush(QBrush(grad))
        qp.drawRoundedRect(self.rect(), 4, 4)
        grad = QLinearGradient(0, 16, 400, 16)
        grad.setColorAt(0, QColor(0, 0, 0, alpha))
        grad.setColorAt(sideEdge, QColor(255, 255, 255, alpha * 0.5))
        grad.setColorAt(1 - sideEdge, QColor(255, 255, 255, alpha * 0.5))
        grad.setColorAt(1, QColor(0, 0, 0, alpha))

        qp.setBrush(QBrush(grad))
        # qp.setBrush(QBrush(self.currentFillColour))

        qp.drawRoundedRect(self.rect(), 4, 4)

    def mousePressEvent(self, event):
        if self.uiParent.isDragging:
            cmds.warning('mousePressEvent when already dragging')
        self.uiParent.hideAllAnchors()
        self.uiParent.startDrag(event.button())

        self.__mousePressPos = None
        self.__mouseMovePos = None
        if event.button() == Qt.LeftButton:
            self.__mousePressPos = event.globalPos()
            self.__mousePressPos.setX(self.__mousePressPos.x() + 8)
            self.__mouseMovePos = event.globalPos()

        self.uiParent.dragButton.setPositionFromSlider(self.mapFromGlobal(self.__mousePressPos))
        super(sliderBar, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        self.uiParent.hideAllAnchors()
        if event.buttons() == Qt.LeftButton:
            # adjust offset from clicked point to origin of widget
            self.__mousePressPos = event.globalPos()
            self.__mouseMovePos = event.globalPos()
            self.__mousePressPos.setX(self.__mousePressPos.x() + 8)

        self.uiParent.dragButton.setPositionFromSlider(self.mapFromGlobal(self.__mousePressPos))

        super(sliderBar, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.uiParent.endDrag()
        super(sliderBar, self).mouseReleaseEvent(event)


class sliderWidget(QWidget):
    def __init__(self, parent, tweemClass=tweenBase,
                 objectTweenClass=None,
                 objectShiftTweenClass=None,
                 objectControlTweenClass=None,
                 keyTweenLMB=keyframeTween,
                 keyTweenMMB=keyframeTween,
                 keyTweenRMB=keyframeTween,
                 keyShiftTweenClass=None,
                 keyControlTweenClass=None,
                 funcs=None,
                 largeAnchors=[0, 100.0],
                 mediumAnchors=[25.0, 75.0],
                 smallAnchors=[12.5, 37.5, 62.5, 87.5]
                 ):
        QWidget.__init__(self, parent)

        self.isDragging = False
        self.currentDragButton = None
        if tweemClass is None:
            self.tweenClass = tweenBase()
        else:
            self.tweenClass = tweemClass
        self.keyTweenClassDict = {
            Qt.LeftButton: keyTweenLMB,
            Qt.MiddleButton: keyTweenMMB,
            Qt.RightButton: keyTweenRMB,
        }
        self.objTweenClassDict = {
            Qt.LeftButton: WorldSpaceTween,
            Qt.MiddleButton: WorldSpaceTween,
            Qt.RightButton: WorldSpaceTween,
        }
        self.currentTweenClassDict = None
        self.affectingKeys = True
        self.funcs = funcs
        self.barHorizontalOffset = 10
        self.setFocus()
        self.lastEvent = None
        self.dragButton = None
        self.anchorButtons = list()
        self.largeAnchorPositions = list()
        self.mediumAnchorPositions = list()
        self.smallAnchorPositions = list()
        self.tweenClass = None
        self.barWidth = 302
        self.largeAnchorPositions = largeAnchors
        self.mediumAnchorPositions = mediumAnchors
        self.smallAnchorPositions = smallAnchors
        self.setFixedSize(500, 64)
        self.mainLayout = QHBoxLayout(self)
        # self.setStyleSheet('QWidget{margin-left:-1px;}')
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        # self.mainLayout.setSpacing(0)
        self.horizontalBar = sliderBar(self, self.barWidth)
        self.dragButton = DragButton("BD",
                                     xMin=self.barHorizontalOffset,
                                     xMax=self.horizontalBar.width() + self.barHorizontalOffset - 1,
                                     parent=self.horizontalBar,
                                     uiParent=self,
                                     )

        self.setFocusPolicy(Qt.StrongFocus)

        self.dragButton.setFocusPolicy(Qt.StrongFocus)

        for p in self.largeAnchorPositions:
            anchorBtn = DragButton("BD",
                                   xMin=self.barHorizontalOffset,
                                   xMax=self.horizontalBar.width() + self.barHorizontalOffset - 1,
                                   parent=self.horizontalBar,
                                   uiParent=self,
                                   draggable=False,
                                   percent=p,
                                   masterDragger=self.dragButton,
                                   baseIcon=barSmallIconFile,
                                   hoverIcon=barSmallIconFile,
                                   activeIcon=dotSmallIconFile,
                                   inactiveIcon=inactiveIconFile,
                                   width=10,
                                   height=10,
                                   )
            self.anchorButtons.append(anchorBtn)
        for p in self.mediumAnchorPositions:
            anchorBtn = DragButton("BD",
                                   xMax=self.horizontalBar.width() - 1,
                                   parent=self.horizontalBar,
                                   uiParent=self,
                                   draggable=False,
                                   percent=p,
                                   masterDragger=self.dragButton,
                                   baseIcon=dotSmallIconFile,
                                   hoverIcon=dotSmallIconFile,
                                   activeIcon=dotSmallIconFile,
                                   inactiveIcon=inactiveIconFile,
                                   width=6,
                                   height=6,
                                   )
            self.anchorButtons.append(anchorBtn)
        for p in self.smallAnchorPositions:
            anchorBtn = DragButton("BD",
                                   xMax=self.horizontalBar.width(),
                                   parent=self.horizontalBar,
                                   uiParent=self,
                                   draggable=False,
                                   percent=p,
                                   masterDragger=self.dragButton,
                                   baseIcon=dotSmallIconFile,
                                   hoverIcon=dotSmallIconFile,
                                   activeIcon=dotSmallIconFile,
                                   inactiveIcon=inactiveIconFile,
                                   width=6,
                                   height=6,
                                   )
            self.anchorButtons.append(anchorBtn)
        self.mainLayout.addWidget(self.horizontalBar)
        self.horizontalBar.move(2, 2)
        for btn in self.anchorButtons:
            self.mainLayout.addWidget(btn)
        self.mainLayout.addWidget(self.dragButton)

        self.labelLayout = QHBoxLayout()
        self.mainLayout.addLayout(self.labelLayout)

        # self.label = QLabel('testy test test')
        # self.label.setFixedWidth(200)
        # self.label.setStyleSheet("color: black")
        # spacerItem = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        # self.labelLayout.addWidget(self.label)
        # self.labelLayout.addItem(spacerItem)

        self.setAttribute(Qt.WA_StyledBackground, True)
        self.autoFillBackground = True
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.windowFlags()
        self.setSS()

        self.fillColourBaseTop = QColor(255, 160, 47, 88)
        self.fillColourBaseBottom = QColor(215, 128, 26, 88)
        self.fillColourAltTop = QColor(255, 160, 200, 88)
        self.fillColourAltBottom = QColor(215, 128, 200, 88)
        self.currentFillColourTop = self.fillColourBaseTop
        self.currentFillColourBottom = self.fillColourBaseBottom

    def createSelectionChangedScriptJob(self):
        self.selectionChangedCallback = cmds.scriptJob(event=("SelectionChanged", pm.Callback(self.updateTweenClass)))
        return self.selectionChangedCallback

    def setWidgetVisibilityDuringDrag(self):
        pass

    def hideAllAnchors(self):
        cmds.warning('hide all anchors')
        for btn in self.anchorButtons:
            btn.setIconStateInactive()
            btn.update()

    def showAllAnchors(self):
        for btn in self.anchorButtons:
            btn.setIconStateBase()
            btn.update()

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        alpha = 255

        fillColor = QColor(128, 128, 128, alpha)
        lineColor = QColor(64, 64, 64, 64)

        orange = QColor(255, 160, 47, alpha)
        darkOrange = QColor(215, 128, 26, alpha)

        outlineGradient = QLinearGradient(0, -1000, 300, 1000)
        outlineGradient.setColorAt(0, Qt.white)
        outlineGradient.setColorAt(0.3, orange)
        outlineGradient.setColorAt(0.6, orange)
        outlineGradient.setColorAt(1, Qt.black)
        qp.setBrush(QBrush(outlineGradient))

        qp.setBrush(QBrush(fillColor))
        qp.setPen(QPen(QBrush(fillColor), 1))
        qp.setRenderHint(QPainter.Antialiasing)
        # qp.setCompositionMode(qp.CompositionMode_Source)
        # qp.setCompositionMode(qp.CompositionMode_Darken)
        qp.drawRoundedRect(QRect(0, 0, 321, 52), 4, 4)

        # qp.setCompositionMode(qp.CompositionMode_Clear)

        grad = QLinearGradient(200, 0, 200, 32)
        grad.setColorAt(0, orange)
        grad.setColorAt(1, darkOrange)
        qp.setBrush(QBrush(grad))
        # qp.setCompositionMode(qp.CompositionMode_Source)

        font = QFont()
        font.setStyleHint(QFont.Courier, QFont.PreferAntialias)
        font.setPointSize(10)
        qp.setBrush(Qt.black)
        qp.setFont(font)

        textPath = QPainterPath()
        qp.setPen(QColor(64, 64, 64, 255))
        qp.setBrush(QColor(64, 64, 64, 255))
        textPath.addText(16, 44, font, self.tweenClass.labelText)
        qp.drawPath(textPath)

        '''
        textRect.translate(0,1)
        qp.setPen(QColor(0,0,0,20))
        qp.drawText(textRect, Qt.AlignLeft, self.tweenClass.labelText)
        textRect.translate(0, -2)
        qp.setPen(QColor(0,0,0,255))
        qp.drawText(textRect, Qt.AlignLeft, self.tweenClass.labelText)
        textRect.translate(0, 1)
        '''

        qp.end()
        '''
        fillColor = QColor(255, 165, 0, 180)
        lineColor = QColor(64, 64, 64, 64)
        alpha = 50
        sideEdge = (1.0 / self.rect().width()) * 10
        topEdge = (1.0 / self.rect().height()) * 10
        qp.setCompositionMode(qp.CompositionMode_Clear)
        # qp.setCompositionMode(qp.CompositionMode_Source)
        qp.setRenderHint(QPainter.Antialiasing)
        orange = QColor(255, 160, 47, 32)
        darkOrange = QColor(215, 128, 26, 32)

        qp.setPen(QPen(QBrush(lineColor), 0))
        grad = QLinearGradient(200, 0, 200, 32)
        grad.setColorAt(0, self.currentFillColourTop)
        grad.setColorAt(1, self.currentFillColourBottom)
        qp.setBrush(QBrush(grad))
        qp.drawRoundedRect(self.rect(), 4, 4)

        # qp.setCompositionMode(qp.CompositionMode_Overlay)
        # qp.setCompositionMode(qp.CompositionMode_Darken)
        qp.setPen(QPen(QBrush(lineColor), 4))
        grad = QLinearGradient(200, 0, 200, 32)
        grad.setColorAt(0, QColor(0, 0, 0, alpha))
        grad.setColorAt(topEdge, QColor(255, 255, 255, alpha * 0.5))
        grad.setColorAt(1 - topEdge, QColor(255, 255, 255, alpha * 0.5))
        grad.setColorAt(1, QColor(0, 0, 0, alpha))
        qp.setBrush(QBrush(grad))
        qp.drawRoundedRect(self.rect(), 4, 4)
        grad = QLinearGradient(0, 16, 400, 16)
        grad.setColorAt(0, QColor(0, 0, 0, alpha))
        grad.setColorAt(sideEdge, QColor(255, 255, 255, alpha * 0.5))
        grad.setColorAt(1 - sideEdge, QColor(255, 255, 255, alpha * 0.5))
        grad.setColorAt(1, QColor(0, 0, 0, alpha))

        qp.setBrush(QBrush(grad))
        # qp.setBrush(QBrush(self.currentFillColour))

        qp.drawRoundedRect(self.rect(), 4, 4)
        '''
        qp.end()

    def windowFlags(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.X11BypassWindowManagerHint | Qt.Tool)

    def move_UI(self):
        ''' Moves the UI to the widget position '''
        pos = QCursor.pos()
        xOffset = 10  # border?
        self.move(pos.x() - (self.width() * 0.5) + 88, pos.y() - (self.height() * 0.5) + 15)

    def arrangeUI(self):
        self.horizontalBar.move(self.barHorizontalOffset, 6)

        self.dragButton.setButtonToRestPosition()
        for btn in self.anchorButtons:
            btn.setButtonToRestPosition()
        self.update()

    def setSS(self):
        self.setStyleSheet("""
      QWidget{
          background-color: rgba(55, 250, 55, 0);
      }
        QLabel{
          background-color: rgba(55, 250, 55, 0);
      }
      QLayout{
          background: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #2d2d2d, stop: 0.1 #2b2b2b, stop: 0.5 #292929, stop: 0.9 #282828, stop: 1 #252525);
      }
      QFrame{
          border-style: None;
          border-color: rgba(55, 55, 55, 128);
          border-width: 5px;
          border-radius: 5px;
          background-color: rgba(55, 55, 55, 0);
      }
      """)

    def mousePressEvent(self, event):
        self.__mousePressPos = None
        self.__mouseMovePos = None
        if event.button() == Qt.LeftButton:
            self.__mousePressPos = event.globalPos()
            self.__mouseMovePos = event.globalPos()
        # print self.__mousePressPos, self.mapFromParent(self.__mousePressPos)
        super(sliderWidget, self).mousePressEvent(event)

    def enterEvent(self, event):
        return super(sliderWidget, self).enterEvent(event)

    def leaveEvent(self, event):
        return super(sliderWidget, self).enterEvent(event)

    def begin(self):
        """
        Turn auto key off to stop keyframe spamming updates killing performance
        :return:
        """
        self.tweenClass.begin()

    def updateAlpha(self, alpha):
        # print 'sliderWidget updateAlpha', self.tweenClass, alpha
        self.tweenClass.updateAlpha(alpha)

    def show(self):
        super(sliderWidget, self).show()
        self.setEnabled(True)
        self.setFocus()

    def close(self):
        cmds.scriptJob(kill=self.selectionChangedCallback)
        super(sliderWidget, self).hide()

    def showUI(self):
        self.updateTweenClass()
        self.move_UI()
        self.show()
        self.arrangeUI()
        # self.updateTweenClass()

    def startDrag(self, button):
        cmds.warning('starting new drag on button!!', button)
        self.updateTweenClass()

        self.tweenClass = self.currentTweenClassDict[button]()
        self.tweenClass.setAffectedObjects()
        self.tweenClass.cacheValues()
        self.tweenClass.get_modifier()
        cmds.warning('affectedObjects', self.tweenClass.affectedObjects)
        self.currentDragButton = button
        self.isDragging = True

    def endDrag(self):
        self.isDragging = False
        self.currentDragButton = None
        self.tweenClass.apply()
        self.showAllAnchors()
        self.updateTweenClass()

    def updateTweenClass(self):
        """
        query the selection to decide what is the most appropriate tween class to use
        :return:
        """
        cmds.warning('updating tween class')
        selectedKeys = cmds.keyframe(query=True, selected=True)
        selectedObjects = cmds.ls(sl=True, type='transform')
        geState = getGraphEditorState()
        if not geState:
            self.affectingKeys = False
            self.currentTweenClassDict = self.objTweenClassDict
        else:
            if selectedKeys:
                self.affectingKeys = True
                self.currentTweenClassDict = self.keyTweenClassDict
            elif selectedObjects:
                self.affectingKeys = False
                self.currentTweenClassDict = self.objTweenClassDict
        self.tweenClass = self.currentTweenClassDict[Qt.LeftButton]()
        # self.label.setText(self.tweenClass.labelText)
        self.arrangeUI()
        self.tweenClass.setAffectedObjects()
        self.tweenClass.cacheValues()
        cmds.warning(self.tweenClass, self.tweenClass.labelText)
        self.update()

    def get_modifier(self):
        cmds.warning('cmds.getModifiers()', cmds.getModifiers())
        self.keyboardModifier = {0: None, 1: 'shift', 4: 'ctrl'}[cmds.getModifiers()]

    def shiftPressed(self):
        cmds.warning('UI shift pressed')
        if self.isDragging:
            return
        # self.horizontalBar.setStyleSheet("QLabel {background-color: rgba(255, 128, 128, 128);}")
        self.currentFillColourTop = self.fillColourAltTop
        self.currentFillColourBottom = self.fillColourAltBottom
        self.update()
        # self.dragButton.setPixmap(self.dragButton.inactiveIcon)

    def shiftReleased(self):
        cmds.warning('UI shift released')
        if self.isDragging:
            return
        # self.horizontalBar.setStyleSheet("QLabel {background-color: rgba(128, 128, 128, 128);}")
        self.currentFillColourTop = self.fillColourBaseTop
        self.currentFillColourBottom = self.fillColourBaseBottom
        self.update()
        # self.dragButton.setPixmap(self.dragButton.activeIcon)

    def controlPressed(self):
        cmds.warning('UI control pressed')

    def controlReleased(self):
        cmds.warning('UI control released')


def getMObject(node):
    selList = om2.MSelectionList()
    selList.add(node)
    return selList.getDependNode(0)


# TODO - stop using this
def getGraphEditorState():
    """
    use this to determine if we should act on selected keys based on graph editor visibility
    :return:
    """
    GraphEdWindow = None
    state = False
    if cmds.animCurveEditor('graphEditor1GraphEd', query=True, exists=True):
        graphEdParent = cmds.animCurveEditor('graphEditor1GraphEd', query=True, panel=True)
        if not cmds.panel(graphEdParent, query=True, exists=True):
            return False
        if cmds.panel(graphEdParent, query=True, exists=True):
            GraphEdWindow = cmds.panel(graphEdParent, query=True, control=True).split('|')[0]

    if GraphEdWindow:
        state = cmds.workspaceControl(GraphEdWindow, query=True, collapse=True)
        return not state
    return False


sliderStyleSheet = """
QSlider {{ margin: 0px;
 height: 20px;
 border: 1px solid #2d2d2d;
 border-radius: 5px;
 }}
QSlider::groove:horizontal {{
    height: 20px;
	margin: 0px;
	background-color: #343B48;
}}
QSlider::groove:horizontal:hover {{
	background-color: #373E4C;
}}
QSlider::handle:horizontal {{
    background-color: rgb(189, 147, 249);
    border: none;
    height: 20px;
    width: 20px;
    margin: 0px;
	border-radius: 5px;
	image: url(":greasePencilPreGhostOff.png");
}}
QSlider::handle:horizontal:hover {{
    background-color: rgb(195, 155, 255);
}}
QSlider::handle:horizontal:pressed {{

    background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #ffa02f, stop: 1 #d7801a);
}}

QSlider::groove:vertical {{
    border-radius: 5px;
    width: 10px;
    margin: 0px;
	background-color: rgb(52, 59, 72);
}}
QSlider::groove:vertical:hover {{
	background-color: rgb(55, 62, 76);
}}
QSlider::handle:vertical {{
    background-color: rgb(189, 147, 249);
	border: none;
    height: 10px;
    width: 10px;
    margin: 0px;
	border-radius: 5px;
}}
QSlider::handle:vertical:hover {{
    background-color: rgb(195, 155, 255);
}}
QSlider::handle:vertical:pressed {{
    background-color: rgb(255, 121, 198);
}}"""

overShootSliderStyleSheet = """
QSlider {{ margin: 0px;
 height: 20px;
 border: 1px solid #343B48;
 border-radius: 5px;
 }}
QSlider::handle:horizontal {{
    background-color: rgb(189, 147, 249);
    border: none;
    height: 20px;
    width: 20px;
    margin: 0px;
	border-radius: 5px;
	image: url(":greasePencilPreGhostOff.png");
}}
QSlider::handle:horizontal:hover {{
    background-color: rgb(195, 155, 255);
}}
QSlider::handle:horizontal:pressed {{

    background-color: rgb(255, 121, 198);
}}

QSlider::groove:vertical {{
    border-radius: 5px;
    width: 10px;
    margin: 0px;
	background-color: rgb(52, 59, 72);
}}
QSlider::groove:vertical:hover {{
	background-color: rgb(55, 62, 76);
}}
QSlider::handle:vertical {{
    background-color: rgb(189, 147, 249);
	border: none;
    height: 10px;
    width: 10px;
    margin: 0px;
	border-radius: 5px;
}}
QSlider::handle:vertical:hover {{
    background-color: rgb(195, 155, 255);
}}
QSlider::handle:vertical:pressed {{
    background-color: rgb(255, 121, 198);
}}
}}
"""

overShootSliderStyleSheetBar = """
QSlider::groove:horizontal {{
background: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, 
stop: 0 {baseColour}, 
stop: {stop1} {barColour}, 
stop: {stop2} {barColour}, 
stop: {stop3} {baseColour}, 
stop: {stop4} {baseColour}, 
stop: {stop5} {barColour}, 
stop: {stop6} {barColour}, 
stop: 1 {baseColour});
    height: 20px;
	margin: 0px;
}}
QSlider::groove:horizontal:hover {{
background: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, 
stop: 0 {hoverColour}, 
stop: {stop1} {barColour}, 
stop: {stop2} {barColour}, 
stop: {stop3} {hoverColour}, 
stop: {stop4} {hoverColour}, 
stop: {stop5} {barColour}, 
stop: {stop6} {barColour}, 
stop: 1 {hoverColour});
}}
"""


class PySlider(QSlider):
    wheelSignal = Signal(float)

    def __init__(self,
                 margin=0,
                 bg_size=20,
                 bg_radius=10,
                 bg_color="#1b1e23",
                 bg_color_hover="#1e2229",
                 handle_margin=2,
                 handle_size=16,
                 handle_radius=8,
                 handle_color="#568af2",
                 handle_color_hover="#6c99f4",
                 handle_color_pressed="#3f6fd1",
                 minValue=-101,
                 minOvershootValue=-202,
                 maxValue=101,
                 maxOvershootValue=202,
                 ):
        super(PySlider, self).__init__()

        self.minValue = minValue
        self.minOvershootValue = minOvershootValue
        self.maxValue = maxValue
        self.maxOvershootValue = maxOvershootValue

        self.adjust_style = sliderStyleSheet.format()
        self.resetStyle()
        self.overshootState = False
        # self.setPopupMenu(SliderButtonPopup)
        # self.setContextMenuPolicy(Qt.ActionsContextMenu)

    def contextMenuEvent(self, event):
        pass
        # print ('contextMenuEvent', event.globalPos())

    def resetStyle(self):
        self.setStyleSheet(self.adjust_style)

    def toggleOvershoot(self, overshootState):
        self.overshootState = overshootState
        if self.overshootState:
            self.setMaximum(self.maxOvershootValue)
            self.setMinimum(self.minOvershootValue)
            self.updateOvershootStyle()
        else:
            self.setMaximum(self.maxValue)
            self.setMinimum(self.minValue)
            self.resetStyle()

    def wheelEvent(self, event):
        #cmds.warning(self.x(), event.delta() / 120.0 * 25)
        self.setValue(self.value() + event.delta() / 120.0 * 25)
        # super(PySlider, self).wheelEvent(event)
        self.wheelSignal.emit(self.value())

    def sliderMovedEvent(self, *args):
        if self.overshootState:
            self.updateOvershootStyle()

    def updateOvershootStyle(self):
        '''
        style = overShootSliderStyleSheetBar.format(baseColour='#343B48',
                                                    hoverColour='#373E4C',
                                                    barColour='#ec0636',
                                                    stop1='0.1',
                                                    stop2='0.2',
                                                    stop3='0.1',
                                                    stop4='0.1',
                                                    stop5='0.1',
                                                    )
        self.setStyleSheet(overShootSliderStyleSheet.format(stop=self.value()))
        '''
        pass

    def paintEvent(self, event):
        super(PySlider, self).paintEvent(event)
        qp = QPainter()
        qp.begin(self)

        lineColor = QColor(68, 68, 68, 64)

        qp.setCompositionMode(qp.CompositionMode_Overlay)
        qp.setRenderHint(QPainter.Antialiasing)
        if self.overshootState:
            qp.setPen(QPen(QBrush(lineColor), 0))
            qp.setBrush(QBrush(lineColor))
            leftBarPos = (self.width() * 0.25) + 5
            righBarPos = (self.width() * 0.75) - 5
            minSize = self.minimumSizeHint()
            offset = minSize.width() * 0.5

            qp.drawLine(righBarPos, 0, righBarPos, self.height())
            qp.drawLine(leftBarPos, 0, leftBarPos, self.height())
            qp.drawRect(0, 0, leftBarPos, self.height())
            qp.drawRect(righBarPos, 0, righBarPos, self.height())
        qp.end()

    def sliderReleasedEvent(self, *args):
        self.resetStyle()


class sliderButton(QPushButton):
    def __init__(self, label,
                 parent,
                 bg_color="#1b1e23",

                 ):
        super(sliderButton, self).__init__(label, parent)

        adjust_style = sliderStyleSheet.format()
        # self.setStyleSheet(adjust_style)
        self.setFixedSize(20, 20)


class SliderWidget(BaseDialog):
    __instance = None
    # call the tween classes by name, send value
    sliderUpdateSignal = Signal(str, float)
    sliderEndedSignal = Signal(str, float)
    sliderBeginSignal = Signal(str, float)
    modeChangedSignal = Signal(str)
    sliderCancelSignal = Signal()

    minValue = -101
    minOvershootValue = -201
    maxValue = 101
    maxOvershootValue = 201
    baseSliderWidth = 260
    baseWidth = 270

    baseLabel = 'baseLabel'
    shiftLabel = 'shiftLabel'
    controlLabel = 'controlLabel'
    controlShiftLabel = 'controlShiftLabel'
    altLabel = 'altLabel'
    '''
    def __new__(cls):
        if SliderWidget.__instance is None:
            if cmds.about(version=True) == '2022':
                SliderWidget.__instance = BaseDialog.__new__(cls)
            else:
                if QTVERSION < 5:
                    SliderWidget.__instance = BaseDialog.__new__(cls)
                else:
                    SliderWidget.__instance = object.__new__(cls)

        SliderWidget.__instance.val = 'SliderWidget'
        SliderWidget.__instance.app = QApplication.instance()
        return SliderWidget.__instance
    '''
    def __init__(self,
                 parent=wrapInstance(int(omUI.MQtUtil.mainWindow()), QWidget),
                 showLockButton=True, showCloseButton=False,
                 title='inbetween',
                 text='test',
                 modeList=list(),
                 baseLabel='baseLabel',
                 shiftLabel='shiftLabel',
                 controlLabel='controlLabel',
                 controlShiftLabel='controlShiftLabel',
                 altLabel='altLabel',
                 showInfo=True,
                 ):
        super(SliderWidget, self).__init__(parent=parent,
                                           title=title,
                                           text=text,
                                           showLockButton=showLockButton, showCloseButton=showCloseButton)

        self.isCancelled = False
        self.recentlyOpened = False
        self.invokedKey = None
        self.modeList = modeList
        self.setFixedSize(270, 60)
        self.setWindowOpacity(0.9)
        #
        if not showInfo:
            self.infoText.hide()
        # labels
        self.baseLabel = baseLabel
        self.shiftLabel = shiftLabel
        self.controlLabel = controlLabel
        self.controlShiftLabel = controlShiftLabel
        self.altLabel = altLabel

        # self.setWindowFlags(Qt.PopupFocusReason | Qt.Tool | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.autoFillBackground = True
        self.windowFlags()
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        self.isDragging = False

        self.container = QFrame()
        self.container.setStyleSheet("QFrame {{ background-color: #343b48; color: #8a95aa; }}")

        self.slider_2 = PySlider()
        self.slider_2.setOrientation(Qt.Horizontal)
        self.slider_2.setMinimumWidth(self.baseSliderWidth)
        self.slider_2.setMinimum(-101)
        self.slider_2.setMaximum(101)
        self.slider_2.setValue(0)
        self.slider_2.setTickInterval(1)

        self.slider_2.sliderPressed.connect(self.sliderPressed)
        self.slider_2.sliderMoved.connect(self.sliderValueChanged)
        self.slider_2.sliderMoved.connect(self.slider_2.sliderMovedEvent)
        self.slider_2.wheelSignal.connect(self.sliderWheelUpdate)
        self.slider_2.sliderReleased.connect(self.sliderReleased)
        self.slider_2.sliderReleased.connect(self.slider_2.sliderReleasedEvent)

        self.setLayout(self.layout)
        self.layout.addWidget(self.slider_2)
        self.layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        self.overlayLabel = QLabel('', self)
        self.overlayLabel.setStyleSheet("background: rgba(255, 0, 0, 0); color : rgba(255, 255, 255, 168)")
        self.overlayLabel.setEnabled(False)
        self.overlayLabel.setFixedWidth(60)
        self.overlayLabel.setAttribute(Qt.WA_TransparentForMouseEvents)

        self.comboBox = QComboBox()
        self.comboBox.setStyleSheet(getqss.getStyleSheet())
        if self.modeList:
            self.titleLayout.insertWidget(3, self.comboBox)
        self.overshootButton = LockButton('', self, icon='overshootOn.png',
                                          unlockIcon='overshoot.png', )
        self.overshootButton.lockSignal.connect(self.toggleOvershoot)
        self.titleLayout.insertWidget(3, self.overshootButton)
        for c in self.modeList:
            self.comboBox.addItem(c)
        self.currentMode = self.comboBox.currentText()
        self.comboBox.currentIndexChanged.connect(self.modeChanged)
        width = self.comboBox.minimumSizeHint().width()
        self.comboBox.view().setMinimumWidth(width)
        self.comboBox.setMinimumWidth(width + 16)
        # self.resize(self.sizeHint())
        self.setFocusPolicy(Qt.StrongFocus)
        self.infoText.setText(self.baseLabel)

        # emit the mode change signal to load the labels
        self.modeChangedSignal.emit(self.currentMode)
        self.overlayLabel.move(20, self.height() - 20)

    def show(self):
        super(SliderWidget, self).show()
        self.resetValues()
        self.setEnabled(True)
        self.setFocus()
        self.recentlyOpened = True

    def moveToCursor(self):
        pos = QCursor.pos()
        xOffset = 10  # border?
        self.move(pos.x() - (self.width() * 0.5), pos.y() - (self.height() * 0.5) - 12)

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)

        lineColor = QColor(68, 68, 68, 128)

        qp.setCompositionMode(qp.CompositionMode_Source)
        qp.setRenderHint(QPainter.Antialiasing)

        qp.setPen(QPen(QBrush(lineColor), 2))
        grad = QLinearGradient(200, 0, 200, 32)
        grad.setColorAt(0, "#323232")
        grad.setColorAt(0.1, "#373737")
        grad.setColorAt(1, "#323232")
        qp.setBrush(QBrush(grad))
        qp.drawRoundedRect(self.rect(), 8, 8)
        qp.end()

    def keyPressEvent(self, event):
        if event.type() == event.KeyPress:
            if self.recentlyOpened:
                if event.key() is not None:
                    self.invokedKey = event.key()
                    self.recentlyOpened = False
            modifiers = QApplication.keyboardModifiers()

            if not event.isAutoRepeat():
                if event.key() == Qt.Key_Alt:
                    self.altPressed()
                    return
                if event.key() == Qt.Key_Control:
                    if modifiers == Qt.ShiftModifier:
                        self.controlShiftPressed()
                    else:
                        self.controlPressed()
                elif event.key() == Qt.Key_Shift:
                    if modifiers == Qt.ControlModifier:
                        self.controlShiftPressed()
                    else:
                        self.shiftPressed()
        if not self.invokedKey or self.invokedKey == event.key():
            return
        super(SliderWidget, self).keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if event.key() != Qt.Key_Control and event.key() != Qt.Key_Shift and event.key() != Qt.Key_Alt:
            if not self.lockState:
                if not self.invokedKey or self.invokedKey == event.key():
                    SlideTools().removeKeyPressHandlers()
                    self.hide()
        if event.type() == event.KeyRelease:
            modifiers = QApplication.keyboardModifiers()

            if event.key() == Qt.Key_Alt:
                self.modifierReleased()
            if event.key() == Qt.Key_Control:
                if modifiers == (Qt.ShiftModifier | Qt.ControlModifier):
                    self.shiftPressed()
                else:
                    self.modifierReleased()
            elif event.key() == Qt.Key_Shift:
                if modifiers == (Qt.ShiftModifier | Qt.ControlModifier):
                    self.controlPressed()
                else:
                    self.modifierReleased()

    def modifierReleased(self):
        self.infoText.setText(self.baseLabel)

    def controlReleased(self):
        self.infoText.setText(self.baseLabel)

    def controlPressed(self):
        self.infoText.setText(self.controlLabel)

    def controlShiftPressed(self):
        self.infoText.setText(self.controlShiftLabel)

    def shiftPressed(self):
        self.infoText.setText(self.shiftLabel)

    def altPressed(self):
        self.infoText.setText(self.altLabel)

    def mousePressEvent(self, event):
        # print ("Mouse Clicked", event.buttons(), event.button() == Qt.RightButton)
        if event.button() == Qt.RightButton:
            self.sliderReleased(cancel=True)
        if event.button() == Qt.LeftButton:
            self.restoreSlider()

    def sliderValueChanged(self):
        if self.slider_2.value() > self.slider_2.maximum() * 0.6:
            self.overlayLabel.move(10, self.height() - 20)
            self.overlayLabel.setAlignment(Qt.AlignLeft)
        elif self.slider_2.value() < self.slider_2.minimum() * 0.6:
            self.overlayLabel.move(self.width() - self.overlayLabel.width() - 10, self.height() - 20)
            self.overlayLabel.setAlignment(Qt.AlignRight)
        self.overlayLabel.setText(str(self.slider_2.value() * 0.01))
        self.sliderUpdateSignal.emit(self.currentMode, self.slider_2.value())
        # self.slider_2.setStyleSheet(overShootSliderStyleSheet.format(stop=self.slider_2.value() * 0.1))

    def sliderPressed(self):
        self.sliderBeginSignal.emit(self.currentMode, self.slider_2.value())
        self.isDragging = True

    def restoreSlider(self):
        self.slider_2.setEnabled(True)
        self.isCancelled = False

    def sliderReleased(self, cancel=False):
        if cancel:
            self.isCancelled = True
            self.sliderCancelSignal.emit()
            click_pos = QPoint(0, 0)
            event = QMouseEvent(QEvent.MouseButtonPress,
                                click_pos,
                                Qt.MouseButton.LeftButton,
                                Qt.MouseButton.LeftButton,
                                Qt.Modifier)
            QApplication.instance().sendEvent(self, event)
            self.slider_2.setEnabled(False)
            # self.slider_2.clearFocus()
            # self.setFocus()
            # self.update()
            self.slider_2.setSliderDown(False)
            # self.slider_2.setEnabled(True)
        else:
            self.sliderEndedSignal.emit(self.currentMode, self.slider_2.value())
        self.isDragging = False
        self.slider_2.resetStyle()
        self.resetValues()

    def resetValues(self):
        # self.overlayLabel.setText('')
        self.slider_2.blockSignals(True)
        self.slider_2.setValue(0)
        self.slider_2.blockSignals(False)
        self.overlayLabel.hide()

    def sliderWheelUpdate(self):
        if not self.isDragging:
            self.sliderUpdateSignal.emit(self.currentMode, self.slider_2.value())
            self.sliderValueChanged()

    def modeChanged(self, *args):
        self.currentMode = self.comboBox.currentText()
        self.modeChangedSignal.emit(self.currentMode)

    def toggleOvershoot(self, overshootState):
        self.slider_2.toggleOvershoot(overshootState)
        currentPos = self.pos()
        if overshootState:
            self.slider_2.setFixedWidth(self.baseSliderWidth * 2)
            self.setFixedWidth((self.baseWidth - self.baseSliderWidth) + (self.baseSliderWidth * 2))
            currentPos.setX(currentPos.x() - (self.baseSliderWidth * 0.5))
        else:
            self.slider_2.setFixedWidth(self.baseSliderWidth)
            self.setFixedWidth(self.baseWidth)

            currentPos.setX(currentPos.x() + (self.baseSliderWidth * 0.5))
        self.move(currentPos)


class XformSliderWidget(SliderWidget):
    __instance = None
    recentlyOpened = False

    '''
    def __new__(cls):
        if XformSliderWidget.__instance is None:
            if cmds.about(version=True) == '2022':
                XformSliderWidget.__instance = BaseDialog.__new__(cls)
            else:
                if QTVERSION < 5:
                    XformSliderWidget.__instance = BaseDialog.__new__(cls)
                else:
                    XformSliderWidget.__instance = object.__new__(cls)

        XformSliderWidget.__instance.val = 'XformSliderWidget'
        XformSliderWidget.__instance.app = QApplication.instance()
        return XformSliderWidget.__instance
    '''
    def __init__(self, parent=wrapInstance(int(omUI.MQtUtil.mainWindow()), QWidget),
                 title='Object Inbetween',
                 text='test',
                 showLockButton=True, showCloseButton=False,
                 modeList=['Local', 'World'],

                 ):
        super(XformSliderWidget, self).__init__(parent=parent,
                                                title=title,
                                                text=title,
                                                showLockButton=showLockButton, showCloseButton=showCloseButton,
                                                modeList=modeList,
                                                baseLabel='All attributes',
                                                shiftLabel='Translate Only',
                                                controlLabel='Rotate Only',
                                                controlShiftLabel='Translate And Rotate Only',
                                                altLabel='ChannelBox Only'
                                                )
        self.recentlyOpened = False


class KeySliderWidget(SliderWidget):
    __instance = None
    '''
    def __new__(cls):
        if KeySliderWidget.__instance is None:
            if cmds.about(version=True) == '2022':
                KeySliderWidget.__instance = BaseDialog.__new__(cls)
            else:
                if QTVERSION < 5:
                    KeySliderWidget.__instance = BaseDialog.__new__(cls)
                else:
                    KeySliderWidget.__instance = object.__new__(cls)

        KeySliderWidget.__instance.val = 'KeySliderWidget'
        KeySliderWidget.__instance.app = QApplication.instance()
        return KeySliderWidget.__instance
    '''
    def __init__(self, parent=wrapInstance(int(omUI.MQtUtil.mainWindow()), QWidget),
                 title='Key Inbetween',
                 text='test',
                 showLockButton=True, showCloseButton=False,
                 modeList=SlideTools().keyTweenMethods.keys(),
                 showInfo=False,

                 ):
        super(KeySliderWidget, self).__init__(parent=parent,
                                              title=title,
                                              text=title,
                                              showLockButton=showLockButton, showCloseButton=showCloseButton,
                                              modeList=modeList,
                                              baseLabel='All attributes',
                                              shiftLabel='Translate Only',
                                              controlLabel='Rotate Only',
                                              controlShiftLabel='Translate And Rotate Only',
                                              altLabel='ChannelBox Only',
                                              showInfo=showInfo
                                              )
        self.recentlyOpened = False
        self.setFixedSize(270, 46)


class GraphEdKeySliderWidget(QWidget):
    __instance = None
    # call the tween classes by name, send value
    sliderUpdateSignal = Signal(str, float)
    sliderEndedSignal = Signal(str, float)
    sliderBeginSignal = Signal(str, float)
    modeChangedSignal = Signal(str)
    sliderCancelSignal = Signal()

    minValue = -101
    minOvershootValue = -201
    maxValue = 101
    maxOvershootValue = 201
    baseSliderWidth = 160
    baseWidth = 240

    baseLabel = 'baseLabel'
    shiftLabel = 'shiftLabel'
    controlLabel = 'controlLabel'
    controlShiftLabel = 'controlShiftLabel'
    altLabel = 'altLabel'
    labelYOffset = 16

    def __init__(self, parent=wrapInstance(int(omUI.MQtUtil.mainWindow()), QWidget),
                 title='Key Inbetween',
                 text='test',
                 showLockButton=True, showCloseButton=False,
                 modeList=SlideTools().keyTweenMethods.keys(),
                 showInfo=False,

                 ):
        super(GraphEdKeySliderWidget, self).__init__()
        self.isCancelled = False
        self.recentlyOpened = False
        self.invokedKey = None
        self.modeList = modeList
        #
        # labels
        '''
        self.baseLabel = baseLabel
        self.shiftLabel = shiftLabel
        self.controlLabel = controlLabel
        self.controlShiftLabel = controlShiftLabel
        self.altLabel = altLabel
        '''
        # self.setWindowFlags(Qt.PopupFocusReason | Qt.Tool | Qt.FramelessWindowHint)
        # self.setAttribute(Qt.WA_StyledBackground, True)
        # self.autoFillBackground = True
        # self.windowFlags()
        # self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setFixedHeight(24)

        self.isDragging = False

        self.container = QFrame()
        self.container.setStyleSheet("QFrame {{ background-color: #343b48; color: #8a95aa; }}")

        self.slider = PySlider()
        self.slider.setOrientation(Qt.Horizontal)
        self.slider.setFixedWidth(self.baseSliderWidth)
        self.slider.setMinimum(-101)
        self.slider.setMaximum(101)
        self.slider.setValue(0)
        self.slider.setTickInterval(1)

        self.slider.sliderPressed.connect(self.sliderPressed)
        self.slider.sliderMoved.connect(self.sliderValueChanged)
        self.slider.sliderMoved.connect(self.slider.sliderMovedEvent)
        self.slider.wheelSignal.connect(self.sliderWheelUpdate)
        self.slider.sliderReleased.connect(self.sliderReleased)
        self.slider.sliderReleased.connect(self.slider.sliderReleasedEvent)

        self.mainLayout = QHBoxLayout()
        self.mainLayout.setSpacing(0)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.mainLayout)
        self.mainLayout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        self.comboBox = QComboBox()
        self.comboBox.setStyleSheet(getqss.getStyleSheet())
        self.overshootButton = LockButton('', self, icon='overshootOn.png',
                                          unlockIcon='overshoot.png', )
        self.overshootButton.lockSignal.connect(self.toggleOvershoot)

        for c in self.modeList:
            self.comboBox.addItem(c)
        self.currentMode = self.comboBox.currentText()
        self.comboBox.currentIndexChanged.connect(self.modeChanged)
        width = self.comboBox.minimumSizeHint().width()
        self.comboBox.view().setMinimumWidth(width)
        self.comboBox.setMinimumWidth(width + self.labelYOffset)
        self.comboBox.setMaximumWidth(width + self.labelYOffset)
        # self.resize(self.sizeHint())

        # emit the mode change signal to load the labels
        self.modeChangedSignal.emit(self.currentMode)

        self.mainLayout.addWidget(self.slider)
        self.mainLayout.setAlignment(Qt.AlignLeft)
        self.mainLayout.addWidget(self.overshootButton)
        self.mainLayout.addWidget(self.comboBox)
        self.overlayLabel = QLabel('', self)
        self.overlayLabel.setStyleSheet("background: rgba(255, 0, 0, 0); color : rgba(255, 255, 255, 168)")
        self.overlayLabel.setEnabled(False)
        self.overlayLabel.setFixedWidth(60)
        self.overlayLabel.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.labelYPos = 6
        self.overlayLabel.setAlignment(Qt.AlignLeft)
        self.overlayLabel.move(10, self.labelYPos)
        self.setFocusPolicy(Qt.NoFocus)

    def show(self):
        super(GraphEdKeySliderWidget, self).show()
        self.resetValues()
        self.setEnabled(True)
        self.setFocus()
        self.recentlyOpened = True

    def moveToCursor(self):
        pos = QCursor.pos()
        xOffset = 10  # border?
        self.move(pos.x() - (self.width() * 0.5), pos.y() - (self.height() * 0.5) - 12)


    def modifierReleased(self):
        return
        self.infoText.setText(self.baseLabel)

    def controlReleased(self):
        return
        self.infoText.setText(self.baseLabel)

    def controlPressed(self):
        return
        self.infoText.setText(self.controlLabel)

    def controlShiftPressed(self):
        return
        self.infoText.setText(self.controlShiftLabel)

    def shiftPressed(self):
        return
        self.infoText.setText(self.shiftLabel)

    def altPressed(self):
        return
        self.infoText.setText(self.altLabel)

    def mousePressEvent(self, event):
        # print ("Mouse Clicked", event.buttons(), event.button() == Qt.RightButton)
        if event.button() == Qt.RightButton:
            self.sliderReleased(cancel=True)
        if event.button() == Qt.LeftButton:
            self.restoreSlider()

    def sliderValueChanged(self):
        if self.slider.value() > self.slider.maximum() * 0.6:
            self.overlayLabel.move(10, self.labelYPos)
            self.overlayLabel.setAlignment(Qt.AlignLeft)
        elif self.slider.value() < self.slider.minimum() * 0.6:
            self.overlayLabel.move(self.slider.width() - self.overlayLabel.width() - 10, self.labelYPos)
            self.overlayLabel.setAlignment(Qt.AlignRight)

        self.overlayLabel.setText(str(self.slider.value() * 0.01))
        self.sliderUpdateSignal.emit(self.currentMode, self.slider.value())
        # self.slider_2.setStyleSheet(overShootSliderStyleSheet.format(stop=self.slider_2.value() * 0.1))

    def sliderPressed(self):
        self.sliderBeginSignal.emit(self.currentMode, self.slider.value())
        self.isDragging = True
        self.overlayLabel.show()

    def restoreSlider(self):
        self.slider.setEnabled(True)
        self.isCancelled = False

    def sliderReleased(self, cancel=False):
        if cancel:
            self.isCancelled = True
            self.sliderCancelSignal.emit()
            click_pos = QPoint(0, 0)
            event = QMouseEvent(QEvent.MouseButtonPress,
                                click_pos,
                                Qt.MouseButton.LeftButton,
                                Qt.MouseButton.LeftButton,
                                Qt.Modifier)
            QApplication.instance().sendEvent(self, event)
            self.slider.setEnabled(False)
            # self.slider_2.clearFocus()
            # self.setFocus()
            # self.update()
            self.slider.setSliderDown(False)
            # self.slider_2.setEnabled(True)
        else:
            self.sliderEndedSignal.emit(self.currentMode, self.slider.value())
        self.isDragging = False
        self.slider.resetStyle()
        self.resetValues()

    def resetValues(self):
        # self.overlayLabel.setText('')
        self.slider.blockSignals(True)
        self.slider.setValue(0)
        self.slider.blockSignals(False)
        self.overlayLabel.hide()

    def sliderWheelUpdate(self):
        if not self.isDragging:
            self.sliderUpdateSignal.emit(self.currentMode, self.slider.value())
            self.sliderValueChanged()

    def modeChanged(self, *args):
        self.currentMode = self.comboBox.currentText()
        self.modeChangedSignal.emit(self.currentMode)

    def toggleOvershoot(self, overshootState):
        self.slider.toggleOvershoot(overshootState)
        currentPos = self.pos()


class SliderButtonPopup(ButtonPopup):
    def __init__(self, name, parent=None):
        super(ButtonPopup, self).__init__(parent)

        self.setWindowTitle("{0} Options".format(name))

        self.setWindowFlags(Qt.Popup)

        self.layout = QFormLayout(self)

        self.create_widgets()
        self.create_layout()

    def create_widgets(self):
        self.radioGroup = radioGroupVertical(formLayout=self.layout,
                                             tooltips=['y_tb_AdjustmentBlend.kSimple',
                                                       'y_tb_AdjustmentBlend.kIgnore',
                                                       'y_tb_AdjustmentBlend.kStart',
                                                       'y_tb_AdjustmentBlend.kEnd'],
                                             optionVarList=['y_tb_AdjustmentBlend.kSimple',
                                                            'y_tb_AdjustmentBlend.kIgnore',
                                                            'y_tb_AdjustmentBlend.kStart',
                                                            'y_tb_AdjustmentBlend.kEnd'],
                                             optionVar='test_variable',
                                             defaultValue="Simple",
                                             label=str())

    def create_layout(self):
        tbAdjustmentBlendLabel = QLabel('tbAdjustmentBlend')
        rootOptionLabel = QLabel('Global control options')
        self.layout.addRow(tbAdjustmentBlendLabel)
        self.layout.addRow(rootOptionLabel)
        for label, widget in self.radioGroup.returnedWidgets:
            self.layout.addRow(widget)
        # layout.addRow("Size:", self.size_sb)
        # layout.addRow("Opacity:", self.opacity_sb)
