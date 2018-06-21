# encoding: utf-8

###########################################################################################################
#
#
#	General Plugin
#
#	Read the docs:
#	https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates/General%20Plugin
#
#
###########################################################################################################

import objc
from GlyphsApp import *
from GlyphsApp.plugins import *

class SyncSelection(GeneralPlugin):
	counter=0
	
	def settings(self):
		self.name = Glyphs.localize({
			'en': u'Sync Layer Selections', 
			'de': u'Auswahl zwischen Ebenen synchronisieren',
			'es': u'Sincronizar selección de todas las capas',
			'fr': u'Synchroniser les sélections entre les calques',
			'ko': u"선택한 레이어 동기화"
		})
	
	def start(self):
		Glyphs.registerDefault("com.mekkablue.SyncSelection.state", False)

		menuItem = NSMenuItem(self.name, self.toggleSelectionSync)
		menuItem.setState_(bool(Glyphs.defaults["com.mekkablue.SyncSelection.state"]))
		Glyphs.menu[EDIT_MENU].append(menuItem)
		
		if Glyphs.defaults["com.mekkablue.SyncSelection.state"]:
			Glyphs.addCallback(self.keepSelectionInSync, DRAWFOREGROUND)
			self.counter+=1
		self.isSyncing = False
		
	def __del__(self):
		try:
			Glyphs.removeCallback(self.keepSelectionInSync, DRAWFOREGROUND)
			self.counter-=1
		except:
			# exit gracefully, but do report:
			import traceback
			print traceback.format_exc()
	
	def toggleSelectionSync(self, sender):
		if Glyphs.defaults["com.mekkablue.SyncSelection.state"]:
			Glyphs.defaults["com.mekkablue.SyncSelection.state"] = False
			Glyphs.removeCallback(self.keepSelectionInSync, DRAWFOREGROUND)
			self.counter-=1
		else:
			Glyphs.defaults["com.mekkablue.SyncSelection.state"] = True
			Glyphs.addCallback(self.keepSelectionInSync, DRAWFOREGROUND)
			self.counter+=1
		
		currentState = ONSTATE if Glyphs.defaults["com.mekkablue.SyncSelection.state"] else OFFSTATE
		Glyphs.menu[EDIT_MENU].submenu().itemWithTitle_(self.name).setState_(currentState)
		
	
	def keepSelectionInSync(self, sender, blackAndScale=None):
		
		# only sync when a document and a tab is open:
		if Glyphs.font and Glyphs.font.currentTab:
			
			# do not sync when Select All Layers tool is active:
			try:
				toolClass = Glyphs.currentDocument.windowController().toolEventHandler().className()
			except:
				toolClass = None
			if toolClass != "GlyphsToolSelectAllLayers" and not self.isSyncing:
				self.isSyncing = True
				# only sync when a glyph layer is open for editing:
				layer = Glyphs.font.currentTab.activeLayer()
				if layer and not "Background" in layer.className():
					glyph = layer.glyph()
					selection = layer.selection
					otherLayers = [
						l for l in glyph.layers 
							if l.layerId != layer.layerId 
							and l.compareString() == layer.compareString()
						]
									
					# reset selection in other layers:
					for otherLayer in otherLayers:
						otherLayer.selection = None
						
					# step through other layers and sync selection:
					if selection:
						if otherLayers:
							
							# sync anchors:
							for thisAnchor in layer.anchors:
								if thisAnchor in selection:
									for otherLayer in otherLayers:
										try:
											otherLayer.selection.append(otherLayer.anchors[thisAnchor.name])
										except:
											pass
							
							# sync node selection:
							for i,thisPath in enumerate(layer.paths):
								for j,thisNode in enumerate(thisPath.nodes):
									if thisNode in selection:
										for otherLayer in otherLayers:
											try:
												otherLayer.selection.append(otherLayer.paths[i].nodes[j])
											except:
												pass
							
							# sync selection of components:
							for i,thisComponent in enumerate(layer.components):
								if thisComponent in selection:
									for otherLayer in otherLayers:
										try:
											otherLayer.selection.append(otherLayer.components[i])
										except:
											pass

				self.isSyncing = False
	
	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__
	