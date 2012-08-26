# Virtual Revision NVDA plugin
# Version 0.2
#Copyright (C) 2012 Rui Batista <ruiandrebatista@gmail.com>
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.

import wx

import api
import globalPluginHandler
import gui
import textInfos
import addonHandler
addonHandler.initTranslation()



virtualWindowViewer = None

class GlobalPlugin(globalPluginHandler.GlobalPlugin):

	def script_virtualWindowReview(self, nextHandler):
		# Find the first focus ansestor that have any display text, according to the display model
		# This must be the root application window, or something close to that.
		text = None
		root = None
		for ancestor in api.getFocusAncestors():
			if ancestor.appModule and ancestor.displayText:
				root = ancestor
				break
		if root:
			text = root.displayText.replace("\0", ' ')
		obj = api.getFocusObject()
		if obj.windowClassName == u'ConsoleWindowClass':
			info = obj.makeTextInfo(textInfos.POSITION_FIRST)
			info.expand(textInfos.UNIT_STORY)
			text = info.clipboardText
		if text:
			activate()
			virtualWindowViewer.outputCtrl.SetValue(text)
	script_virtualWindowReview.__doc__ = _("Opens a dialog containing the text of the currently focused window for easy review.")

	__gestures = {"kb:nvda+control+w" : "virtualWindowReview"}

class VirtualWindowViewer(wx.Frame):
	""" Virtual Window viewer GUI.
	"""

	def __init__(self, parent):
		super(VirtualWindowViewer, self).__init__(parent, wx.ID_ANY, _("Virtual Revision"))
		self.Bind(wx.EVT_ACTIVATE, self.onActivate)
		self.Bind(wx.EVT_CLOSE, self.onClose)
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		self.outputCtrl = wx.TextCtrl(self, wx.ID_ANY, size=(500, 500), style=wx.TE_MULTILINE | wx.TE_READONLY|wx.TE_RICH)
		self.outputCtrl.Bind(wx.EVT_CHAR, self.onOutputChar)
		mainSizer.Add(self.outputCtrl, proportion=1, flag=wx.EXPAND)
		self.SetSizer(mainSizer)
		mainSizer.Fit(self)
		self.outputCtrl.SetFocus()

	def onActivate(self, evt):
		pass

	def onClose(self, evt):
		self.Destroy()

	def onOutputChar(self, evt):
		key = evt.GetKeyCode()
		if key == wx.WXK_ESCAPE:
			self.Close()
		evt.Skip()

def activate():
	"""Activate the virtual window viewer.
	If the virtual window viewer has not already been created and opened, this will create and open it.
	Otherwise, it will be brought to the foreground if possible.
	"""
	global virtualWindowViewer
	if not virtualWindowViewer:
		virtualWindowViewer = VirtualWindowViewer(gui.mainFrame)
	virtualWindowViewer.Raise()
	# There is a MAXIMIZE style which can be used on the frame at construction, but it doesn't seem to work the first time it is shown,
	# probably because it was in the background.
	# Therefore, explicitly maximise it here.
	# This also ensures that it will be maximized whenever it is activated, even if the user restored/minimised it.
	virtualWindowViewer.Maximize()
	virtualWindowViewer.Show()
