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
import maya.mel as mel
import maya.cmds as cmds
import maya.api.OpenMaya as om2
import maya.api.OpenMayaAnim as oma2
import pymel.core.datatypes as dt
import math
from Abstract import *
from tb_UI import *
import tb_helpStrings
import maya
import traceback

maya.utils.loadStringResourcesForModule(__name__)
qtVersion = pm.about(qtVersion=True)
if int(qtVersion.split('.')[0]) < 5:
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

assetCommandName = 'tempControlCommand'


class hotkeys(hotKeyAbstractFactory):
    def createHotkeyCommands(self):
        self.commandList = list()
        self.setCategory(self.helpStrings.category.get('layers'))
        self.addCommand(self.tb_hkey(name='quickMergeAllLayers',
                                     annotation='Merges all layers',
                                     category=self.category,
                                     command=['BakeTools.quickMergeAllLayers()'],
                                     help=maya.stringTable['tbCommand.quickMergeAllLayers']))

        self.addCommand(self.tb_hkey(name='quickMergeSelectionToNew',
                                     annotation='',
                                     category=self.category,
                                     command=['BakeTools.quickMergeSelectionToNew()'],
                                     help=maya.stringTable['tbCommand.quickMergeSelectionToNew']))

        self.addCommand(self.tb_hkey(name='quickMergeSelectionToBase',
                                     annotation='',
                                     category=self.category,
                                     command=['BakeTools.quickMergeSelectionToBase()'],
                                     help=maya.stringTable['tbCommand.quickMergeSelectionToBase']))

        self.addCommand(self.tb_hkey(name='bakeConstraintToAdditive',
                                     annotation='',
                                     category=self.category,
                                     command=['BakeTools.bakeConstraintToAdditiveSelection()'],
                                     help=maya.stringTable['tbCommand.bakeConstraintToAdditive']))
        self.addCommand(self.tb_hkey(name='additiveExtractSelection',
                                     annotation='',
                                     category=self.category,
                                     command=['BakeTools.additiveExtractSelection()'],
                                     help=maya.stringTable['tbCommand.additiveExtractSelection']))

        self.addCommand(self.tb_hkey(name='simpleBakeToOverride',
                                     annotation='',
                                     category=self.category,
                                     command=['BakeTools.bake_to_override()'],
                                     help=maya.stringTable['tbCommand.simpleBakeToOverride']))
        self.addCommand(self.tb_hkey(name='simpleBakeToOverride_2s',
                                     annotation='',
                                     category=self.category,
                                     command=['BakeTools.bake_to_override(sampleRate=2)'],
                                     help=maya.stringTable['tbCommand.simpleBakeToOverride']))
        self.addCommand(self.tb_hkey(name='simpleBakeToOverride_3s',
                                     annotation='',
                                     category=self.category,
                                     command=['BakeTools.bake_to_override(sampleRate=3)'],
                                     help=maya.stringTable['tbCommand.simpleBakeToOverride']))
        self.addCommand(self.tb_hkey(name='simpleBakeToOverride_4s',
                                     annotation='',
                                     category=self.category,
                                     command=['BakeTools.bake_to_override(sampleRate=4)'],
                                     help=maya.stringTable['tbCommand.simpleBakeToOverride']))
        self.addCommand(self.tb_hkey(name='simpleBakeToOverride_5s',
                                     annotation='',
                                     category=self.category,
                                     command=['BakeTools.bake_to_override(sampleRate=5)'],
                                     help=maya.stringTable['tbCommand.simpleBakeToOverride']))
        self.addCommand(self.tb_hkey(name='simpleBakeToOverride_x',
                                     annotation='',
                                     category=self.category,
                                     command=['BakeTools.bakeOnXUI()'],
                                     help=maya.stringTable['tbCommand.simpleBakeToOverride']))

        self.addCommand(self.tb_hkey(name='simpleBakeToBase',
                                     annotation='',
                                     category=self.category,
                                     command=['BakeTools.simpleBake()'],
                                     help=maya.stringTable['tbCommand.simpleBakeToBase']))

        self.addCommand(self.tb_hkey(name='quickCreateAdditiveLayer',
                                     annotation='',
                                     category=self.category,
                                     command=['BakeTools.addAdditiveLayer()'],
                                     help=maya.stringTable['tbCommand.quickCreateAdditiveLayer']))
        self.addCommand(self.tb_hkey(name='quickCreateAdditiveLayer_Component',
                                     annotation='',
                                     category=self.category,
                                     command=['BakeTools.addAdditiveLayer(component=False)'],
                                     help=maya.stringTable['tbCommand.quickCreateAdditiveLayer']))
        self.addCommand(self.tb_hkey(name='quickCreateOverrideLayer',
                                     annotation='',
                                     category=self.category,
                                     command=['BakeTools.addOverrideLayer()'],
                                     help=maya.stringTable['tbCommand.quickCreateOverrideLayer']))

        self.addCommand(self.tb_hkey(name='counterAnimLayer',
                                     annotation='',
                                     category=self.category,
                                     command=['BakeTools.counterLayerAnimation()'],
                                     help=maya.stringTable['tbCommand.counterAnimLayer']))

        self.setCategory(self.helpStrings.category.get('constraints'))
        self.addCommand(self.tb_hkey(name='simpleConstraintOffset',
                                     annotation='constrain to objects with offset',
                                     category=self.category,
                                     command=[
                'BakeTools.parentConst(constrainGroup=False, offset=True, postBake=False)'],
                                     help=maya.stringTable['tbCommand.simpleConstraintOffset']))
        self.addCommand(self.tb_hkey(name='simpleConstraintNoOffset',
                                     annotation='constrain to objects with NO offset',
                                     category=self.category,
                                     command=[
                'BakeTools.parentConst(constrainGroup=False, offset=False, postBake=False)'],
                                     help=maya.stringTable['tbCommand.simpleConstraintNoOffset']))
        self.addCommand(self.tb_hkey(name='simpleConstraintOffsetPostBake',
                                     annotation='constrain to objects with offset - post baked',
                                     category=self.category,
                                     command=[
                'BakeTools.parentConst(constrainGroup=False, offset=True, postBake=True)'],
                                     help=maya.stringTable['tbCommand.simpleConstraintOffsetPostBake']))

        self.addCommand(self.tb_hkey(name='simpleConstraintNoOffsetPostBake',
                                     annotation='constrain to objects with NO offset - post baked',
                                     category=self.category,
                                     command=[
                'BakeTools.parentConst(constrainGroup=False, offset=False, postBake=True)'],
                                     help=maya.stringTable['tbCommand.simpleConstraintNoOffsetPostBake']))

        self.addCommand(self.tb_hkey(name='simpleConstraintOffsetPostBakeReverse',
                                     annotation='constrain to objects with offset - post baked, constraint reversed',
                                     category=self.category,
                                     command=[
                'BakeTools.parentConst(constrainGroup=False, offset=True, postBake=True, postReverseConst=True)'],
                                     help=maya.stringTable['tbCommand.simpleConstraintOffsetPostBakeReverse']))

        self.addCommand(self.tb_hkey(name='simpleConstraintNoOffsetPostBakeReverse',
                                     annotation='constrain to objects with NO offset - post baked, constraint reversed',
                                     category=self.category,
                                     command=[
                'BakeTools.parentConst(constrainGroup=False, offset=False, postBake=True, postReverseConst=True)'],
                                     help=maya.stringTable['tbCommand.simpleConstraintNoOffsetPostBakeReverse']))

        self.addCommand(self.tb_hkey(name='bakeOutSelectedTempControls',
                                     annotation='right click menu for temp controls',
                                     category=self.category,
                                     command=['BakeTools.bakeSelectedHotkey()'],
                                     help=maya.stringTable['tbCommand.kbakeOutSelected']))
        self.addCommand(self.tb_hkey(name='bakeOutAllTempControls',
                                     annotation='right click menu for temp controls',
                                     category=self.category,
                                     command=['BakeTools.bakeAllHotkey()'],
                                     help=maya.stringTable['tbCommand.kbakeOutAll']))
        self.addCommand(self.tb_hkey(name='removeAllTempControls',
                                     annotation='right click menu for temp controls',
                                     category=self.category,
                                     command=['BakeTools.removeAllHotkey()'],
                                     help=maya.stringTable['tbCommand.kremoveAll']))

        self.setCategory(self.helpStrings.category.get('TempControls'))
        self.addCommand(self.tb_hkey(name='bakeToLocator',
                                     annotation='',
                                     category=self.category,
                                     command=['BakeTools.bake_to_locator(constrain=True, orientOnly=False)'],
                                     help=maya.stringTable['tbCommand.bakeToLocator']))
        self.addCommand(self.tb_hkey(name='bakeToLocatorPinned',
                                     annotation='',
                                     category=self.category,
                                     command=['BakeTools.bake_to_locator_pinned(constrain=True, orientOnly=False)'],
                                     help=maya.stringTable['tbCommand.bakeToLocator']))
        self.addCommand(self.tb_hkey(name='bakeToLocatorRotation',
                                     annotation='constrain to object to locator - rotate only',
                                     category=self.category,
                                     command=['BakeTools.bake_to_locator(constrain=True, orientOnly=True)'],
                                     help=maya.stringTable['tbCommand.bakeToLocatorRotation']))
        self.addCommand(self.tb_hkey(name='redirectSelected',
                                     annotation='constrain to object to locator - rotate only',
                                     category=self.category,
                                     command=['BakeTools.redirectSelected()'],
                                     help=maya.stringTable['tbCommand.redirectSelected']))
        self.addCommand(self.tb_hkey(name='worldOffsetSelection',
                                     annotation='worldOffsetSelection',
                                     category=self.category,
                                     command=['BakeTools.worldOffsetSelection()'],
                                     help=maya.stringTable['tbCommand.worldOffsetSelection']))
        self.addCommand(self.tb_hkey(name='worldOffsetSelectionRotation',
                                     annotation='worldOffsetSelection',
                                     category=self.category,
                                     command=['BakeTools.worldOffsetSelectionRotation()'],
                                     help=maya.stringTable['tbCommand.worldOffsetSelectionRotation']))

        self.setCategory(self.helpStrings.category.get('ignore'))
        self.addCommand(self.tb_hkey(name=assetCommandName,
                                     annotation='right click menu for temp controls',
                                     category=self.category,
                                     command=['BakeTools.assetRmbCommand()'],
                                     help='Do not assign to a hotkey'))

        return self.commandList

    def assignHotkeys(self):
        return


class BakeTools(toolAbstractFactory):
    """
    Use this as a base for toolAbstractFactory classes
    """
    # __metaclass__ = abc.ABCMeta
    __instance = None
    toolName = 'BakeTools'
    hotkeyClass = hotkeys()
    funcs = functions()

    quickBakeSimOption = 'tbQuickBakeUseSim'

    quickBakeRemoveContainerOption = 'tbQuickBakeRemoveContainer'
    tbTempControlMotionTrailOption = 'tbTempControlMotionTrailOption'
    tbTempControlChannelOption = 'tbTempControlChannelOption'
    tbBakeSimObjectCountOption = 'tbBakeSimObjectCountOption'
    tbBakeLocatorSizeOption = 'tbBakeLocatorSize'
    tbBakeWorldOffsetSizeOption = 'tbBakeWorldOffsetSize'
    tbMotionControlSizeOption = 'tbMotionControlSize'

    overrideLayerColour = 19
    additiveLayerColour = 18

    assetCommandName = 'tempControlCommand'

    assetName = 'TempControls'
    worldOffsetAssetName = 'WorldOffsetControls'
    constraintTargetAttr = 'constraintTarget'
    tempControlPairAttr = 'tempControlPair'

    def __new__(cls):
        if BakeTools.__instance is None:
            BakeTools.__instance = object.__new__(cls)

        BakeTools.__instance.val = cls.toolName
        return BakeTools.__instance

    def __init__(self):
        self.hotkeyClass = hotkeys()
        self.funcs = functions()

    """
    Declare an interface for operations that create abstract product
    objects.
    """

    def optionUI(self):
        super(BakeTools, self).optionUI()
        topFormLayout = QFormLayout()
        bookendOptionWidget = optionVarBoolWidget('Bookend layer weight when baking to layer ', self.bookendBakeOption)
        bookendHighlightOptionWidget = optionVarBoolWidget(
            'Bookend layer weight when baking to layer\nWith the timeslider highlighted ',
            self.bookendBakeHighlightOption)
        simOptionWidget = optionVarBoolWidget('Bake to locator uses Simulation ', self.quickBakeSimOption)
        containerOptionWidget = optionVarBoolWidget('Remove containers post bake     ',
                                                    self.quickBakeRemoveContainerOption)

        crossSizeWidget = intFieldWidget(optionVar=self.tbBakeLocatorSizeOption,
                                         defaultValue=1.0,
                                         label='Baked locator control size',
                                         minimum=0.1, maximum=100, step=0.1)
        worldOffsetSizeWidget = intFieldWidget(optionVar=self.tbBakeWorldOffsetSizeOption,
                                               defaultValue=0.5,
                                               label='World offset control size',
                                               minimum=0.1, maximum=100, step=0.1)

        # motionControlSizeWidget.changedSignal.connect(self.updatePreview)
        crossSizeWidget.changedSignal.connect(self.updatePreview)
        worldOffsetSizeWidget.changedSignal.connect(self.updatePreview)

        constraintChannelHeader = subHeader('Constraint Channels')
        constraintChannelInfo = infoLabel([
            'Turn this option on to make the bake to temp control functions only constrain up the highlighted channelBox attributes.'])
        constraintChannelWidget = optionVarBoolWidget('Constrain Highlighted Channels',
                                                      self.tbTempControlChannelOption)

        tempControlHeader = subHeader('Bake Simulation')
        tempControlInfo = infoLabel(['When baking many objects it is often faster to use simulation.',
                                     'Experiment to see where the threshold lies on your machine. Set the value below to automatically toggle bake sim when baking many objects'])

        bakeSimThresholdWidget = intFieldWidget(optionVar=self.tbBakeSimObjectCountOption,
                                                defaultValue=10,
                                                label='Bake Simulation when baking more than > objects',
                                                minimum=1, maximum=100, step=1)
        motionTrailHeader = subHeader('Motion Trails')
        motionTrailInfo = infoLabel(['Add motion trails to newly created temp controls.'])
        motionTrailWidget = optionVarBoolWidget('Motion Trail On Temp Controls',
                                                self.tbTempControlMotionTrailOption)

        self.layout.addLayout(topFormLayout)
        self.layout.addWidget(bookendOptionWidget)
        self.layout.addWidget(bookendHighlightOptionWidget)
        self.layout.addWidget(simOptionWidget)
        self.layout.addWidget(containerOptionWidget)
        self.layout.addWidget(crossSizeWidget)
        self.layout.addWidget(worldOffsetSizeWidget)
        topFormLayout.addRow(bookendOptionWidget.labelText, bookendOptionWidget)
        topFormLayout.addRow(bookendHighlightOptionWidget.labelText, bookendHighlightOptionWidget)
        topFormLayout.addRow(simOptionWidget.labelText, simOptionWidget)
        topFormLayout.addRow(containerOptionWidget.labelText, containerOptionWidget)
        topFormLayout.addRow(crossSizeWidget.label, crossSizeWidget)
        # self.layout.addWidget(motionControlSizeWidget)
        topFormLayout.addRow(worldOffsetSizeWidget.label, worldOffsetSizeWidget)

        self.layout.addWidget(constraintChannelHeader)
        self.layout.addWidget(constraintChannelInfo)
        self.layout.addWidget(constraintChannelWidget)

        self.layout.addWidget(tempControlHeader)
        self.layout.addWidget(tempControlInfo)
        self.layout.addWidget(bakeSimThresholdWidget)
        self.layout.addWidget(motionTrailHeader)
        self.layout.addWidget(motionTrailInfo)
        self.layout.addWidget(motionTrailWidget)
        self.layout.addStretch()
        return self.optionWidget

    def showUI(self):
        return cmds.warning(self, 'optionUI', ' function not implemented')

    def drawMenuBar(self, parentMenu):
        return None

    """
    Functions
    """

    def drawPreview(self):
        self.funcs.tempControl(name='temp',
                               suffix='Preview',
                               scale=pm.optionVar.get(self.tbBakeLocatorSizeOption, 1),
                               drawType='cross')

    def updatePreview(self, scale):
        if not cmds.objExists('temp_Preview'):
            self.drawPreview()

        cmds.setAttr('temp_Preview.scaleX', scale)
        cmds.setAttr('temp_Preview.scaleY', scale)
        cmds.setAttr('temp_Preview.scaleZ', scale)

    def getBestTimelineRangeForBake(self, sel=list(), keyRange=None):
        timelineRange = self.funcs.getTimelineRange()
        isHighlighted = self.funcs.isTimelineHighlighted()
        keyRange = [timelineRange[0], timelineRange[1]]
        if isHighlighted:
            minTime, maxTime = self.funcs.getTimelineHighlightedRange()
            keyRange = [minTime, maxTime]
        '''
        if not keyRange:
            print ('keyRange', keyRange)
            isHighlighted = self.funcs.isTimelineHighlighted()
            if isHighlighted:
                minTime, maxTime = self.funcs.getTimelineHighlightedRange()
                keyRange = [minTime, maxTime]
            else:
                keyRange = self.funcs.get_all_layer_key_times(sel)
                if not keyRange or keyRange[0] == None:
                    keyRange = timelineRange
                self.expandKeyRangeToTimelineRange(keyRange, timelineRange)
        '''
        return keyRange

    def bake_to_override(self, sampleRate=1, sel=None, layerPrefix='', keyRange=None, deleteConstraints=True,
                         bookend=True):
        print('THIS')
        print('keyRange', keyRange)
        highlighted = self.funcs.isTimelineHighlighted()
        if not sel:
            sel = cmds.ls(sl=True)
        if not sel:
            return
        with self.funcs.undoChunk():
            with self.funcs.keepSelection():
                preContainers = set(pm.ls(type='container'))
                preBakeLayers = pm.ls(type='animLayer')
                keyRange = self.funcs.getBestTimelineRangeForBake(sel, keyRange=keyRange)
                newAnimLayer = pm.animLayer('resultLayerBLANKNAME', override=True, passthrough=True)

                pm.bakeResults(sel,
                               time=(keyRange[0], keyRange[-1]),
                               destinationLayer=str(newAnimLayer),
                               simulation=False,
                               sampleBy=1,
                               oversamplingRate=1,
                               disableImplicitControl=True,
                               preserveOutsideKeys=False,
                               sparseAnimCurveBake=True,
                               removeBakedAttributeFromLayer=False,
                               removeBakedAnimFromLayer=False,
                               bakeOnOverrideLayer=True,
                               minimizeRotation=True,
                               controlPoints=False,
                               shape=False)

                pm.setAttr(newAnimLayer + ".ghostColor", self.overrideLayerColour)
                pm.rename(newAnimLayer, layerPrefix + 'OverrideBaked')

                if deleteConstraints:
                    if not isinstance(sel, list):
                        sel = [sel]
                    for n in sel:
                        n = str(n)
                        self.deleteConstraintsForNode(n)
                        self.clearBlendAttrs(n)

                self.removeContainersPostBake(preContainers)
            self.funcs.select_layer(str(newAnimLayer))

            if sampleRate != 1:
                self.resampleLayer(str(newAnimLayer), sampleRate, startTime=keyRange[0], endTime=keyRange[-1])
            if not highlighted:
                print('Not highlighted')
                # timeline isn't highlighted, do we bookend the weight anyway?
                if pm.optionVar.get(self.bookendBakeOption, False):
                    print('bookend')
                    self.funcs.bookEndLayerWeight(str(newAnimLayer), keyRange[0], keyRange[-1])
            else:
                print('highlighted')
                # timeline is highlighted, do we bookend the weight for "convenience"?
                if pm.optionVar.get(self.bookendBakeHighlightOption, False):
                    print('bookend')
                    self.funcs.bookEndLayerWeight(str(newAnimLayer), keyRange[0], keyRange[-1])

            cmds.refresh()

    def deleteConstraintsForNode(self, n):
        n = str(n)
        constraints = cmds.listRelatives(n, type='constraint')
        if constraints:
            cmds.delete(constraints)

    def simpleBake(self, sel=None):
        if not sel:
            sel = cmds.ls(sl=True)
        if not sel:
            return
        with self.funcs.keepSelection():
            keyRange = self.funcs.getBestTimelineRangeForBake(sel)
            pm.bakeResults(sel,
                           time=(keyRange[0], keyRange[-1]),
                           simulation=False,
                           sampleBy=1,
                           oversamplingRate=1,
                           disableImplicitControl=True,
                           preserveOutsideKeys=False,
                           sparseAnimCurveBake=True,
                           removeBakedAttributeFromLayer=False,
                           removeBakedAnimFromLayer=False,
                           bakeOnOverrideLayer=False,
                           minimizeRotation=True,
                           controlPoints=False,
                           shape=False)

    def removeContainersPostBake(self, preContainers):
        if pm.optionVar.get(self.quickBakeRemoveContainerOption, False):
            resultContainer = list(set(pm.ls(type='container')).difference(set(preContainers)))
            if not resultContainer:
                return
            pm.select(resultContainer, replace=True)
            mel.eval('SelectContainerContents')
            mel.eval('doRemoveFromContainer(1, {"container -e -includeShapes -includeTransform "})')
            pm.delete(resultContainer)

    def bake_to_locator(self, sel=list(), constrain=False, orientOnly=False, select=True, skipMotionTrails=False):
        if not sel:
            sel = pm.ls(sl=True)
        locs = []
        constraints = []
        with self.funcs.suspendUpdate():
            try:
                if sel:
                    for s in sel:
                        # loc = self.funcs.tempLocator(name=s, suffix='baked')
                        ps = pm.PyNode(s)
                        ns = ps.namespace()
                        if not cmds.objExists(ns + self.assetName):
                            self.createAsset(ns + self.assetName, imageName=None)
                        asset = ns + self.assetName
                        loc = self.funcs.tempControl(name=s, suffix='baked', drawType='cross',
                                                     scale=pm.optionVar.get(self.tbBakeLocatorSizeOption, 1))
                        pm.addAttr(loc, ln=self.constraintTargetAttr, at='message')
                        pm.connectAttr(s + '.message', loc + '.' + self.constraintTargetAttr)
                        const = pm.parentConstraint(s, loc)
                        locs.append(loc)
                        constraints.append(const)
                        pm.container(asset, edit=True,
                                     includeHierarchyBelow=True,
                                     force=True,
                                     addNode=loc)
                if locs:
                    preContainers = set(pm.ls(type='container'))
                    keyRange = self.funcs.getBestTimelineRangeForBake()
                    pm.bakeResults(locs,
                                   simulation=pm.optionVar.get(self.quickBakeSimOption, False),
                                   sampleBy=1,
                                   oversamplingRate=1,
                                   disableImplicitControl=True,
                                   preserveOutsideKeys=False,
                                   sparseAnimCurveBake=True,
                                   removeBakedAttributeFromLayer=False,
                                   removeBakedAnimFromLayer=False,
                                   bakeOnOverrideLayer=False,
                                   minimizeRotation=True,
                                   controlPoints=False,
                                   shape=False,
                                   time=[keyRange[0],
                                         keyRange[1]],
                                   )
                    self.removeContainersPostBake(preContainers)
                    if constrain:
                        pm.delete(constraints)
                        for cnt, loc in zip(sel, locs):
                            skipT = self.funcs.getAvailableTranslates(cnt)
                            skipR = self.funcs.getAvailableRotates(cnt)
                            constraint = pm.parentConstraint(loc, cnt, skipTranslate={True: ('x', 'y', 'z'),
                                                                                      False: [x.split('translate')[-1]
                                                                                              for x in
                                                                                              skipT]}[
                                orientOnly],
                                                             skipRotate=[x.split('rotate')[-1] for x in skipR])
                            pm.container(asset, edit=True,
                                         includeHierarchyBelow=True,
                                         force=True,
                                         addNode=constraint)
                if pm.optionVar.get(self.tbTempControlMotionTrailOption, False):
                    if not skipMotionTrails:
                        for l in locs:
                            cmds.select(str(l), replace=True)
                            mel.eval('createMotionTrail')
                if select:
                    pm.select(locs, replace=True)
                return locs
            except Exception:
                cmds.warning(traceback.format_exc())
                self.funcs.resumeSkinning()

    def bake_to_locator_pinned(self, sel=list(), constrain=False, orientOnly=False, select=True,
                               skipMotionTrails=False):
        """
        Bake selected  controls to last selected one
        :param sel:
        :param constrain:
        :param orientOnly:
        :param select:
        :param skipMotionTrails:
        :return:
        """
        if not sel:
            sel = pm.ls(sl=True)
        locs = []
        constraints = []
        if not sel:
            return
        controls = sel[:-1]
        target = sel[-1]

        with self.funcs.suspendUpdate():
            try:
                parentNode = self.funcs.tempNull(name=target, suffix='baked')

                ps = pm.PyNode(parentNode)
                ns = ps.namespace()
                if not cmds.objExists(ns + self.assetName):
                    self.createAsset(ns + self.assetName, imageName=None)
                asset = ns + self.assetName

                constraint = pm.parentConstraint(target, parentNode)
                pm.container(asset, edit=True,
                             includeHierarchyBelow=True,
                             force=True,
                             addNode=[parentNode, constraint])

                for s in controls:
                    # loc = self.funcs.tempLocator(name=s, suffix='baked')

                    loc = self.funcs.tempControl(name=s, suffix='baked', drawType='cross',
                                                 scale=pm.optionVar.get(self.tbBakeLocatorSizeOption, 1))
                    pm.parent(loc, parentNode)
                    pm.addAttr(loc, ln=self.constraintTargetAttr, at='message')
                    pm.connectAttr(s + '.message', loc + '.' + self.constraintTargetAttr)
                    const = pm.parentConstraint(s, loc)
                    locs.append(loc)
                    constraints.append(const)
                    pm.container(asset, edit=True,
                                 includeHierarchyBelow=True,
                                 force=True,
                                 addNode=loc)

                if locs:
                    preContainers = set(pm.ls(type='container'))
                    keyRange = self.funcs.getBestTimelineRangeForBake()
                    pm.bakeResults(locs,
                                   simulation=pm.optionVar.get(self.quickBakeSimOption, False),
                                   sampleBy=1,
                                   oversamplingRate=1,
                                   disableImplicitControl=True,
                                   preserveOutsideKeys=False,
                                   sparseAnimCurveBake=True,
                                   removeBakedAttributeFromLayer=False,
                                   removeBakedAnimFromLayer=False,
                                   bakeOnOverrideLayer=False,
                                   minimizeRotation=True,
                                   controlPoints=False,
                                   shape=False,
                                   time=[keyRange[0],
                                         keyRange[1]],
                                   )
                    self.removeContainersPostBake(preContainers)
                    if constrain:
                        pm.delete(constraints)
                        for cnt, loc in zip(sel, locs):
                            constraint = self.funcs.safeParentConstraint(loc, cnt,
                                                                         orientOnly=orientOnly,
                                                                         maintainOffset=False)
                            '''
                            pm.container(asset, edit=True,
                                         includeHierarchyBelow=True,
                                         force=True,
                                         addNode=constraint)
                            '''
                '''
                if pm.optionVar.get(self.tempControlMotionTrailOption, False):
                    if not skipMotionTrails:
                        for l in locs:
                            cmds.select(str(l), replace=True)
                            mel.eval('createMotionTrail')
                '''
                if select:
                    pm.select(locs, replace=True)
                return locs

            except Exception:
                cmds.warning(traceback.format_exc())
                self.funcs.resumeSkinning()

    def bakeSelectedHotkey(self):
        sel = pm.ls(sl=True)
        if not sel:
            return
        assets = list()
        for s in sel:
            asset = pm.container(query=True, findContainer=s)
            if asset not in assets:
                assets.append(asset)

        if not assets:
            return
        self.bakeSelectedCommand(assets, sel)

    def bakeAllHotkey(self):
        sel = pm.ls(sl=True)
        if not sel:
            return
        asset = pm.container(query=True, findContainer=sel[0])
        if not asset:
            return
        self.bakeAllCommand(asset, sel)

    def removeAllHotkey(self):
        sel = pm.ls(sl=True)
        if not sel:
            return
        asset = pm.container(query=True, findContainer=sel[0])
        if not asset:
            return
        self.deleteControlsCommand(asset, sel)

    def assetRmbCommand(self):
        panel = cmds.getPanel(underPointer=True)
        parentMMenu = panel + 'ObjectPop'
        cmds.popupMenu(parentMMenu, edit=True, deleteAllItems=True)
        sel = pm.ls(sl=True)
        asset = pm.container(query=True, findContainer=sel[0])

        # check asset message attribute

        cmds.menuItem(label='Bake Tools', enable=False, boldFont=True, image='container.svg')
        cmds.menuItem(divider=True)
        cmds.menuItem(label='Bake selected temp controls to layer',
                      command=pm.Callback(self.bakeSelectedCommand, asset, sel))
        cmds.menuItem(label='Bake all temp controls to layer', command=pm.Callback(self.bakeAllCommand, asset, sel))
        cmds.menuItem(divider=True)
        cmds.menuItem(label='Delete selected temp controls',
                      command=pm.Callback(self.deleteSelectedControlsCommand, asset, sel))
        cmds.menuItem(label='Delete all temp controls', command=pm.Callback(self.deleteControlsCommand, asset, sel))
        cmds.menuItem(divider=True)

    def assetRmbCommand(self):
        panel = cmds.getPanel(underPointer=True)
        parentMMenu = panel + 'ObjectPop'
        cmds.popupMenu(parentMMenu, edit=True, deleteAllItems=True)
        sel = pm.ls(sl=True)
        asset = pm.container(query=True, findContainer=sel[0])

        # check asset message attribute
        # print ("asset", asset, sel)

        cmds.menuItem(label='Bake Tools', enable=False, boldFont=True, image='container.svg')
        cmds.menuItem(divider=True)
        cmds.menuItem(label='Bake selected temp controls to layer',
                      command=pm.Callback(self.bakeSelectedCommand, asset, sel))
        cmds.menuItem(label='Bake all temp controls to layer', command=pm.Callback(self.bakeAllCommand, asset, sel))
        # cmds.menuItem(label='Bake out to layer', command=pm.Callback(self.bakeOutCommand, asset))
        cmds.menuItem(label='Delete all temp controls', command=pm.Callback(self.deleteControlsCommand, asset, sel))
        cmds.menuItem(divider=True)

    def get_available_attrs(self, node):
        '''
        returns 2 lists of attrs that are not available for constraining
        '''
        attrs = ['X', 'Y', 'Z']

        lockedTranslates = []
        lockedRotates = []
        for attr in attrs:
            if not pm.getAttr(node + '.' + 'translate' + attr, settable=True):
                lockedTranslates.append(attr.lower())
            if not pm.getAttr(node + '.' + 'rotate' + attr, settable=True):
                lockedRotates.append(attr.lower())

        return lockedTranslates, lockedRotates

    def bakeSelectedCommand(self, asset, sel):
        if not isinstance(asset, list):
            asset = [asset]
        tempControls = [x for x in sel if pm.attributeQuery(self.constraintTargetAttr, node=x, exists=True)]
        # print ('tempControls', tempControls)
        pairedControls = [x for x in tempControls if pm.attributeQuery(self.tempControlPairAttr, node=x, exists=True)]
        pairedControls = [pm.listConnections(x + '.' + self.tempControlPairAttr) for x in pairedControls]
        # print ('pairedControls', pairedControls)
        filteredPairedControls = [item for sublist in pairedControls for item in sublist if item]
        # print ('filteredPairedControls', filteredPairedControls)
        filteredPairedControls = [p for p in filteredPairedControls if p not in tempControls]
        tempControls += filteredPairedControls
        # print ('tempControls', tempControls)

        targets = [cmds.listConnections(s + '.' + self.constraintTargetAttr) for s in tempControls]
        # print ('targets', targets)
        filteredTargets = list(set([item for sublist in targets for item in sublist if item]))
        # print ('filteredTargets', filteredTargets)

        self.bake_to_override(sel=filteredTargets)
        pm.delete(tempControls)

    def bakeAllCommand(self, asset, sel):
        nodes = pm.ls(pm.container(asset, query=True, nodeList=True), transforms=True)
        targets = [x for x in nodes if pm.attributeQuery(self.constraintTargetAttr, node=x, exists=True)]
        filteredTargets = [pm.listConnections(x + '.' + self.constraintTargetAttr)[0] for x in targets]

        self.bake_to_override(sel=filteredTargets)
        pm.delete(asset)

    def deleteSelectedControlsCommand(self, asset, sel):
        pm.delete(sel)

    def deleteControlsCommand(self, asset, sel):
        pm.delete(asset)

    def parentConst(self, constrainGroup=False, offset=True, postBake=False, postReverseConst=False):
        drivers = pm.ls(sl=True)
        if not len(drivers) > 1:
            return pm.warning('not enough objects selected to constrain, please select at least 2')
        target = drivers.pop(-1)

        if constrainGroup:
            if not target.getParent():
                pm.warning("trying to constrain object's parent, but it is parented to the world")
            else:
                target = target.getParent()

        pm.parentConstraint(drivers, target,
                            skipTranslate=self.funcs.getAvailableTranslates(target),
                            skipRotate=self.funcs.getAvailableRotates(target),
                            maintainOffset=offset)
        if postBake:
            self.quickBake(target)
            if postReverseConst:
                if len(drivers) != 1:
                    return pm.warning('Can only post reverse constraint if 2 objects are used')
                else:
                    pm.parentConstraint(target, drivers[0],
                                        skipTranslate=self.funcs.getAvailableTranslates(drivers[0]),
                                        skipRotate=self.funcs.getAvailableRotates(drivers[0]),
                                        maintainOffset=True)

    def clearBlendAttrs(self, node):
        for attr in cmds.listAttr(node):
            if 'blendParent' in str(attr):
                cmds.deleteAttr(node, at=attr)

    def quickBake(self, node, startTime=None, endTime=None, deleteConstraints=True):
        if not startTime:
            startTime = pm.playbackOptions(query=True, minTime=True)
        if not endTime:
            endTime = pm.playbackOptions(query=True, maxTime=True)
        with self.funcs.suspendUpdate():
            try:
                keyRange = self.getBestTimelineRangeForBake()
                pm.bakeResults(node,
                               simulation=False,
                               disableImplicitControl=False,
                               time=[keyRange[0],
                                     keyRange[1]],
                               sampleBy=1)
                if deleteConstraints:
                    if not isinstance(node, list):
                        node = [node]
                    for n in node:
                        n = str(n)
                        constraints = cmds.listRelatives(n, type='constraint')
                        if constraints:
                            cmds.delete(constraints)
                        self.clearBlendAttrs(n)
            except Exception:
                cmds.warning(traceback.format_exc())
                self.funcs.resumeSkinning()

    def addOverrideLayer(self):
        return self.add_layer(override=True)

    def addAdditiveLayer(self, component=True):
        return self.add_layer(override=False, component=component)

    def createLayer(self, override=False, suffixStr=None, component=True):
        if suffixStr is None:
            suffixStr = {True: 'Override', False: 'Additive'}[override]

        colour = {True: self.overrideLayerColour, False: self.additiveLayerColour}

        newAnimLayer = pm.animLayer(suffixStr,
                                    override=override,
                                    addSelectedObjects=True,
                                    passthrough=True,
                                    lock=False)

        newAnimLayer.ghostColor.set(colour[override])
        newAnimLayer.scaleAccumulationMode.set(not override)
        newAnimLayer.rotationAccumulationMode.set(component)

        self.deselect_layers()
        newAnimLayer.selected.set(True)
        newAnimLayer.preferred.set(True)
        return newAnimLayer

    def add_layer(self, override=False, component=True):
        timeRange = None
        if self.funcs.isTimelineHighlighted():
            timeRange = self.funcs.getTimelineHighlightedRange()
        newAnimLayer = self.createLayer(override=override, component=component)

        if timeRange:
            if override:
                # if adding an override layer with timeline selected, key the layer weight
                self.allTools.tools['LayerEditor'].bookEndLayerWeight(newAnimLayer, timeRange[0], timeRange[1])
            '''
            # key the start and end times with an identity pose
            cmds.setKeyframe(animLayer=newAnimLayer,
                             time=((timeRange[0]), timeRange[1]),
                             respectKeyable=True,
                             hierarchy=False,
                             breakdown=False,
                             dirtyDG=True,
                             controlPoints=False,
                             shape=False,
                             identity=True)
            '''
        return
        '''
            if override:
                cmds.setKeyframe(animLayer=newAnimLayer,
                                 time=(cmds.currentTime(query=True), ),
                                 respectKeyable=True,
                                 hierarchy=False,
                                 breakdown=False,
                                 dirtyDG=True,
                                 controlPoints=False,
                                 shape=False,
                                 identity=True)
        '''
        '''
        # in case there's something to do automatically to the objects?
        sel = pm.ls(selection=True)
        if not sel:
            return
        '''

    def deselect_layers(self):
        for layers in pm.ls(type='animLayer'):
            layers.selected.set(False)

    def counterLayerAnimation(self):
        """
        Counters the animation of the last selected object in the layer, outputs the countered
        animation into a new layer under the other.
        TODO - fix this so it gets a better key range!
        :return:
        """
        sel = pm.ls(sl=True)
        if not sel:
            return cmds.warning('nothing selected')
        if len(sel) == 1:
            return cmds.warning('please select at least one controller to counter, followed by the driver')
        animLayer = self.funcs.get_selected_layers()
        if not animLayer:
            return cmds.warning('no anim layer selected')
        driver = sel[-1]
        targets = sel[:-1]

        affectedLayers = cmds.animLayer([driver], q=True, affectedLayers=True)
        if animLayer[0] not in affectedLayers:
            return cmds.warning('driver control is not found in the selected layer')
        keyRange = self.funcs.get_all_key_times(str(driver), selected=False)
        if not keyRange:
            return cmds.warning('driver control does not appear to have any keys in the selected layer')
        resultLayer = pm.animLayer(animLayer[0] + '_Counter')
        pm.setAttr(resultLayer + '.scaleAccumulationMode', 0)
        pm.animLayer(resultLayer, edit=True, override=True, parent=animLayer[0])
        allAttrs = list()
        for target in targets:
            translates = self.funcs.getAvailableTranslates(target)
            rotates = self.funcs.getAvailableRotates(target)
            attrs = ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ']
            layerAttrs = [target + '.' + x for x in attrs if x not in translates + rotates]
            pm.animLayer(resultLayer, edit=True, attribute=layerAttrs)
            allAttrs.extend(layerAttrs)

        # mut the layer to get the underlying animtion
        pm.animLayer(animLayer[0], edit=True, mute=True)
        # bake the controls to locators
        locators = self.bake_to_locator(sel=targets, constrain=True, select=False)
        # restore the animation layer
        pm.animLayer(animLayer[0], edit=True, mute=False)

        # bake out the result values

        preContainers = set(pm.ls(type='container'))
        keyRange = self.funcs.getBestTimelineRangeForBake()
        pm.bakeResults(allAttrs,
                       time=(keyRange[0], keyRange[-1]),
                       destinationLayer=resultLayer,
                       simulation=False,
                       sampleBy=1,
                       oversamplingRate=1,
                       disableImplicitControl=True,
                       preserveOutsideKeys=False,
                       sparseAnimCurveBake=True,
                       removeBakedAttributeFromLayer=False,
                       removeBakedAnimFromLayer=False,
                       bakeOnOverrideLayer=True,
                       minimizeRotation=True,
                       controlPoints=False,
                       shape=False)
        pm.delete(locators)
        self.removeContainersPostBake(preContainers)

        for v in allAttrs:
            if not cmds.getAttr(v, keyable=True):
                continue  # skip locked attributes
            layerValues = []
            baseplug, layerplug = self.funcs.getLowerLayerPlugs(v, resultLayer)
            animRange = int(keyRange[-1] - keyRange[0] + 1)
            if not baseplug:
                continue
            if not layerplug:
                continue
            for x in range(0, animRange):
                baseVal = cmds.getAttr(baseplug, time=keyRange[0] + x)
                layerVal = cmds.getAttr(layerplug, time=keyRange[0] + x)
                delta = layerVal - baseVal
                layerValues.append(delta)

            for x in range(0, animRange):
                cmds.setKeyframe(layerplug, time=keyRange[0] + x, value=layerValues[x])
        pm.animLayer(resultLayer, edit=True, override=False)

    def additiveExtractSelection(self):
        print('additiveExtractSelection')

        sel = cmds.ls(sl=True)
        if sel:
            self.additiveExtract(sel)

    def bakeConstraintToAdditiveSelection(self):
        sel = cmds.ls(sl=True)
        if sel:
            self.bakeConstraintToAdditive(sel)

    def bakeConstraintToAdditive(self, selection):
        """
        Bakes out controls with constraints to an additive layer.
        :param selection:
        :return:
        """
        if not selection:
            return cmds.warning('No objects selected')

        constraints = [cmds.listConnections(s, type='constraint') for s in selection]
        filteredConstraints = list(set([item for sublist in constraints for item in sublist if item]))
        if not filteredConstraints:
            return cmds.warning('No constraints found')

        additiveLayer = cmds.animLayer('AdditiveExtract', override=True)

        keyRange = self.funcs.get_all_layer_key_times(selection)
        cmds.bakeResults(selection,
                         time=(keyRange[0], keyRange[-1]),
                         destinationLayer=additiveLayer,
                         simulation=False,
                         sampleBy=1,
                         oversamplingRate=1,
                         disableImplicitControl=True,
                         preserveOutsideKeys=False,
                         sparseAnimCurveBake=False,
                         removeBakedAttributeFromLayer=False,
                         removeBakedAnimFromLayer=False,
                         bakeOnOverrideLayer=True,
                         minimizeRotation=True,
                         controlPoints=False,
                         shape=False)

        nodesToRemove = list()
        for s in selection:
            constraints = cmds.listRelatives(s, type='constraint')
            if not constraints:
                continue
            for c in constraints:
                connections = cmds.listConnections(c, type='transform')
                if connections:
                    for con in connections:
                        if con in selection:
                            continue
                        if con not in nodesToRemove:
                            nodesToRemove.append(con)
        for c in nodesToRemove:
            if cmds.objExists(c): cmds.delete(nodesToRemove)

        cmds.animLayer(additiveLayer, edit=True, mute=True, lock=True)

        cmds.currentTime(cmds.currentTime(query=True))

        overrideLayer = cmds.animLayer('ConstraintBase', override=True)
        cmds.bakeResults(selection,
                         time=(keyRange[0], keyRange[-1]),
                         destinationLayer=overrideLayer,
                         simulation=False,
                         sampleBy=1,
                         oversamplingRate=1,
                         disableImplicitControl=True,
                         preserveOutsideKeys=False,
                         sparseAnimCurveBake=False,
                         removeBakedAttributeFromLayer=False,
                         removeBakedAnimFromLayer=False,
                         bakeOnOverrideLayer=True,
                         minimizeRotation=True,
                         controlPoints=False,
                         shape=False)

        cmds.animLayer(additiveLayer, edit=True, mute=False, lock=False)
        cmds.animLayer(additiveLayer, edit=True, override=False)
        cmds.setAttr(additiveLayer + '.scaleAccumulationMode', 0)

        cmds.currentTime(cmds.currentTime(query=True))

        attributes = cmds.animLayer(overrideLayer, query=True, attribute=True)

        baseLayerMPlugs, baseLayerMFnAnimCurves = self.funcs.omGetPlugsFromLayer(str(overrideLayer), attributes)
        additiveLayerMPlugs, additiveMFnAnimCurves = self.funcs.omGetPlugsFromLayer(str(additiveLayer), attributes)

        overrideValues = dict()
        additiveValues = dict()
        additiveMTimeArray = None
        overrideMTimeArray = None

        for attr, curve in baseLayerMFnAnimCurves.items():
            keyTimes = [om2.MTime(curve.input(key).value, om2.MTime.uiUnit()) for key in range(curve.numKeys)]

            baseKeyValues = [curve.value(key) for key in range(curve.numKeys)]
            additiveKeyValues = [additiveMFnAnimCurves[attr].value(key) for key in range(curve.numKeys)]

            initialVal = baseKeyValues[0]
            finalVal = baseKeyValues[-1]

            blendedValues = []
            for index, key in enumerate(keyTimes):
                blendedValues.append(baseKeyValues[index] - additiveKeyValues[index])
            additiveValues[attr] = blendedValues
            overrideValues[attr] = [initialVal, finalVal]
            if not additiveMTimeArray:
                additiveMTimeArray = self.funcs.createMTimeArray(keyTimes[0].value,
                                                                 int(keyTimes[-1].value) - int(keyTimes[0].value) + 1)
                overrideMTimeArray = self.funcs.createMTimePairArray(keyTimes[0], keyTimes[-1])
        dg = om2.MDGModifier()
        for key, mcurve in additiveMFnAnimCurves.items():
            sources = additiveLayerMPlugs[key].connectedTo(True, False)
            for i in range(len(sources)):
                dg.disconnect(sources[i], additiveLayerMPlugs[key])

            dg.doIt()

            adjustedCurve = oma2.MFnAnimCurve(additiveLayerMPlugs[key])
            adjustedCurve.create(additiveLayerMPlugs[key], additiveMFnAnimCurves[key].animCurveType, dg)

            adjustedCurve.addKeys(additiveMTimeArray,
                                  additiveValues[key],
                                  oma2.MFnAnimCurve.kTangentGlobal,
                                  oma2.MFnAnimCurve.kTangentGlobal)
            dg.doIt()

            sources = baseLayerMPlugs[key].connectedTo(True, False)
            for i in range(len(sources)):
                dg.disconnect(sources[i], baseLayerMPlugs[key])

            dg.doIt()

            adjustedCurve = oma2.MFnAnimCurve(baseLayerMPlugs[key])
            adjustedCurve.create(baseLayerMPlugs[key], baseLayerMFnAnimCurves[key].animCurveType, dg)

            adjustedCurve.addKeys(overrideMTimeArray,
                                  overrideValues[key],
                                  oma2.MFnAnimCurve.kTangentGlobal,
                                  oma2.MFnAnimCurve.kTangentGlobal)
            dg.doIt()

        for attr in attributes:
            if 'visibility' in attr.split('.')[-1]:
                cmds.animLayer(additiveLayer, edit=True, removeAttribute=attr)
        cmds.delete(overrideLayer)

    def overrideLayerEnumFixup(self, layerName, startTime):
        zeroedAttrTypes = ['enum', 'bool']
        zeroedAttrs = [a for a in cmds.animLayer(layerName, query=True, attribute=True) if
                       cmds.getAttr(a, type=True) in zeroedAttrTypes]
        cmds.animLayer(layerName, edit=True, override=False)
        cmds.animLayer(layerName, edit=True, mute=False)
        cmds.animLayer(layerName, edit=True, selected=True)
        cmds.animLayer(layerName, edit=True, preferred=True)
        cmds.setKeyframe(zeroedAttrs, identity=True, time=(startTime,))
        cmds.animLayer(layerName, edit=True, lock=True)
        cmds.animLayer(layerName, edit=True, lock=False)

    def additiveExtract(self, nodes):
        """
        TODO - fix bad calculation on non-zero start time
        :param nodes:
        :return:
        """
        print('additiveExtract', nodes)
        overrideLayer = cmds.animLayer('AdditiveBase', override=True)
        keyRange = self.funcs.getBestTimelineRangeForBake()
        print('key range', keyRange)
        cmds.bakeResults(nodes,
                         time=(keyRange[0], keyRange[-1]),
                         destinationLayer=overrideLayer,
                         simulation=False,
                         sampleBy=1,
                         oversamplingRate=1,
                         disableImplicitControl=True,
                         preserveOutsideKeys=False,
                         sparseAnimCurveBake=True,
                         removeBakedAttributeFromLayer=False,
                         removeBakedAnimFromLayer=False,
                         bakeOnOverrideLayer=True,
                         minimizeRotation=True,
                         controlPoints=False,
                         shape=False)
        additiveLayer = cmds.animLayer('AdditiveExtract', copy=overrideLayer, parent=overrideLayer)
        cmds.animLayer(additiveLayer, edit=True, override=False)
        cmds.setAttr(additiveLayer + '.scaleAccumulationMode', 0)

        attributes = cmds.animLayer(overrideLayer, query=True, attribute=True)
        '''
        for attr in attributes:
            if 'visibility' in attr.split('.')[-1]:
                cmds.animLayer(additiveLayer, edit=True, removeAttribute=attr)
        '''
        layeredPlugs = list()
        basePlugs = list()
        baseLayerMPlugs, baseLayerMFnAnimCurves = self.funcs.omGetPlugsFromLayer(str(overrideLayer), attributes)
        additiveLayerMPlugs, additiveMFnAnimCurves = self.funcs.omGetPlugsFromLayer(str(additiveLayer), attributes)
        # print (baseLayerMFnAnimCurves)
        overrideValues = dict()
        additiveValues = dict()
        additiveMTimeArray = None
        overrideMTimeArray = None
        ignoredAttributeTypes = ['bool', 'enum']
        for attr, curve in baseLayerMFnAnimCurves.items():
            attrIngored = False
            attrType = cmds.getAttr(attr, type=True)
            attrIngored = attrType in ignoredAttributeTypes
            keyTimes = [om2.MTime(curve.input(key).value, om2.MTime.uiUnit()) for key in range(curve.numKeys)]

            # print (keyTimes[0], keyTimes[-1])
            keyValues = [curve.value(key) for key in range(curve.numKeys)]
            # print (keyValues)
            initialVal = keyValues[0]
            finalVal = keyValues[-1]
            keyRange = keyTimes[-1] - keyTimes[0]
            # print (initialVal, finalVal, keyRange)
            # print ('keyRange', keyRange.value)
            blendedValues = []
            for index, key in enumerate(keyTimes):
                alpha = (key.value - keyTimes[0].value) / keyRange.value
                # print(attr, keyTimes[0].value, key.value, 'alpha', alpha,  keyRange.value)
                progress = ((finalVal - initialVal) * alpha) + initialVal
                # print (attr, key, progress)
                if attrIngored:
                    blendedValues.append(progress)
                else:
                    blendedValues.append(keyValues[index] - progress)
            additiveValues[attr] = blendedValues
            overrideValues[attr] = [initialVal, finalVal]
            if not additiveMTimeArray:
                additiveMTimeArray = self.funcs.createMTimeArray(keyTimes[0].value,
                                                                 int(keyTimes[-1].value) - int(keyTimes[0].value) + 1)
                overrideMTimeArray = self.funcs.createMTimePairArray(keyTimes[0], keyTimes[-1])
            # print ('additiveMTimeArray', additiveMTimeArray)
        dg = om2.MDGModifier()
        for key, mcurve in additiveMFnAnimCurves.items():
            sources = additiveLayerMPlugs[key].connectedTo(True, False)
            for i in range(len(sources)):
                dg.disconnect(sources[i], additiveLayerMPlugs[key])

            dg.doIt()

            adjustedCurve = oma2.MFnAnimCurve(additiveLayerMPlugs[key])
            adjustedCurve.create(additiveLayerMPlugs[key], additiveMFnAnimCurves[key].animCurveType, dg)

            adjustedCurve.addKeys(additiveMTimeArray,
                                  additiveValues[key],
                                  oma2.MFnAnimCurve.kTangentGlobal,
                                  oma2.MFnAnimCurve.kTangentGlobal)
            dg.doIt()

            sources = baseLayerMPlugs[key].connectedTo(True, False)
            for i in range(len(sources)):
                dg.disconnect(sources[i], baseLayerMPlugs[key])

            dg.doIt()

            adjustedCurve = oma2.MFnAnimCurve(baseLayerMPlugs[key])
            adjustedCurve.create(baseLayerMPlugs[key], baseLayerMFnAnimCurves[key].animCurveType, dg)

            adjustedCurve.addKeys(overrideMTimeArray,
                                  overrideValues[key],
                                  oma2.MFnAnimCurve.kTangentGlobal,
                                  oma2.MFnAnimCurve.kTangentGlobal)
            dg.doIt()
            # layeredPlugs.append(layerPlug)
            # basePlugs.append(basePlug)
        # self.overrideLayerEnumFixup(additiveLayer, keyTimes[0].value)
        self.funcs.bookEndLayerWeight(str(additiveLayer), keyRange[0], keyRange[-1])

    def getLayerNodesAndConstraints(self):
        allLayers = cmds.ls(type='animLayer')
        if 'BaseAnimation' in allLayers:
            allLayers.pop(allLayers.index('BaseAnimation'))

        allNodes = list()
        for layer in allLayers:
            attrs = cmds.animLayer(layer, query=True, attribute=True)
            nodes = [mel.eval('plugNode("%s")' % attr) for attr in attrs]
            allNodes.extend(list(set(nodes)))

        filteredTargets = [item for sublist in [cmds.listRelatives(n, type='constraint') or [] for n in nodes] for item
                           in sublist if item]
        filteredNodes = list(set([n for n in allNodes if not cmds.referenceQuery(n, isNodeReferenced=True)]))
        filteredConstraints = list(
            set([c for c in filteredTargets if not cmds.referenceQuery(c, isNodeReferenced=True)]))

        return filteredNodes, filteredConstraints

    def quickMergeAllLayers(self):
        try:
            with self.funcs.suspendUpdate():
                allLayers = cmds.ls(type='animLayer')
                rootLayer = cmds.animLayer(query=True, root=True)

                allAttrs = list()
                allNodes = list()
                for layer in allLayers:
                    attrs = cmds.animLayer(layer, query=True, attribute=True)
                    if not attrs:
                        continue
                    for attr in attrs:
                        if attr not in allAttrs:
                            allAttrs.append(attr)
                        node = mel.eval('plugNode "{0}"'.format(attrs[-1]))
                        if node not in allNodes:
                            allNodes.append(node)
                '''
                allConstraints = [item for sublist in [cmds.listRelatives(n, type='constraint') or [] for n in allNodes]
                                  for item in sublist if item]
                allConstraints = [x for x in allConstraints if cmds.objExists(x)]
                filteredConstraints = list(
                    set([c for c in allConstraints if not cmds.referenceQuery(c, isNodeReferenced=True)]))
                unreferencedNodes = list(
                    set([n for n in allNodes if not cmds.referenceQuery(n, isNodeReferenced=True)]))
                '''
                allLayers.remove(rootLayer)
                if not allNodes:
                    return cmds.warning('No controls found in layers, aborting')
                if not allAttrs:
                    return cmds.warning('No controls found in layers, aborting')
                '''
                # removing this and just reverting to timeline range
                keyRange = self.funcs.get_all_layer_key_times(allNodes)

                timelineRange = self.funcs.getTimelineRange()
                if not keyRange or keyRange[0] is None:
                    keyRange = timelineRange

                self.expandKeyRangeToTimelineRange(keyRange, timelineRange)
                '''
                keyRange = self.funcs.getBestTimelineRangeForBake()
                cmds.bakeResults(allAttrs,
                                 time=(keyRange[0], keyRange[-1]),
                                 # destinationLayer=rootLayer,
                                 simulation=True,
                                 sampleBy=1,
                                 oversamplingRate=1,
                                 disableImplicitControl=True,
                                 preserveOutsideKeys=False,
                                 sparseAnimCurveBake=True,
                                 removeBakedAttributeFromLayer=True,
                                 removeBakedAnimFromLayer=True,
                                 # bakeOnOverrideLayer=False,
                                 minimizeRotation=True,
                                 controlPoints=False,
                                 shape=False)

                cmds.delete(allLayers)
                # cmds.delete(unreferencedNodes)
                # cmds.delete(filteredConstraints)

        except Exception:
            cmds.warning(traceback.format_exc())
            self.funcs.resumeSkinning()

    def expandKeyRangeToTimelineRange(self, keyRange, timelineRange):
        keyRange[0] = min(keyRange[0], timelineRange[0])
        keyRange[1] = max(keyRange[-1], timelineRange[1])

    def quickMergeSelectionToNew(self):
        self.quickMergeSelection(base=False)

    def quickMergeSelectionToBase(self):
        self.quickMergeSelection(base=True)

    def quickMergeSelection(self, base=True):
        selection = cmds.ls(sl=True)
        if not selection:
            return cmds.warning('No objects selected')
        try:
            with self.funcs.suspendUpdate():
                allLayers = cmds.ls(type='animLayer')
                rootLayer = cmds.animLayer(query=True, root=True)
                affectedLayers = cmds.animLayer(query=True, affectedLayers=True)
                if rootLayer in affectedLayers: affectedLayers.remove(rootLayer)
                if not affectedLayers:
                    return cmds.warning('Objects do not appear to be in any animation layers')

                resultLayer = cmds.animLayer(override=True)

                keyRange = self.funcs.getBestTimelineRangeForBake()
                if base:

                    cmds.bakeResults(selection,
                                     time=(keyRange[0], keyRange[-1]),
                                     # destinationLayer=rootLayer,
                                     simulation=len(selection) > pm.optionVar.get(self.tbBakeSimObjectCountOption, 10),
                                     sampleBy=1,
                                     oversamplingRate=1,
                                     disableImplicitControl=True,
                                     preserveOutsideKeys=False,
                                     sparseAnimCurveBake=True,
                                     removeBakedAttributeFromLayer=True,
                                     removeBakedAnimFromLayer=True,
                                     # bakeOnOverrideLayer=False,
                                     minimizeRotation=True,
                                     controlPoints=False,
                                     shape=False)

                else:
                    cmds.bakeResults(selection,
                                     time=(keyRange[0], keyRange[-1]),
                                     destinationLayer=resultLayer,
                                     simulation=len(selection) > pm.optionVar.get(self.tbBakeSimObjectCountOption, 10),
                                     sampleBy=1,
                                     oversamplingRate=1,
                                     disableImplicitControl=True,
                                     preserveOutsideKeys=False,
                                     sparseAnimCurveBake=True,
                                     removeBakedAttributeFromLayer=True,
                                     removeBakedAnimFromLayer=True,
                                     # bakeOnOverrideLayer=False,
                                     minimizeRotation=True,
                                     controlPoints=False,
                                     shape=False)
                mel.eval('deleteEmptyAnimLayers')

        except Exception as e:
            self.funcs.resumeSkinning()

    def worldOffsetSelection(self):
        sel = cmds.ls(sl=True, type='transform')
        if not sel:
            return
        with self.funcs.suspendUpdate():
            try:
                self.worldOffset(sel)
            except Exception:
                cmds.warning(traceback.format_exc())
                self.funcs.resumeSkinning()

    def worldOffsetSelectionRotation(self):
        sel = cmds.ls(sl=True, type='transform')
        if not sel:
            return
        with self.funcs.suspendUpdate():
            try:
                self.worldOffset(sel, rotationOnly=True)
            except Exception:
                cmds.warning(traceback.format_exc())
                self.funcs.resumeSkinning()

    def worldOffset(self, sel, rotationOnly=False):
        """
        :return:
        """
        if not sel:
            return list()

        rotationRoots = dict()
        rotateAnimNodes = dict()
        rotateAnimOffsetNodes = dict()

        tempConstraints = list()
        for s in sel:
            rotationRoot = self.funcs.tempControl(name=s,
                                                  suffix='worldOffset',
                                                  drawType='orb',
                                                  scale=pm.optionVar.get(self.tbBakeWorldOffsetSizeOption, 0.5))
            rotateAnimNode = self.funcs.tempNull(name=s, suffix='RotateBaked')
            rotateAnimOffsetNode = self.funcs.tempControl(name=s,
                                                          suffix='localOffset',
                                                          drawType='diamond',
                                                          scale=pm.optionVar.get(self.tbBakeWorldOffsetSizeOption, 0.5))

            self.funcs.getSetColour(s, rotationRoot, brightnessOffset=-0.5)
            self.funcs.getSetColour(s, rotateAnimOffsetNode, brightnessOffset=0.5)

            pm.parent(rotateAnimNode, rotationRoot)
            pm.parent(rotateAnimOffsetNode, rotateAnimNode)

            tempConstraints.append(pm.pointConstraint(s, rotationRoot))
            tempConstraints.append(pm.parentConstraint(s, rotateAnimNode))

            rotationRoots[s] = rotationRoot
            rotateAnimNodes[s] = rotateAnimNode
            rotateAnimOffsetNodes[s] = rotateAnimOffsetNode
            ns = s.rsplit(':', 1)[0]
            if not cmds.objExists(ns + self.worldOffsetAssetName):
                self.createAsset(ns + self.worldOffsetAssetName, imageName=None)
            asset = ns + self.worldOffsetAssetName

            pm.addAttr(rotationRoot, ln=self.constraintTargetAttr, at='message')
            pm.addAttr(rotateAnimNode, ln=self.constraintTargetAttr, at='message')
            pm.addAttr(rotateAnimOffsetNode, ln=self.constraintTargetAttr, at='message')
            pm.connectAttr(s + '.message', rotationRoot + '.' + self.constraintTargetAttr)
            pm.connectAttr(s + '.message', rotateAnimNode + '.' + self.constraintTargetAttr)
            pm.connectAttr(s + '.message', rotateAnimOffsetNode + '.' + self.constraintTargetAttr)
            pm.container(asset, edit=True,
                         includeHierarchyBelow=True,
                         force=True,
                         addNode=rotationRoot)

        bakeTargets = list(rotationRoots.values()) + list(rotateAnimNodes.values())
        keyRange = self.funcs.getBestTimelineRangeForBake()
        pm.bakeResults(bakeTargets,
                       time=(keyRange[0], keyRange[1]),
                       simulation=False,
                       sampleBy=1,
                       oversamplingRate=1,
                       disableImplicitControl=True,
                       preserveOutsideKeys=False,
                       sparseAnimCurveBake=True,
                       removeBakedAttributeFromLayer=False,
                       removeBakedAnimFromLayer=False,
                       bakeOnOverrideLayer=False,
                       minimizeRotation=True,
                       controlPoints=False,
                       shape=False)
        pm.delete(tempConstraints)

        channels = self.funcs.getChannels()
        for s in sel:
            self.funcs.safeParentConstraint(rotateAnimOffsetNodes[s], s,
                                            orientOnly=rotationOnly,
                                            maintainOffset=False,
                                            channels=channels)
        pm.select(rotationRoots.values(), replace=True)

    def redirectSelected(self):
        sel = cmds.ls(sl=True)
        if not sel:
            return
        with self.funcs.suspendUpdate():
            try:
                self.redirect(sel)
            except Exception:
                cmds.warning(traceback.format_exc())
                self.funcs.resumeSkinning()

    def redirect(self, sel):
        if not sel:
            return

        roots = dict()
        rotationRoots = dict()
        translateAnimNodes = dict()
        rotateAnimNodes = dict()
        translateAnimOFfsetNodes = dict()
        rotateAnimOffsetNodes = dict()
        tempConstraints = list()

        for s in sel:
            root = self.funcs.tempControl(name=s, suffix='Root', drawType='redirectRoot')
            rotationRoot = self.funcs.tempControl(name=s, suffix='RotationRoot', drawType='flatRotator')
            translateAnimNode = self.funcs.tempNull(name=s, suffix='TranslateBaked')
            translateAnimOFfsetNode = self.funcs.tempControl(name=s, suffix='TranslateOffset', drawType='plus')
            rotateAnimNode = self.funcs.tempNull(name=s, suffix='RotateBaked')
            rotateAnimOffsetNode = self.funcs.tempControl(name=s, suffix='RotateOffset', drawType='sphereZ', scale=1.0)

            self.funcs.getSetColour(s, root, brightnessOffset=0)

            self.funcs.getSetColour(s, rotationRoot, brightnessOffset=-0.5)
            self.funcs.getSetColour(s, rotateAnimOffsetNode, brightnessOffset=0.5)

            self.funcs.getSetColour(s, translateAnimOFfsetNode, brightnessOffset=0.5)

            pm.parent(rotateAnimOffsetNode, rotateAnimNode)
            pm.parent(rotateAnimNode, rotationRoot)
            pm.parent(rotationRoot, root)
            pm.parent(translateAnimOFfsetNode, translateAnimNode)
            pm.parent(translateAnimNode, root)

            pm.delete(pm.parentConstraint(s, root))
            pm.setAttr(root.rotate, (0, 0, 0))

            rotationRoot.inheritsTransform.set(0)

            tempConstraints.append(pm.parentConstraint(s, translateAnimNode))
            tempConstraints.append(pm.parentConstraint(s, rotateAnimNode))
            pm.pointConstraint(translateAnimNode, rotationRoot)

            roots[s] = root
            rotationRoots[s] = rotationRoot
            translateAnimNodes[s] = translateAnimNode
            rotateAnimNodes[s] = rotateAnimNode
            translateAnimOFfsetNodes[s] = translateAnimOFfsetNode
            rotateAnimOffsetNodes[s] = rotateAnimOffsetNode
        bakeTargets = list(translateAnimNodes.values()) + list(rotateAnimNodes.values())
        keyRange = self.funcs.getBestTimelineRangeForBake()
        pm.bakeResults(bakeTargets,
                       time=(keyRange[0], keyRange[1]),
                       simulation=False,
                       sampleBy=1,
                       oversamplingRate=1,
                       disableImplicitControl=True,
                       preserveOutsideKeys=False,
                       sparseAnimCurveBake=True,
                       removeBakedAttributeFromLayer=False,
                       removeBakedAnimFromLayer=False,
                       bakeOnOverrideLayer=False,
                       minimizeRotation=True,
                       controlPoints=False,
                       shape=False)
        pm.delete(tempConstraints)

        # TODO - add scalar/blend to animated nodes-rest position

        for s in sel:
            pm.pointConstraint(translateAnimOFfsetNodes[s], s)
            pm.orientConstraint(rotateAnimOffsetNodes[s], s)

    def resampleSelectedLayer(self, sample=1):
        allLayers = self.funcs.get_selected_layers(None)
        for layer in allLayers:
            self.resampleLayer(layer, sample=sample)

    def resampleLayer(self, layer=str(), sample=1, startTime=None, endTime=None):
        if not layer:
            return
        curves = cmds.animLayer(layer, query=True, animCurves=True)
        if not curves:
            return
        for c in curves:
            keyTimes = cmds.keyframe(c, query=True, timeChange=True)
            if not startTime:
                startTime = keyTimes[0]
            if not endTime:
                endTime = keyTimes[-1]
            cmds.bakeResults(c,
                             sampleBy=sample,
                             oversamplingRate=1,
                             time=(startTime, (endTime)),
                             preserveOutsideKeys=True,
                             sparseAnimCurveBake=False)

    def bakeOnXUI(self):
        wd = bakeOnXWidget(title='Bake to key per (x) frames', label='Frames', buttonText="Bake", default="Bake")

    def bakeChannel(self):
        curves = self.funcs.get_selected_curves()
        for c in curves:
            cmds.bakeResults(c,
                             sampleBy=1,
                             oversamplingRate=1,
                             preserveOutsideKeys=1)


class bakeOnXWidget(IntInputWidget):
    def __init__(self, title=str(), label=str(), buttonText="Accept", default="Accept"):
        super(bakeOnXWidget, self).__init__(title=title, label=label, buttonText=buttonText, default=default)
        buttonLayout = QHBoxLayout()
        self.layout().addLayout(buttonLayout)
        for x in range(5):
            button = QPushButton("%s's" % (x + 1))
            button.sample = x + 1
            button.clicked.connect(self.button_pushed)
            buttonLayout.addWidget(button)

        self.acceptedSignal.connect(self.bake_pressed)

    def bake_pressed(self, sample):
        pm.Callback(BakeTools().bake_to_override(sampleRate=sample))

    def button_pushed(self):
        pm.Callback(BakeTools().bake_to_override(sampleRate=self.sender().sample))
        self.close()
