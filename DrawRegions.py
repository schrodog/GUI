import copy
import sys
import pyfits
from PIL import Image
import numpy as np
from math import sqrt
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class DrawRegions(QGraphicsPixmapItem):

	def __init__(self,pixmap=None,parent=None,scene=None):
		super(DrawRegions,self).__init__()
		global graphX
		global graphY
		self.hoverX, self.hoverY=0,0
		self.spaceArray, self.finalArray=[],[]
		self.setFlags(QGraphicsPixmapItem.ItemIsFocusable)
		self.scale=1.0
		self.mouseLeftClicking=False
		self.scaleX, self.scaleY = 0,0
		self.brushSize=30
		self.setAcceptHoverEvents(True)

		# print 'draw=',graphX,graphY
		self.minX, self.maxX=graphX,0
		self.minY, self.maxY=graphY,0

	def paint(self,painter,options,widget=None):
		painter.drawPixmap(0,0,self.pixmap())

		radius=self.brushSize
		painter.setPen(Qt.NoPen)
		painter.setBrush(QColor(125,125,125,120))

		painter.drawEllipse(self.hoverX-radius,self.hoverY-radius,2*radius,2*radius)

		painter.setBrush(QColor(125,125,125,30))

		for i in self.finalArray:
			for coor in i:
				radius=coor[2]
				painter.drawEllipse(coor[0]-radius,coor[1]-radius,2*radius,2*radius)

		if self.mouseLeftClicking:
			for coor in self.spaceArray:
				radius=coor[2]
				painter.drawEllipse(coor[0]-radius,coor[1]-radius,2*radius,2*radius)

	def mousePressEvent(self,event):
		if event.button()==Qt.LeftButton:
			self.mouseLeftClicking=True
			self.spaceArray=[]
		elif event.button()==Qt.RightButton:
			self.scaleX=event.pos().x()
			self.scaleY=event.pos().y()
			self.setX(graphX/2-self.scaleX)
			self.setY(graphY/2-self.scaleY)
			
		self.update()

	def hoverMoveEvent(self,event):
		self.hoverX,self.hoverY=event.pos().x(),event.pos().y()
		self.update()
	def mouseMoveEvent(self,event):
		# print 'in=',event.pos().x(),event.pos().y()
		if self.mouseLeftClicking:
			self.x=event.pos().x()
			self.y=event.pos().y()
			r=self.brushSize
			if self.notRepeat(self.x,self.y):
				self.spaceArray.insert(0,[self.x,self.y,r])
				if self.x+r>self.maxX:
					if self.x+r <= graphX:
						self.maxX=self.x+r
					else: 
						self.maxX=graphX
				if self.x-r<self.minX:
					if self.x-r >= 0:
						self.minX=self.x-r
					else:
						self.minX=0

				if self.y+r>self.maxY:
					if self.y+r <= graphY:
						self.maxY=self.y+r
					else: 
						self.maxY=graphY
				if self.y-r<self.minY:
					if self.y-r >= 0:
						self.minY=self.y-r
					else:
						self.minY=0
				# print self.minX,self.maxX,self.minY,self.maxY
				self.update()			

	def mouseReleaseEvent(self,event):
		self.mouseLeftClicking=False
		self.finalArray.insert(0,self.spaceArray)
		self.update()

	def keyPressEvent(self,event):
		super(DrawRegions,self).keyPressEvent(event) 	#need this,can press esc
		if event.key()==Qt.Key_W:
			self.setTransformOriginPoint(self.scaleX,self.scaleY)
			if self.scale>=1 and self.scale<10:
				if self.brushSize>2:
					self.brushSize /= 1.2
				self.scale += 0.5
			elif self.scale<1:
				self.scale += 0.2
			self.setScale(self.scale)
		elif event.key()==Qt.Key_Q:
			self.setTransformOriginPoint(self.scaleX,self.scaleY)
			if self.scale > 1:
				if self.brushSize<75:
					self.brushSize *= 1.2
				self.scale -= 0.5
			elif self.scale>=0.4:
				self.scale -= 0.2
			self.setScale(self.scale)
		elif event.key()==Qt.Key_E:
			self.setTransformOriginPoint(0,0)
			self.setScale(1.0)
		elif event.key()==Qt.Key_F:
			if self.brushSize<=155:
				self.brushSize +=5
		elif event.key()==Qt.Key_D:
			if self.brushSize >=10:
				self.brushSize -= 5
			elif self.brushSize <=10 and self.brushSize>1:
				self.brushSize -= 1
		elif event.key()==Qt.Key_U:
			self.delArray()
		self.update()

	def notRepeat(self,x,y):
		for i in self.spaceArray:
			if (i[0] == x) and (i[1]==y):
				return False
		return True

	def delArray(self):
		self.finalArray = self.finalArray[1:]
		self.update()
	def loadArray(self):
		return self.finalArray

	def saveRegion(self):
		fname=QFileDialog.getSaveFileName(None,"Save Region","/home/lkit/Pictures")
		f=open(fname,'w')
		f.write("%d %d\n" %(graphX,graphY))
		f.write("%d %d %d %d\n" %(self.minX,self.maxX,self.minY,self.maxY))
		for i in self.finalArray:
			for j in i:
				f.write("%d %d %d | " %(j[0], j[1], j[2]))
			f.write("\n")
		f.close()

	def loadRegion(self):
		fname=QFileDialog.getOpenFileName(None,"Load Region","/home/lkit/tmp")
		f=open(str(fname))
		dimension=map(int,f.readline().split())
		self.minX,self.maxX,self.minY,self.maxY=map(int,f.readline().split())
		data=[[map(int,i.split()) for i in line.split("|") if i.split()] for line in f]
		f.close()
		if (graphX>=dimension[0] and graphY>=dimension[1]):
			self.finalArray=data
			# print 'data->finalArray'
		else:
			msgBox=QMessageBox()
			msgBox.setWindowTitle("Warning")
			msgBox.setText("Mismatched region")
			msgBox.exec_()				
	def loadComputeRegion(self):
		data=[self.minX,self.maxX,self.minY,self.maxY]
		return data



class MainWindow(QMainWindow):
	def __init__(self):
		super(MainWindow,self).__init__()
		global graphX
		global graphY
		self.minX,self.maxX,self.minY,self.maxY=0,0,0,0
		self.mode=0
		self.setWindowTitle("Draw Regions")

		self.toolBar=QToolBar()
		self.addToolBar(Qt.LeftToolBarArea,self.toolBar)
		selectAction=self.toolBar.addAction("Select Mode")
		# selectAction.setCheckable(True)
		maskAction=self.toolBar.addAction("Mask Mode")
		undo=self.toolBar.addAction("undo")
		self.toolBar.addSeparator()
		newImageAction=self.toolBar.addAction("New image")
		saveRegionAction=self.toolBar.addAction("Save Region")
		loadRegionAction=self.toolBar.addAction("Load Region")		
		self.toolBar.addSeparator()
		exportAsFITSAction=self.toolBar.addAction("Export As FITS")
		exportAsPNGAction=self.toolBar.addAction("Export As PNG")
		exportWSLAPAction=self.toolBar.addAction("Export To WSLAP")
		self.toolBar.addSeparator()
		helpAction=self.toolBar.addAction("Help")

		self.statusBar=QStatusBar()
		self.setStatusBar(self.statusBar)

		selectAction.triggered.connect(self.showMsg01)
		maskAction.triggered.connect(self.showMsg02)
		undo.triggered.connect(self.undoAction)
		newImageAction.triggered.connect(self.newImage)
		saveRegionAction.triggered.connect(self.saveRegion)
		loadRegionAction.triggered.connect(self.loadRegion)
		exportAsFITSAction.triggered.connect(self.exportAsFits)
		exportAsPNGAction.triggered.connect(self.exportAsPNG)
		exportWSLAPAction.triggered.connect(self.exportWSLAP)
		helpAction.triggered.connect(self.helpFunc)

		
	def showMsg01(self):
		self.mode=1
		self.statusBar.showMessage("Select Mode")
	def showMsg02(self):
		self.mode=2
		self.statusBar.showMessage("Mask Mode")
	def undoAction(self):
		self.imagePanel.delArray()
	def saveRegion(self):
		self.imagePanel.saveRegion()
	def loadRegion(self):
		self.imagePanel.loadRegion()
	def newImage(self):
		global graphX
		global graphY
		self.scene=QGraphicsScene()
		self.pixmap=self.openImage()
		graphX,graphY= self.pixmap.width(),self.pixmap.height()
		self.resize(graphX,graphY)
		self.scene.setSceneRect(0, 0, graphX,graphY)
		self.imagePanel=DrawRegions(scene=self.scene)
		self.imagePanel.setPixmap(self.pixmap)
		self.scene.addItem(self.imagePanel)	#add GraphicsItem
		self.view = QGraphicsView(self.scene)
		layout=QHBoxLayout()
		layout.addWidget(self.view)
		self.widget=QWidget()
		self.widget.setLayout(layout)
		self.setCentralWidget(self.widget)


	def exportAsFits(self):
		if self.mode != 0:
			TFtable=self.genTFtable()

			input_fits=QFileDialog.getOpenFileName(self,"Open source FITS file",
				"/home/lkit/Data","*.fits")
			f=pyfits.open(str(input_fits))
			input_data=np.asarray(f[0].data)
			f.close()
			# print input_data
			if self.mode==1:
				output_data=np.asarray([[0.0 for i in range(graphX)] for j in range(graphY)])
			elif self.mode==2:
				output_data=copy.copy(input_data)
			# print output_data
			for i in range(int(self.minX),int(self.maxX)):
				for j in range(int(self.minY),int(self.maxY)):
					if self.mode==1:
						if TFtable[j,i]:
							output_data[graphY-j-1,i]=input_data[graphY-j-1,i]
					elif self.mode==2:
						if not TFtable[j,i]:
							output_data[graphY-j-1,i]=0

			hdu=pyfits.PrimaryHDU(output_data)
			out_fits=QFileDialog.getSaveFileName(None,"Save FITS file","/home/lkit/Pictures")
			hdu.writeto(str(out_fits),clobber=True)
		else:
			self.warningMsg("Please choose select/mask mode")


	def exportAsPNG(self):
		if self.mode != 0:
			TFtable=self.genTFtable()

			imInput=Image.open(str(self.input_image))
			input_data=np.asarray(imInput,dtype=np.uint8)
			if self.mode==1:
				if len(input_data[0,0])==3:
					# print 'choose 000'
					output_data=np.asarray([[[0,0,0] for i in range(graphX)] for j in range(graphY)], dtype=np.uint8)
				elif len(input_data[0,0])==4:
					# print 'choose 0000'
					output_data=np.asarray([[[0,0,0,255] for i in range(graphX)] for j in range(graphY)], dtype=np.uint8)
			else:
				output_data=copy.copy(input_data)

			for i in range(int(self.minX),int(self.maxX)):
				for j in range(int(self.minY),int(self.maxY)):
					if self.mode==1:
						if TFtable[j,i]:
							# print input_data[j,i],output_data[j,i]
							output_data[j,i]=copy.copy(input_data[j,i])
					elif self.mode==2:
						if not TFtable[j,i]:
							output_data[j,i]=[0,0,0]
			if len(input_data[0,0])==3:
				imOutput=Image.fromarray(output_data,mode='RGB')
			elif len(input_data[0,0])==4:
				imOutput=Image.fromarray(output_data,mode='RGBA')

			out_image=QFileDialog.getSaveFileName(None,"Save PNG Image","/home/lkit/Pictures",
				"Image Files (*.bmp *.jpg *.png *.xpm)")
			imOutput.save(str(out_image))
		else:
			self.warningMsg("Please choose select/mask mode")


	def genTFtable(self):
		def dist(x,y,X,Y,R):
		    return sqrt((x-X)**2+(y-Y)**2)<=R
		self.minX,self.maxX,self.minY,self.maxY=self.imagePanel.loadComputeRegion()

		points=np.asarray(self.imagePanel.loadArray())

		if self.mode==1:
			TFtable=np.asarray([[False for i in range(graphX)] for j in range(graphY)])
			mode_const=True
		elif self.mode==2:
			TFtable=np.asarray([[True for i in range(graphX)] for j in range(graphY)])
			mode_const=False

		for i in range(int(self.minX),int(self.maxX)):
			for j in range(int(self.minY),int(self.maxY)):
				for k0 in points:
					for k in k0:
						if dist(j,i,k[1],k[0],k[2]):
							TFtable[j,i]=mode_const
			print 'i=',i
		return TFtable

	def openImage(self):
		fname=QFileDialog.getOpenFileName(self,"Open image",
			"/home/lkit/Pictures","Image Files (*.bmp *.jpg *.png *.xpm)")
		self.input_image=fname
		if fname.isEmpty(): return None
		return QPixmap(fname)

	def keyPressEvent(self,event):
		if event.key()==Qt.Key_Escape:
			self.close()

	def exportWSLAP(self):
		def rebin(a, shape):
		    sh = shape[0],a.shape[0]//shape[0],shape[1],a.shape[1]//shape[1]
		    return a.reshape(sh).mean(-1).mean(1)
		if self.mode!=0:
			TFtable=self.genTFtable()
			
			input_fits=QFileDialog.getOpenFileName(self,"Open source FITS file",
				"/home/lkit/tmp","*.fits")
			f=pyfits.open(str(input_fits))
			input_data=np.asarray(f[0].data)
			f.close()			
			if self.mode==1:
				original_data=np.asarray([[0.0 for i in range(graphX)] for j in range(graphY)])
			else:
				original_data=copy.copy(input_fits)		

			# before resize
			for i in range(int(self.minX),int(self.maxX)):
				for j in range(int(self.minY),int(self.maxY)):
					if self.mode==1:
						if TFtable[j,i]:
							# print graphY,i,j
							original_data[graphY-j-1,i]=input_data[graphY-j-1,i]
					elif self.mode==2:
						if not TFtable[j,i]:
							original_data[graphY-j-1,i]=0.0
	
			targetX, targetY= 8,8

			layer=1
			file_mode=1
			output_data=rebin(original_data,(targetX,targetY))

			wslapName=QFileDialog.getSaveFileName(self,"Save mass layer file","/home/lkit/tmp")
			if file_mode==1:
				f=open(wslapName,'w')
			elif file_mode==2:
				f=open(wslapName,'a')
			for j in range(targetX):
				for i in range(targetY):
					f.write("\t\t%d\t\t%d\t%0.8f\t\t\t%d\n" %(j,i,output_data[j,i],layer))
			f.close()
		else:
			self.warningMsg("Please choose select/mask mode")

	def warningMsg(self,string):
		msgBox=QMessageBox()
		msgBox.setWindowTitle("Warning")
		msgBox.setText(string)
		msgBox.exec_()

	def helpFunc(self):
		msgBox=QMessageBox()
		msgBox.setWindowTitle("Help")
		msgBox.setText("<Keyboard>\n"
			"W:\tEnlarge image\nQ:\tShrink image\n"
			"F:\tIncrease brush size\nD:\tDecrease brush size\n"
			"U:\tUndo\n\n<Mouse>\n"
			"Left Click:\tSelect/Mask regions\n"
			"Right Click:\tSet as center")
		msgBox.exec_()


def main():        
    app=QApplication(sys.argv)
    ex=MainWindow()
    ex.show()
    app.exec_()
    app.deleteLater() 	# need this avoid error
    sys.exit()

if __name__=='__main__':
    main()		

