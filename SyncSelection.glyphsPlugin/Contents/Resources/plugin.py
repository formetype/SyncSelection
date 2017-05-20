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


from GlyphsApp.plugins import *
from GlyphsApp import UPDATEINTERFACE

class SyncSelection(GeneralPlugin):
	def settings(self):
		self.name = Glyphs.localize({
			'en': u'Sync Layer Selections', 
			'de': u'Auswahl zwischen Ebenen synchronisieren',
			'es': u'Sincronizar selección entre capas',
			'fr': u'Synchroniser la sélection entre les couches'
		})
		NSUserDefaults.standardUserDefaults().registerDefaults_(
			{
				"com.mekkablue.SyncSelection.state": False
			}
		)
	
	def start(self):
		try: 
			# new API in Glyphs 2.3.1-910
			menuItem = NSMenuItem(self.name, self.toggleSelectionSync)
			menuItem.setState_(bool(Glyphs.defaults["com.mekkablue.SyncSelection.state"]))
			Glyphs.menu[EDIT_MENU].append(menuItem)
		except:
			# old code, don't know if it works, likely to be removed soon:
			mainMenu = Glyphs.mainMenu()
			s = objc.selector(self.toggleSelectionSync,signature='v@:@')
			menuItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(self.name, s, "")
			menuItem.setTarget_(self)
			menuItem.setState_(bool(Glyphs.defaults["com.mekkablue.SyncSelection.state"]))
			mainMenu.itemWithTag_(5).submenu().addItem_(menuItem)
		
		if Glyphs.defaults["com.mekkablue.SyncSelection.state"]:
			self.addSyncCallback()
	
	def toggleSelectionSync(self, sender):
		if Glyphs.defaults["com.mekkablue.SyncSelection.state"]:
			Glyphs.defaults["com.mekkablue.SyncSelection.state"] = False
			self.removeSyncCallback()
		else:
			Glyphs.defaults["com.mekkablue.SyncSelection.state"] = True
			self.addSyncCallback()
		
		currentState = Glyphs.defaults["com.mekkablue.SyncSelection.state"]
		Glyphs.menu[EDIT_MENU].submenu().itemWithTitle_(self.name).setState_(currentState)

	def addSyncCallback(self):
		try:
			NSNotificationCenter.defaultCenter().addObserver_selector_name_object_(self, self.keepSelectionInSync, UPDATEINTERFACE, objc.nil)
		except Exception as e:
			import traceback
			print traceback.format_exc()
	
	def removeSyncCallback(self):
		try:
			NSNotificationCenter.defaultCenter().removeObserver_(self)
		except Exception as e:
			import traceback
			print traceback.format_exc()
	
	def keepSelectionInSync(self):
		if Glyphs.font and Glyphs.font.currentTab:
			layer = Glyphs.font.currentTab.activeLayer()
			if layer:
				glyph = layer.glyph()
				selection = layer.selection
				otherLayers = [l for l in glyph.layers if l != layer]

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
					
	
	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__
	