# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Altitudecorrector
                                 A QGIS plugin
 Calculates altitude correction for airborne gamma spectroemtry data
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2019-11-07
        git sha              : $Format:%H$
        copyright            : (C) 2019 by Morten Sickel
        email                : morten@sickel.net
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon, QCursor
from qgis.PyQt.QtWidgets import QAction, QFileDialog

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .altitudecorrector_dialog import AltitudecorrectorDialog
import os.path

import numpy
import processing
from PyQt5.QtCore import Qt

from qgis.core import QgsProject, Qgis, QgsApplication

from qgis.PyQt.QtWidgets import QGraphicsScene, QGraphicsView
# QApplication, ,QCheckBox, QFileDialog

from qgis.core import QgsVectorLayer, QgsFeature, QgsField, QgsGeometry, QgsPointXY, QgsField, QgsProject, QgsMapLayerProxyModel, QgsCoordinateTransform, QgsCoordinateReferenceSystem, QgsFieldProxyModel

from qgis.core import QgsExpression,QgsExpressionContextUtils

import processing

class Altitudecorrector:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'Altitudecorrector_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Spectral data')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('Altitudecorrector', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=False,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToVectorMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def updatemeasfields(self):
        self.dlg.fcbMeasure.setLayer(self.dlg.lcbMeasure.currentLayer())
        self.dlg.fcbAltitude.setLayer(self.dlg.lcbMeasure.currentLayer())


    def fit(self,data,log=False):
        
        x=numpy.array(data[0])
        y=numpy.array(data[1])
        if log:
            fit=numpy.polyfit(x, numpy.log(y), 1, w=numpy.sqrt(y))
            print(fit)
            fit=numpy.polyfit(x, numpy.log(y), 1, )
            print(fit)
        else:
            fit=numpy.polyfit(x, y, 1)
        return(fit)
    
    
    def plotdata(self):
        """
        
        """
        try:
            caliblayer=self.overlaylayer
        except:
            self.iface.messageBar().pushMessage(
                   "Atitude correction", "Overlay layer does not exist - run overlay",
                    level=Qgis.Critical, duration=3)
            return
        
        self.waterdata=self.extractdata(caliblayer,self.dlg.leWater.text())       
        self.landdata=self.extractdata(caliblayer,self.dlg.leLand.text())
        self.altplot(self.landdata,self.dlg.gwLand)
        self.altplot(self.waterdata,self.dlg.gwWater)
        # "Canned" parameters
        # ntb=4.284670
        # ntbfactor=0.001743
        # ntb0=ntb+ntbfactor
        # expfactor=-0.006383
        # gmmdown=(value1-ntb)*math.exp(expfactor)/math.exp(expfactor*value2)+ ntb0
        #self.landdata[0]=[x-ntb for x in self.landdata[0]]
        
    def savedata(self):
        """ Saves the overlay data as a tab separated data file to be able to 
        use other tools to calculate the parameters. Also updating the R-script in
        the last tab to use the saved file.
        """
        try:
            layer=self.overlaylayer
        except:
            self.iface.messageBar().pushMessage(
                   "Atitude correction", "Overlay layer does not exist - run overlay",
                    level=Qgis.Critical, duration=3)
            return
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self.dlg,"Save tab separated data file","","data files (*.dat);;All Files (*)", options=options)
        if not fileName:
            return
        script=self.dlg.teRscript.toPlainText()
        scriptlines=script.split("\n")
        scriptlines[0]='filename="{}"'.format(fileName)
        self.dlg.teRscript.setText('\n'.join(scriptlines))
        
        features=layer.getFeatures()
        valueidx = layer.fields().indexFromName(self.dlg.fcbMeasure.currentField())
        altidx=layer.fields().indexFromName(self.dlg.fcbAltitude.currentField())
        typeidx=layer.fields().indexFromName(self.dlg.fcbArea.currentField())
        ididx=layer.fields().indexFromName("id")
        idfield=ididx >=0
        id=0
        sep='\t'
        with open(fileName,"w") as outfile:
            outfile.write(sep.join(["id","altitude","measure","type\n"]))
            for feat in features:
                attrs=feat.attributes()
                if idfield:
                    id=attrs[ididx]
                else:
                    id=+1
                linedata=[id,attrs[altidx],attrs[valueidx],attrs[typeidx]]
                linedata=[str(t) for t in linedata]
                outfile.write(sep.join(linedata))
                outfile.write("\n")
        
        
    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/altitudecorrector/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Altitude correction'),
            callback=self.run,
            parent=self.iface.mainWindow())
        self.dlg = AltitudecorrectorDialog()
        self.dlg.lcbArea.setFilters(QgsMapLayerProxyModel.PolygonLayer)
        self.dlg.fcbArea.setLayer(self.dlg.lcbArea.currentLayer())
        self.dlg.lcbArea.layerChanged.connect(lambda: self.dlg.fcbArea.setLayer(self.dlg.lcbArea.currentLayer()))   
        self.dlg.lcbMeasure.setFilters(QgsMapLayerProxyModel.PointLayer)
        self.dlg.lcbOverlay.setFilters(QgsMapLayerProxyModel.PointLayer)
        self.dlg.fcbMeasure.setLayer(self.dlg.lcbArea.currentLayer())
        self.dlg.fcbMeasure.setFilters(QgsFieldProxyModel.Numeric)
        self.dlg.fcbAltitude.setFilters(QgsFieldProxyModel.Numeric)
        self.dlg.fcbAltitude.setLayer(self.dlg.lcbArea.currentLayer())
        self.dlg.lcbMeasure.layerChanged.connect(self.updatemeasfields)   
        self.dlg.lcbOverlay.layerChanged.connect(self.updatedoverlay)   
        self.dlg.pbRun.clicked.connect(self.plotdata)
        self.dlg.pbFit.clicked.connect(self.fit_curve)
        self.dlg.pbOverlay.clicked.connect(self.overlay)
        self.dlg.pbSave.clicked.connect(self.savedata)
        
        # will be set False in run()
        self.first_start = True
        self.updatemeasfields()
        from .qgis_function import altitudecorrection
    

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginVectorMenu(
                self.tr(u'Spectral data'),
                action)
            self.iface.removeToolBarIcon(action)
        QgsExpression.unregisterFunction("$altitudecorrection")
        
    def updatedoverlay(self):
        pass

    def extractdata(self,layer,key):
        """ Extracts altitude and dose data from a layer where type is a given key
        The fields to extract and the type field must have been selected in the UI
        
        :params layer: Layer to extract data from
        :params key: Value for key to select data
        """
        self.measure=[]
        self.altitude=[]
        features=layer.getFeatures()
        valueidx = layer.fields().indexFromName(self.dlg.fcbMeasure.currentField())
        altidx=layer.fields().indexFromName(self.dlg.fcbAltitude.currentField())
        typeidx=layer.fields().indexFromName(self.dlg.fcbArea.currentField())
        for feat in features:
            attrs=feat.attributes()
            if key == None or attrs[typeidx]==key: 
                self.altitude.append(attrs[altidx])
                self.measure.append(attrs[valueidx])
        if len(self.measure) < 2:
            self.iface.messageBar().pushMessage(
                   "Atitude correction", "Too few points found for altitude correction",
                    level=Qgis.Warnin, duration=3)
            
        return([self.altitude,self.measure])
    
    
    def overlay(self):
        """ Runs an overlay of the selected layers, makes plots of
        land and water data and calculates the parameters
        """
        measure=self.dlg.fcbMeasure.layer()
        area=self.dlg.fcbArea.layer()
        params={'INPUT':measure,
                'OVERLAY':area,
                'OUTPUT':"memory:land_water",
                'INTERSECTION':"memory:land_water"}
        QgsApplication.setOverrideCursor(QCursor(Qt.WaitCursor));
        self.iface.messageBar().pushMessage(
                   "Atitude correction", "Running overlay",
                    level=Qgis.Info, duration=3)
        output=processing.runAndLoadResults("qgis:intersection", params)
        QgsApplication.restoreOverrideCursor() 
        self.iface.messageBar().pushMessage(
                   "Atitude correction", "Overlay finished",
                    level=Qgis.Success, duration=3)
        self.overlaylayer=QgsProject.instance().mapLayer(output['OUTPUT'])
        self.dlg.lcbOverlay.setLayer(self.overlaylayer)
        self.plotdata()
        self.fit_curve()
    
    def altplot(self,dataset,graphicsview):
        """Plots dose vs altitude for land and water data
        """
        w=graphicsview.width()
        h=graphicsview.height()
        air=39 # Spacing around plot
        #bt=airborne
        plotw=w-air*2
        ploth=h-air*2
        scene=QGraphicsScene()
        graphicsview.setScene(scene)
        xspan=[min(dataset[1]),max(dataset[1])]
        yspan=[min(dataset[0]),max(dataset[0])]
        xfact=(xspan[1]-xspan[0])/plotw
        yfact=(yspan[1]-yspan[0])/ploth
        plotradius=2
        xaxy=float(ploth+plotradius*2) # x-axix y value
        yaxx=float(air-1)              # y-axis X value
        scene.addLine(yaxx,xaxy,yaxx,xaxy-ploth) # Y-axis
        scene.addLine(yaxx,xaxy,float(w-air/2),xaxy) # X-axis
        for alt,meas in zip(dataset[1],dataset[0]): #TODO, swap alt and meas
            x=(alt-xspan[0])/xfact+air # doserate
            y=ploth-(meas-yspan[0])/yfact # altitude|
            scene.addEllipse(x,y,plotradius*2,plotradius*2)
        scene.addText("Doserate").setPos(w-70,xaxy+5)
        # Is there a simple way to turn text 90 degrees?
        scene.addText("Altitude").setPos(air/2,0)
        xlabels = xspan
        for i in xlabels:
            scene.addText(str(round(i))).setPos((i - xspan[0])/xfact+air,xaxy)
        ylabels = yspan
        for i in ylabels:
            scene.addText(str(round(i))).setPos(0,ploth-(i - yspan[0])/yfact)
        
    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass

    def monoExp(self,x, m, t, b):
      import numpy as np
      return m * np.exp(-t * x) + b
   
    def fit_curve(self):
      try:
        import numpy as np
        import scipy.optimize
      except ImportError:
        self.iface.messageBar().pushMessage(
                   "Atitude correction", "Cannot import numpy and/or scipy - cannot run fit",
                    level=Qgis.Warning, duration=3)
        return()
      self.iface.messageBar().pushMessage(
                   "Atitude correction", "Calculating parameters ...",
                    level=Qgis.Success, duration=3)
      
      # https://swharden.com/blog/2020-09-24-python-exponential-fit/
      # NTB - calc average from waterdata
      # 
      waterfit=self.fit(self.waterdata)
      self.dlg.leWaterSlope.setText(str(round(waterfit[0],6)))
      ntb = round(waterfit[1],6)
      QgsExpressionContextUtils.setProjectVariable(QgsProject.instance(),'altitudecorrection_ntb',ntb)
      self.dlg.leNTB.setText(str(ntb))
      #print(waterfit[1])
      # To check that data makes sense:
      # "Canned" parameters
      # ntb=4.284670
      # ntbfactor=0.001743
      # ntb0=ntb+ntbfactor
      # expfactor=-0.006383
      # gmmdown=(value1-ntb)*math.exp(expfactor)/math.exp(expfactor*value2)+ ntb0
      calibdata=[]
      # Subtracting ntb to get only terrestrial background
      calibdata=[x - ntb for x in self.landdata[1]]
      p0=(50,0.006,ntb)
      params, cv = scipy.optimize.curve_fit(self.monoExp, self.landdata[0], calibdata, p0)
      dose0,alpha,offset=params
      self.dlg.leDose0.setText(str(round(dose0,6)))
      QgsExpressionContextUtils.setProjectVariable(QgsProject.instance(),'altitudecorrection_dose0',float(dose0)) # params[0])
      self.dlg.leAlpha.setText(str(round(params[1],6)))
      QgsExpressionContextUtils.setProjectVariable(QgsProject.instance(),'altitudecorrection_alpha',float(alpha)) # params[1])
      
      
# enum Qgis::MessageLevel
# 
# Level for messages This will be used both for message log and message bar in application.
# Info 	
# Warning 	
# Critical 	
# Success 	
# None 
