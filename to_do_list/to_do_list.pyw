import sys

import os
import math
import yaml
import os.path

sys.path.append(os.path.realpath('.'))
sys.path.append(os.path.realpath('../'))

from PyQt4.QtGui import * 
from PyQt4.QtCore import *

def sign(a):
  if a >= 0:
    return 1.0
  return -1.0

class ToDoList(QWidget):

  def __init__(self,parent=None):
    QWidget.__init__(self,parent)
    self.setWindowTitle("To Do")
    self.setFixedSize(300,300)
    self.setWindowFlags(Qt.FramelessWindowHint | self.windowFlags()) 
    n = 16
    points = QPolygon(n)
    for i in range(0,n):
      print math.cos(float(i)/float(n)*math.pi*2.0)
      c = math.cos(float(i)/float(n)*math.pi*2.0)
      s = math.sin(float(i)/float(n)*math.pi*2.0)
      c = math.sqrt(math.sqrt(math.fabs(c)))*sign(c) 
      s = math.sqrt(math.sqrt(math.fabs(s)))*sign(s)      
      points.setPoint(i,QPoint(self.width()/2.0+c*self.width()/2.0,self.height()/2.0+s*self.height()/2.0))
    mask = QRegion(points)
    self.setMask(mask)
    palette = self.palette()
    palette.setBrush(self.backgroundRole(), QBrush(QColor("#FF6")))
    self.setPalette(palette)
    self._isMoving = False
    self._position = None
  
    self._path = os.path.expanduser('~')+"/to_dos.txt"
    
    print self._path
  
    self.edit = QLineEdit()
    self.add = QPushButton("Add")
    self.connect(self.add,SIGNAL("clicked()"),self.addToDoItem)
    self.connect(self.edit,SIGNAL("returnPressed()"),self.addToDoItem)
    self.title = QLabel("To Do's")
    self.title.setAlignment(Qt.AlignCenter)
    styleSheet = """
    
    QListWidget{font-size:12px;}
        
    QLineEdit,QPushButton{
    margin:3px; padding:4px; font-size:12px; background:#FFF; border:0px solid #EEE; 
    }
     QPushButton:pressed {
     background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                       stop: 0 #dadbde, stop: 1 #f6f7fa);
 }
    
    QLabel{
      font-size:28px;
      text-align:left;
      font-weight:bold;
    }

    """
    self.toDos = QListWidget()
    self.toDos.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)     
    self.toDos.setWordWrap(True)
    self.toDos.setSpacing(4)
    self.done = QPushButton("Done")
    self.up = QPushButton("Up")
    self.down = QPushButton("Down")
    self.toDos.setAlternatingRowColors(True)
    self.setAttribute(Qt.WA_DeleteOnClose,False)
    self.setContentsMargins(2,2,2,2)
    
    self.buttonLayout = QGridLayout()
    
    box = QBoxLayout(QBoxLayout.LeftToRight)
    box.addWidget(self.done)
    box.addWidget(self.up)
    box.addWidget(self.down)
    

    self.connect(self.done,SIGNAL("clicked()"),self.deleteItems)
    self.connect(self.up,SIGNAL("clicked()"),self.moveItemsUp)
    self.connect(self.down,SIGNAL("clicked()"),self.moveItemsDown)
    
    self.pixmap = QPixmap(16,16)
    self.pixmap.fill(Qt.transparent)
    
    painter = QPainter(self.pixmap)
    painter.drawText(5,12,"-")
    
    painter.end()
    
    self.trayIcon = QSystemTrayIcon(QIcon(self.pixmap))
    self.trayIcon.show()
    
    self.menu = QMenu()
    showItem = self.menu.addAction("Show")
    exitItem = self.menu.addAction("Exit")
    
    self.connect(showItem,SIGNAL("triggered()"),lambda: self.show())
    self.connect(exitItem,SIGNAL("triggered()"),lambda: self.exit())
    self.connect(self.trayIcon,SIGNAL("activated(QSystemTrayIcon::ActivationReason)"),self.activated)
    
    self.trayIcon.setContextMenu(self.menu)
    
    self.setStyleSheet(styleSheet)    
    
    self.buttonLayout.addWidget(self.edit,0,0)
    self.buttonLayout.addWidget(self.add,0,1)
  
    self.layout = QGridLayout()
    self.layout.addWidget(self.title)
    self.layout.addItem(self.buttonLayout)
    self.layout.addWidget(self.toDos)
    self.layout.addItem(box)
    self.setLayout(self.layout)

    self._showedMessage = False
    
#    self.setWindowFlags(Qt.WindowStaysOnTopHint)
  
    self.loadToDos()
    
  def activated(self,reason):
    if reason == QSystemTrayIcon.DoubleClick:
      self.show()
    
  def exit(self):
    self.trayIcon.hide()
    exit(0)  
    
  def closeEvent(self,e):
    self.hide()
    if self._showedMessage == False:
      self._showedMessage = True
      self.trayIcon.showMessage("Minimized","The To-Do list has been minimized. Double-click on this icon to re-open it. Right click on the icon and select 'exit' to fully close the application.")
    e.ignore()
    
  def updateTrayBarIcon(self):
    self.pixmap.fill(Qt.transparent)
    painter = QPainter(self.pixmap)
    painter.drawText(5,12,str(self.toDos.count()))
    self.trayIcon.setIcon(QIcon(self.pixmap))
    
    
  def deleteItems(self):
    selectedItems = self.toDos.selectedItems()
    for item in selectedItems:
      self.toDos.takeItem(self.toDos.row(item))
    self.saveToDos()
    self.updateTrayBarIcon()
    
  def moveItemsUp(self):
    selectedItems = self.toDos.selectedItems()
    for item in selectedItems:
      row = self.toDos.row(item)
      if row > 0:
        self.toDos.takeItem(row)
        self.toDos.insertItem(row-1,item)
      self.toDos.setCurrentItem(item)
    self.saveToDos()
    
  def saveToDos(self):
    toDos = list()
    for i in range(0,self.toDos.count()):
      toDos.append(str(self.toDos.item(i).text().toUtf8()))
    yaml.dump(toDos,open(self._path,'w'))
    
  def loadToDos(self):
    try:
      if not os.path.exists(self._path): 
        return 
      toDos = yaml.load(open(self._path,'r'))
      print toDos
      self.toDos.clear()
      for toDo in toDos:
        self.toDos.addItem(QString().fromUtf8(toDo))
      self.updateTrayBarIcon()
    except:
      print sys.exc_info()
      pass
         
    
  def moveItemsDown(self):
    selectedItems = self.toDos.selectedItems()
    selectedItems.reverse()
    for item in selectedItems:
      row = self.toDos.row(item)
      if row <= self.toDos.count():
        self.toDos.takeItem(row)
        self.toDos.insertItem(row+1,item)
      self.toDos.setCurrentItem(item)
    self.saveToDos()
    
  def addToDoItem(self):
    text = self.edit.text()
    if self.toDos.findItems(text,Qt.MatchExactly) == [] and text != "":
      self.edit.setText("")
      self.toDos.insertItem(0,text)
      self.updateTrayBarIcon()
    self.saveToDos()
    
  def updateGeometry(self):
    pass
  
  def mousePressEvent(self,e):
    print "Checking..."
    if e.button() == Qt.LeftButton:
      print "Starting to move..."
      self._isMoving = True
      self._position = e.pos()
    
  def mouseMoveEvent(self,e):
    if e.buttons() & Qt.LeftButton and self._isMoving:
      self.move(self.pos()+e.pos()-self._position)
    
  def mouseReleaseEvent(self,e):
    if e.button() == Qt.LeftButton:
      self._isMoving = False
  
if __name__ == '__main__':
  qApp = QApplication(sys.argv)
  QApplication.setStyle(QStyleFactory.create("QMacStyle"))

  MyToDoList = ToDoList()  
  MyToDoList.show()

  qApp.exec_()