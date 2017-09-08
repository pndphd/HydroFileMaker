# -*- coding: utf-8 -*-
"""
/***************************************************************************
 HydroFileMaker
								 A QGIS plugin
 Makes the flow and depth HydroFileMaker input files
							  -------------------
		begin				: 2016-10-25
		git sha			  : $Format:%H$
		copyright			: (C) 2016 by Peter Dudley
		email				: pndphd@gmail.com
 ***************************************************************************/

/***************************************************************************
 *																		 *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or	 *
 *   (at your option) any later version.								   *
 *																		 *
 ***************************************************************************/
"""
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
import qgis.utils
# Initialize Qt resources from file resources.py
import resources
import processing
# Import the code for the dialog
from HydroFileMaker_dialog import HydroFileMakerDialog
import os.path
from qgis.gui import *
from qgis.analysis import *
import resources
import os
import glob


class HydroFileMaker:
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
			'HydroFileMaker_{}.qm'.format(locale))

		if os.path.exists(locale_path):
			self.translator = QTranslator()
			self.translator.load(locale_path)

			if qVersion() > '4.3.3':
				QCoreApplication.installTranslator(self.translator)

		# Create the dialog (after translation) and keep reference
		self.dlg = HydroFileMakerDialog()

		# Declare instance attributes
		self.actions = []
		self.menu = self.tr(u'&HydroFileMaker')
		# TODO: We are going to let the user set this up in a future iteration
		self.toolbar = self.iface.addToolBar(u'HydroFileMaker')
		self.toolbar.setObjectName(u'HydroFileMaker')
		
		self.dlg.lineEdit.clear()
		self.dlg.pushButton.clicked.connect(self.select_output_file)

	# noinspection PyMethodMayBeStatic
	def tr(self, message):
		"""Get the translation for a string using Qt translation API.

		We implement this ourselves since we do not inherit QObject.

		:param message: String for translation.
		:type message: str, QString

		:returns: Translated version of message.
		:rtype: QString
		"""
		# noinspection PyType	er,PyArgumentList,PyCallByClass
		return QCoreApplication.translate('HydroFileMaker', message)


	def add_action(
		self,
		icon_path,
		text,
		callback,
		enabled_flag=True,
		add_to_menu=True,
		add_to_toolbar=True,
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
			self.toolbar.addAction(action)

		if add_to_menu:
			self.iface.addPluginToMenu(
				self.menu,
				action)

		self.actions.append(action)

		return action
		

	def initGui(self):
		"""Create the menu entries and toolbar icons inside the QGIS GUI."""

		icon_path = ':/plugins/HydroFileMaker/icon.png'
		self.add_action(
			icon_path,
			text=self.tr(u''),
			callback=self.run,
			parent=self.iface.mainWindow())


	def unload(self):
		"""Removes the plugin menu item and icon from QGIS GUI."""
		for action in self.actions:
			self.iface.removePluginMenu(
				self.tr(u'&HydroFileMaker'),
				action)
			self.iface.removeToolBarIcon(action)
		# remove the toolbar
		del self.toolbar
		
	def select_output_file(self):
		
		filename = QFileDialog.getSaveFileName(self.dlg, "Select output file ","",".Data")
		self.dlg.lineEdit.setText(filename)

	def run(self):
		"""Run method that performs all the real work"""
		#Clear the File name area
		self.dlg.lineEdit.clear()
		#Clear ther list of rasters
		self.dlg.listWidget.clear()
		
		#Load the list of rasters into the list area
		for name, layer in QgsMapLayerRegistry.instance().mapLayers().iteritems():
			if layer.type() == QgsMapLayer.RasterLayer:
				self.dlg.listWidget.addItem(layer.name())
				self.dlg.listWidget.item(self.dlg.listWidget.count() - 1).setSelected(1)
  		self.dlg.listWidget.setDragDropMode(QAbstractItemView.InternalMove)
		
		#Load the vector layers into ther combo box
		layers = self.iface.legendInterface().layers()
		layer_list = []
		self.dlg.comboBox.clear()
		for layer in layers:
			layer_list.append(layer.name())
		self.dlg.comboBox.addItems(layer_list)

		# show the dialog
		self.dlg.show()
		# Run the dialog event loop
		result = self.dlg.exec_()
		# See if OK was pressed
		
		#Set a first time through indicator
		check = 1
		
		#make and empty list
		output = []
		
		if result:
			#load in ther output file name
			fileName = self.dlg.lineEdit.text()
			
			#get ther vector layer you want 
			selectedLayerIndex = self.dlg.comboBox.currentIndex()
			vectorLayer = layers[selectedLayerIndex]
			
			# delete all attributes currently in the layer
			fList = list()
			a = 0
			for field in vectorLayer.pendingFields():
				fList.append(a)
				a = a+1
			vectorLayer.dataProvider().deleteAttributes(fList)
			vectorLayer.updateFields()
			vectorLayer.commitChanges()
			
			#iterate each raster over ther vector layer
			for x in range(0, self.dlg.listWidget.count()):
				if self.dlg.listWidget.item(x).isSelected():
					for name, search_layer in QgsMapLayerRegistry.instance().mapLayers().iteritems():
						if search_layer.name() == self.dlg.listWidget.item(x).text():
							rasterLayer = search_layer

							#get the stats for each grid cell
							coverStatistics = QgsZonalStatistics( vectorLayer, rasterLayer.source())
							statistics = coverStatistics.calculateStatistics(None)
							vectorLayer.updateFields()
							vectorLayer.commitChanges()
							
							#Get ther fields form the layer
							fields = vectorLayer.pendingFields()
							fieldNames = [field.name() for field in fields]
							
							# QgsZonalStatistics will gennerate 3 columns that last one is mean which we want
							# rename the last column (mean) to the name we want
							vectorLayer.addAttributeAlias(len(fieldNames)-1,rasterLayer.name())
							
							# delete the other 2 fields made by the stats algo (the third to last and second to last)
							fList = list()
							fList.append(len(fieldNames)-2)
							fList.append(len(fieldNames)-3)
							vectorLayer.dataProvider().deleteAttributes(fList)
							vectorLayer.updateFields()
							vectorLayer.commitChanges()
					
			#open the output file for writting
			outputFile = open(fileName, 'w')
			
			# make a blank string called coords
			text = ''
			
			# get the list of features form ther layer
			features = vectorLayer.getFeatures()
			
			#Write ther first 2 lines plus first catagory label
			text = "Line 1\nLine 2\n"
			text = text + "Flows:\t"
			
			#Get ther fields from the layer
			fields = vectorLayer.pendingFields()
			fieldNames = [field.name() for field in fields]
			
			#Get the number of fields
			flowList = [0]*len(fieldNames)
			n=0
			
			#make a list of all flow conditions, take out duplicates, and sort them
			for flow in fieldNames:
				# the saga:gridstatisticsforpolygons puts "[MEAN]" on the end of ther column title so we take that off
				flow2 =  vectorLayer.attributeAlias(vectorLayer.fieldNameIndex(flow))
				flowList[n] = float(flow2[1:])
				n = n + 1
			flowList = list(set(flowList))
			flowList.sort(key=float)
			
			#make column header for shape id
			for i in flowList:
				text = text + str(i)+ "\t"
			text = text + "\n" + "Cell" + "\t"
			
			#make headders for ther flows
			for flow in fieldNames:
				# the saga:gridstatisticsforpolygons puts "[MEAN]" on the end of ther column title so we take that off
				flow2 =  vectorLayer.attributeAlias(vectorLayer.fieldNameIndex(flow))
				text = text + flow2[0] + "@" + flow2[1:] +"\t"
			text = text + "\n"
			
			# itterate over the features
			for feature in features:
				geom = feature.geometry()
				# get the vertices
				pt = geom.asPolygon()
				# check if the list is populated
				check = 1
				
				if check:
					# get ther feature id
					number = feature.id()+1
					# write the feature ID
					text = text + str(number) + "\t" 
					#write out the atttributes
					for att in feature.attributes():
						if not(att):
							text = text + str(0) + "\t"
						else:
							text = text + str(att) + "\t" 
					text = text + "\n"
			#write to the file
			unicodeLine = text.encode('utf-8')
			outputFile.write(unicodeLine)
			outputFile.close()
			#QgsMapLayerRegistry.instance().removeMapLayer(tempLayer.id())



