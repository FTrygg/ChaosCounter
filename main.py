from PyQt5.QtWidgets import * 
from PyQt5.QtGui import * 
from PyQt5.QtCore import * 
import traceback, sys, os
import cv2 as cv
import numpy as np
import pyautogui
import operator
from pyqtkeybind import keybinder
import sys

#debug flag just used for me when I want to test pictures prior to packing the program
DEBUG = False


#trade window values for 1080p. Will soon move out from here
tradeWindowMainAnchor = (282,69) #coordinates of upper left corner of the main trade window
tradePartnerAnchor = (29,135)   #coordinates of upper left corner of trade partner window
tradePartnerAnchorBottomRight = (660,397) #coordinates of bottom right corner of trade partner window
ownTradeAnchor = (29,466) #coordinates of upper left corner of own trade window
ownTradeAnchorButtomRight = (660,728) #coordinates of bottom right corner of own trade window
invAnchor = (1272,588)      #upper left corner of inventory in the bottom right
invAnchorButtonRight = (1902,849) #coordinates of bottom right corner of the main inventory in the bottom right
offset = 52.5               
margin = 0                  #border between single stacks

#overlaysize and coordinates within the overlay graphic
ov = (972,803) 
tradePartnerSummaryAnchor = (694,135)
tradePartnerSummaryBottomRight = (946,397)
ownInventorySummaryAnchor  = (694,466)
ownInventorySummaryBottomRight = (946,728)

#these are set in stone, not to change
inventoryRows = 12
inventoryColumns = 5
inventoryBoxes = inventoryRows*inventoryColumns

#settings where to save all the stuff
settings = QSettings('studentTech', 'ChaosCounter')

#function used for me so that I dont manually have to type every single path in the .spec file
def printSpecPath(absolutePath,name):
    print("('"+name+"','"+absolutePath+"', 'Data'),")

#Get absolute path to resource for PyInstaller
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

#this is needed to gain access to global hotkeys, as PyQt5's keybinds only work if the window is in focus
class WinEventFilter(QAbstractNativeEventFilter):
    def __init__(self, keybinder):
        self.keybinder = keybinder
        super().__init__()

    def nativeEventFilter(self, eventType, message):
        ret = self.keybinder.handler(eventType, message)
        return ret, 0

#signals for the individual workers
class WorkerSignals(QObject):
    
    outputSignal = pyqtSignal(int,int,int)

#single tile evaluater
class SnipWorker(QRunnable):
    def __init__(self,snipNo,snipToEval,currencyFirstPicture,currency):
        super(SnipWorker, self).__init__()
        self.snipNo = snipNo
        self.snipToEval = snipToEval
        self.currencyFirstPicture = currencyFirstPicture
        self.currency = currency
        self.signals = WorkerSignals()

    def run(self):
        self.match = 0
        self.mostlikelyStack = None
        self.requiredConfidence = 0.88
        
        #check first pictures (the ones without any number) first to minimize calculation time
        for img, position in zip(self.currencyFirstPicture, range(0,len(self.currencyFirstPicture))):
            self.result = cv.matchTemplate(self.snipToEval,img, cv.TM_CCORR_NORMED)

            if self.result.max() > self.match:
                self.match = self.result.max()
                self.mostlikelyStack = position
            
            if self.match > self.requiredConfidence:
                break
        
        #if likely one of the included currencies or empty:
        if self.match > self.requiredConfidence:
            #if empty
            if self.mostlikelyStack == 0:
                self.signals.outputSignal.emit(self.snipNo,0,0)

            #if a currency
            else:
                self.amountMatch = 0
                self.bestMatchIndex = 0
                self.currencyStackToEval = self.currency[self.mostlikelyStack]
                for curAmount, ind in zip(self.currencyStackToEval, range(0,len(self.currencyStackToEval))):
                    self.localMatch = cv.matchTemplate(self.snipToEval,curAmount, cv.TM_CCORR_NORMED).max()
                    if self.localMatch > self.amountMatch:
                        self.amountMatch = self.localMatch
                        self.bestMatchIndex = ind

                #account for reverse order in currency list
                self.signals.outputSignal.emit(self.snipNo,self.mostlikelyStack,len(self.currencyStackToEval)-self.bestMatchIndex)

        #if not empty but no currency
        else:
            self.emptyPic = self.currencyFirstPicture[0]
            self.result = cv.matchTemplate(self.snipToEval,self.emptyPic, cv.TM_CCORR_NORMED)
            if self.result.max() > 0.8:
                self.signals.outputSignal.emit(self.snipNo,0,0)
            else:
                self.signals.outputSignal.emit(self.snipNo,len(self.currencyFirstPicture)+1,0)
                
class DonateWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        #if running with debug flag, use hard coded path, else look for path in .spec file. 
        if DEBUG:
            self.backgroundImage = QImage("Hardcodedpath, hidden here because it uses my network drive")
        else:
            self.backgroundImage = QImage(resource_path("DonateWindowBackground.png"))

        self.backgroundImage = self.backgroundImage.scaled(QSize(800,900)) 
        self.palette1 = QPalette()
        self.palette1.setBrush(10, QBrush(self.backgroundImage))                     # 10 = Windowrole
        self.setPalette(self.palette1)
        # setting geometry 
        self.setFixedSize(800,900)
        self.setWindowFlag(Qt.FramelessWindowHint)

        self.createExitButton()
        self.createDonateText()
        self.createDonateButton()
        self.createGitHubButton()

    def createExitButton(self):
        self.closeButton = QPushButton("", self) 
        self.closeButton.setGeometry(800-(38+5), 11, 30, 30) 
        self.closeButton.setFlat(True)
        self.closeButton.clicked.connect(self.closeDonation) 

        #if running with debug flag, use hard coded path, else look for path in .spec file. 
        if DEBUG:
            self.backgroundImage = QImage("Hardcodedpath, hidden here because it uses my network drive")
        else:
            self.backgroundImage = QImage(resource_path("CloseButtonBackground.png"))
        self.backgroundImage = self.backgroundImage.scaled(QSize(30,30)) 
        self.palette1 = QPalette()
        self.palette1.setBrush(1,QBrush(self.backgroundImage))                     # 1 = Buttonrole
        self.closeButton.setPalette(self.palette1)
        self.closeButton.setAutoFillBackground(True)

    def createDonateText(self):   
        self.border = 50
        self.donationText = QLabel(self)
        self.donationText.setGeometry(8+self.border,89,784-self.border*2,802)
        self.donationText.setStyleSheet("color : rgb(254,192,118); background: transparent;")
        self.donationText.setAlignment(Qt.AlignCenter)
        self.donationText.setText(self.text())  
        self.donationText.setWordWrap(True)
        self.donationText.setFont(QFont("Courier",int(9)))

    def createDonateButton(self):
        self.donateButton = QPushButton("", self) 
        self.width = 300
        self.donateButton.setGeometry(int(800/2-self.width/2),700,self.width, int(self.width/2000*560)) 
        self.donateButton.setFlat(True)
        self.donateButton.clicked.connect(self.openDonationWebbrowser) 

        #if running with debug flag, use hard coded path, else look for path in .spec file. 
        if DEBUG:
            self.backgroundImage = QImage("Hardcodedpath, hidden here because it uses my network drive")
        else:
            self.backgroundImage = QImage(resource_path("PayPalButton.png"))
        self.backgroundImage = self.backgroundImage.scaled(QSize(self.width, int(self.width/2000*560))) 
        self.palette1 = QPalette()
        self.palette1.setBrush(1,QBrush(self.backgroundImage))                     # 1 = Buttonrole
        self.donateButton.setPalette(self.palette1)
        self.donateButton.setAutoFillBackground(True)

    def createGitHubButton(self):
        self.gitHubButton = QPushButton("", self) 
        self.width = 300
        self.gitHubButton.setGeometry(int(800/2-self.width/2),790,self.width, int(self.width/2000*560)) 
        self.gitHubButton.setFlat(True)
        self.gitHubButton.clicked.connect(self.openGitHubWebbrowser) 

        #if running with debug flag, use hard coded path, else look for path in .spec file. 
        if DEBUG:
            self.backgroundImage = QImage("Hardcodedpath, hidden here because it uses my network drive")
        else:
            self.backgroundImage = QImage(resource_path("GitHubButton.png"))
        self.backgroundImage = self.backgroundImage.scaled(QSize(self.width, int(self.width/2000*560))) 
        self.palette1 = QPalette()
        self.palette1.setBrush(1,QBrush(self.backgroundImage))                     # 1 = Buttonrole
        self.gitHubButton.setPalette(self.palette1)
        self.gitHubButton.setAutoFillBackground(True)

    def text(self):
        txt = "This program was made by a student who needed an excuse to improve his programming skills. " 
        txt += "While I tried everything to make this program as good as possible, it is far from perfect as it relies "
        txt += "on visual only data, rather than accessing memory. "
        txt += "This on the other hand should make this tool tolerated by the terms of PoE. " 
        txt += "I am no expert at this, please enlighten me if that is not the case. " 
        txt += "Enjoy my medium effort graphics and complete absense of GUI experience.\n\n"

        txt += "My main motivation to create this tool was my questionable interactions while trading " 
        txt += "combined with the bot discussion during the Harvest league. " 
        txt += "I though, that if we make trading for human players a bit more accessible, " 
        txt += "players won't be inclined to move this over to bots. " 
        txt += "I am aware, that my program could be abused by exactly those "
        txt += "and as a results I won't share my source code.\n\n"

        txt += "If you have issues spending your money after buying every single supporter pack, "
        txt += "feel free to donate me something so that maybe I will be able to afford one at some point. "
        txt += "In that case thank you, if not, no hard feelings, I am a student myself ;)\n\n"

        txt += "Have a good one!"
        return txt
    
    def closeDonation(self):
        self.hide()

    def openDonationWebbrowser(self):
        QDesktopServices.openUrl(QUrl('https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=YUXL8CBVZJ94C&source=url'))

    def openGitHubWebbrowser(self):
        QDesktopServices.openUrl(QUrl('https://github.com/FTrygg/ChaosCounter'))

class SetupWindow(QMainWindow):
    startClicked = pyqtSignal()
    resolution = pyqtSignal(str)
    popupOnStart = pyqtSignal(bool)
    donationClicked = pyqtSignal()
    def __init__(self): 
        super().__init__() 
        # setting title 
        self.setWindowTitle("Chaos Counter") 
        self.setWindowIcon(QIcon(resource_path('CCIcon.png')))
        #if running with debug flag, use hard coded path, else look for path in .spec file. 
        if DEBUG:
            self.backgroundImage = QImage("Hardcodedpath, hidden here because it uses my network drive")
        else:
            self.backgroundImage = QImage(resource_path("StartWindowBackground.png"))

        self.backgroundImage = self.backgroundImage.scaled(QSize(600,800)) 
        self.palette1 = QPalette()
        self.palette1.setBrush(10, QBrush(self.backgroundImage))                     # 10 = Windowrole
        self.setPalette(self.palette1)

        # setting geometry 
        self.setFixedSize(600,800)
        self.setWindowFlag(Qt.FramelessWindowHint)
  
        # calling method to setup the rest of GUI
        self.UiComponents() 

    def UiComponents(self): 
        # creating a start button 
        self.startButton = QPushButton("", self) 
        self.startButton.setGeometry(198, 670, 205, 52) 
        self.startButton.setFlat(True)
        self.startButton.clicked.connect(self.startApplication) 

        if DEBUG:
            self.backgroundImage = QImage("Hardcodedpath, hidden here because it uses my network drive")
        else:
            self.backgroundImage = QImage(resource_path("StartButtonBackground.png"))
        self.backgroundImage = self.backgroundImage.scaled(QSize(205,52)) 
        self.palette1 = QPalette()
        self.palette1.setBrush(1,QBrush(self.backgroundImage))                     # 1 = Buttonrole
        self.startButton.setPalette(self.palette1)
        self.startButton.setAutoFillBackground(True)
        
        # creating a exit button 
        self.closeButton = QPushButton("", self) 
        self.closeButton.setGeometry(600-(38+5), 18, 37, 37) 
        self.closeButton.setFlat(True)
        self.closeButton.clicked.connect(self.exitProgram) 

        #if running with debug flag, use hard coded path, else look for path in .spec file. 
        if DEBUG:
            self.backgroundImage = QImage("Hardcodedpath, hidden here because it uses my network drive")
        else:
            self.backgroundImage = QImage(resource_path("CloseButtonBackground.png"))
        self.backgroundImage = self.backgroundImage.scaled(QSize(37,37)) 
        self.palette1 = QPalette()
        self.palette1.setBrush(1,QBrush(self.backgroundImage))                     # 1 = Buttonrole
        self.closeButton.setPalette(self.palette1)
        self.closeButton.setAutoFillBackground(True)
        
        
        # creating selection box
        self.listBox = QListWidget(self)
        self.listBox.setGeometry(300-int(136/2),530,136, 121)
        self.listBox.setStyleSheet("QListWidget { border: none;} QListView::item:selected{background-color: rgb(105,50,8);} ") 

        #if running with debug flag, use hard coded path, else look for path in .spec file. 
        if DEBUG:
            self.backgroundImage = QImage("Hardcodedpath, hidden here because it uses my network drive")
        else:
            self.backgroundImage = QImage(resource_path("ComboBoxBackground.png"))
        self.backgroundImage = self.backgroundImage.scaled(QSize(136,121)) 
        self.palette1 = QPalette()
        self.palette1.setBrush(9,QBrush(self.backgroundImage))      # 9 = Listboxrole
        self.palette1.setBrush(10,QBrush(QColor(255, 0, 0, 0)))     # 10 = General Background Role            
        self.listBox.setPalette(self.palette1)
        self.listBox.setAutoFillBackground(True)
        
        #resolutions in box
        listItems = (
            "1920x1080",
            "2560x1440")

        for element, pos in zip(listItems,range(0,len(listItems))):
            item = QListWidgetItem(element)
            item.setTextAlignment(Qt.AlignCenter)
            item.setForeground(QBrush(QColor(231,180,119)))
            self.listBox.insertItem(pos,item)
        
        self.checkBox = QRadioButton(self)
        self.checkBox.setGeometry(300-80, 655, 14, 14) 
        self.checkBox.setStyleSheet("QRadioButton::indicator:unchecked {background-color: rgb(254,192,118);}QRadioButton::indicator:checked {background-color: rgb(105,50,8); border: 3px solid rgb(254,192,118);}")
        
    
        #create label with text not to show again on next start up
        note = QLabel(self)
        note.setGeometry(300-80+16,654,165,17)
        note.setStyleSheet("color : rgb(254,192,118); background: transparent;")
        note.setText("Do not show again next time")  
        
        #creat more info button
        self.infobutton = QPushButton(self)
        self.infobutton.setGeometry(600-(38+40), 21, 30, 30) 
        self.infobutton.setFlat(True)
        self.infobutton.clicked.connect(self.openDonationWindow) 

        #if running with debug flag, use hard coded path, else look for path in .spec file. 
        if DEBUG:
            self.backgroundImage = QImage("Hardcodedpath, hidden here because it uses my network drive")
        else:
            self.backgroundImage = QImage(resource_path("InfoButton.png"))
        self.backgroundImage = self.backgroundImage.scaled(QSize(30,30)) 
        self.palette1 = QPalette()
        self.palette1.setBrush(1,QBrush(self.backgroundImage))                     # 1 = Buttonrole
        self.infobutton.setPalette(self.palette1)
        self.infobutton.setAutoFillBackground(True)

    def openDonationWindow(self):
        self.donationClicked.emit()

    def startApplication(self): 
        #make sure a resolution is set
        if len(self.listBox.selectedItems()) != 0:
            self.startClicked.emit()
            for entry in self.listBox.selectedItems():
                self.resolution.emit(entry.text())
            if self.checkBox.isChecked():
                self.popupOnStart.emit(False)
            else:
                self.popupOnStart.emit(True)
        else:
            msg = QMessageBox()
            msg.setWindowTitle("No Selection")
            msg.setText("Plese select your resolution first!")
            x = msg.exec_()

    def exitProgram(self):
        print("exiting program...") 
        sys.exit()
  
class OverlayWindow(QMainWindow):
    newRequestSignal = pyqtSignal()
    doneComputing = pyqtSignal()
    openSettings = pyqtSignal()
    def __init__(self): 
        super().__init__() 
        
        self.tradePartnerInventoryEvaluatedContent = []
        self.ownInventoryEvaluatedContent = []
        self.currencyIncluded = []
        self.initCurrency()
        self.currencyIcons = self.importCurrencyIcons()

        self.threadpool = QThreadPool()
        #print("overlay window running threaded:")
        #print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())
        
        self.setWindowTitle("Trade evaluation") 
        self.setGeometry(tradeWindowMainAnchor[0],tradeWindowMainAnchor[1],ov[0],ov[1])

        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(ov[0],ov[1]) 
        self.setWindowFlag(Qt.FramelessWindowHint)

        self.newRequestSignal.connect(self.evaluateContent)
        self.doneComputing.connect(self.updateGUIInventory)
        self.loadCurrencyPictures()
        self.setWindowIcon(QIcon(resource_path('CCIcon.png')))
  
        # calling method 
        self.UiComponents() 

    def initCurrency(self):
        #all currencies here, excluded if pictures are missing 
        #                              name maxstack short
        self.currencyIncluded.append(("Empty",1,""))
        self.currencyIncluded.append(("OrbofAlteration",20,"Alt"))
        self.currencyIncluded.append(("OrbofFusing",20,"Fuse"))
        self.currencyIncluded.append(("OrbofAlchemy",10,"Alc"))
        self.currencyIncluded.append(("ChaosOrb",10,"C"))
        #self.currencyIncluded.append(("GemcuttersPrism",20))
        #self.currencyIncluded.append(("ExaltedOrb",10))
        self.currencyIncluded.append(("ChromaticOrb",20,"Chrom"))
        self.currencyIncluded.append(("JewellersOrb",20,"Jew"))
        self.currencyIncluded.append(("OrbofChance",20,"Chance"))
        self.currencyIncluded.append(("CartographersChisel",20,"Chisel"))
        self.currencyIncluded.append(("OrbofScouring",30,"Scour"))
        self.currencyIncluded.append(("BlessedOrb",20,"Blessed"))
        #self.currencyIncluded.append(("OrbofRegret",40))
        self.currencyIncluded.append(("RegalOrb",10,"Regal"))
        #self.currencyIncluded.append(("DivineOrb",10))
        self.currencyIncluded.append(("VaalOrb",10,"Vaal"))
        self.currencyIncluded.append(("SacrificeatDusk",1,"Dusk"))
        self.currencyIncluded.append(("SacrificeatMidnight",1,"Midnight"))
        self.currencyIncluded.append(("SacrificeatDawn",1,"Dawn"))
        self.currencyIncluded.append(("SacrificeatNoon",1,"Noon"))
        self.currencyIncluded.append(("MortalGrief",1,"Grief"))
        self.currencyIncluded.append(("MortalRage",1,"Rage"))
        self.currencyIncluded.append(("MortalHope",1,"Hope"))
        self.currencyIncluded.append(("MortalIgnorance",1,"Ignorance"))
        #self.currencyIncluded.append(("EbersKey",1))
        #self.currencyIncluded.append(("Yrielskey",1))
        #self.currencyIncluded.append(("InyasKey",1))
        #self.currencyIncluded.append(("VolkuursKey",1))
        self.currencyIncluded.append(("OfferingtotheGoddess",1,"Offer"))
        #self.currencyIncluded.append(("FragmentoftheHydra",1))
        #self.currencyIncluded.append(("FragmentofthePhoenix",1))
        #self.currencyIncluded.append(("FragmentoftheMinotaur",1))
        #self.currencyIncluded.append(("FragmentoftheChimera",1))
        self.currencyIncluded.append(("SimpleSextant",10,"S.Sex"))
        self.currencyIncluded.append(("PrimeSextant",10,"P.Sex"))
        self.currencyIncluded.append(("AwakenedSextant",10,"A.Sex"))
        #self.currencyIncluded.append(("OrbofAnnulment",20))
        self.currencyIncluded.append(("OrbofHorizons",20,"Hor"))
        #self.currencyIncluded.append(("HarbringersOrb",20))
        #self.currencyIncluded.append(("AncientOrb",20))
        self.currencyIncluded.append(("SilverCoin",30,"Silver"))

    def importCurrencyIcons(self):
        self.icons = []

        for currency in self.currencyIncluded:
            self.filename = str(currency[0] + ".png")
            #if running with debug flag, use hard coded path, else look for path in .spec file. 
            if DEBUG:
                self.iconRootFolder = "Hardcodedpath, hidden here because it uses my network drive"
                self.loc = self.iconRootFolder +  self.filename
                self.icon = QIcon(self.loc)
                printSpecPath(self.loc,self.filename)
            else:
                self.icon = QIcon(resource_path(self.filename))

            self.icons.append(self.icon)   
 
        return self.icons

    def UiComponents(self):
        self.BackgroundPhoto = QLabel(self)
        self.BackgroundPhoto.setGeometry(0,0,ov[0],ov[1])
    
        #if running with debug flag, use hard coded path, else look for path in .spec file. 
        if DEBUG:
            self.backgroundImage = QImage("Hardcodedpath, hidden here because it uses my network drive")
        else:
            self.backgroundImage = QImage(resource_path("OverlayBackground.png"))
        self.backgroundImage = self.backgroundImage.scaled(QSize(ov[0],ov[1])) 
        self.palette1 = QPalette()
        self.palette1.setBrush(10,QBrush(self.backgroundImage))         
        self.BackgroundPhoto.setPalette(self.palette1)
        self.BackgroundPhoto.setAutoFillBackground(True)

        
        # creating a exit button 
        self.closeButton = QPushButton("", self) 
        self.closeButton.setGeometry(int(ov[0]*0.96),int(ov[1]*0.015), 30, 30) 
        self.closeButton.setFlat(True)
        self.closeButton.clicked.connect(self.closeOverlay) 

        if DEBUG:
            self.backgroundImage = QImage("Hardcodedpath, hidden here because it uses my network drive")
        else:
            self.backgroundImage = QImage(resource_path("CloseButtonBackground.png"))

        self.backgroundImage = self.backgroundImage.scaled(QSize(30,30)) 
        self.palette1 = QPalette()
        self.palette1.setBrush(1,QBrush(self.backgroundImage))                     # 1 = Buttonrole
        self.closeButton.setPalette(self.palette1)
        self.closeButton.setAutoFillBackground(True)

        #create array of labels for partner inventory
        self.tradePartnerInventoryBoxes = self.createGrid(tradePartnerAnchor,tradePartnerAnchorBottomRight)
        self.ownInventoryBoxes = self.createGrid(ownTradeAnchor,ownTradeAnchorButtomRight)

        #create listbos for summary of trade partner
        self.tradePartnerSummary = QListWidget(self)
        self.tradePartnerSummarySize = tuple(map(operator.sub, tradePartnerSummaryBottomRight,tradePartnerSummaryAnchor ))
        self.tradePartnerSummary.setGeometry(tradePartnerSummaryAnchor[0], tradePartnerSummaryAnchor[1], self.tradePartnerSummarySize[0], self.tradePartnerSummarySize[1] )
        self.tradePartnerSummary.setStyleSheet("background-color : rgba(255,255,255,0); border : none; color : rgb(231,180,119);")
        self.tradePartnerSummary.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.tradePartnerSummary.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        #create listbos for summary of own inventory
        self.ownInventorySummary = QListWidget(self)
        self.ownInventorySummarySize = tuple(map(operator.sub, ownInventorySummaryBottomRight,ownInventorySummaryAnchor ))
        self.ownInventorySummary.setGeometry(ownInventorySummaryAnchor[0], ownInventorySummaryAnchor[1], self.ownInventorySummarySize[0], self.ownInventorySummarySize[1] )
        self.ownInventorySummary.setStyleSheet("background-color : rgba(255,255,255,0); border : none; color : rgb(231,180,119);")
        self.ownInventorySummary.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.ownInventorySummary.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        #create settings button
        self.settingsButton = QPushButton(self)
        self.settingsButton.setGeometry(int(ov[0]*0.91),int(ov[1]*0.015)+2, 25, 25) 
        self.settingsButton.setFlat(True)
        self.settingsButton.clicked.connect(self.requestSettings)

        #if running with debug flag, use hard coded path, else look for path in .spec file. 
        if DEBUG:
            self.backgroundImage = QImage("Hardcodedpath, hidden here because it uses my network drive")
        else:
            self.backgroundImage = QImage(resource_path("SettingsButton.png"))
            
        self.backgroundImage = self.backgroundImage.scaled(QSize(25,25)) 
        self.palette1 = QPalette()
        self.palette1.setBrush(1,QBrush(self.backgroundImage))                     # 1 = Buttonrole
        self.settingsButton.setPalette(self.palette1)
        self.settingsButton.setAutoFillBackground(True)

        #create refresh button
        self.refreshButton = QPushButton(self)
        self.refreshButton.setGeometry(int(ov[0]*0.22),int(ov[1]*0.935)+1, 42, 42) 
        self.refreshButton.setFlat(True)
        self.refreshButton.clicked.connect(self.evaluateContent)

        if DEBUG:
            self.backgroundImage = QImage("Hardcodedpath, hidden here because it uses my network drive")
        else:
            self.backgroundImage = QImage(resource_path("RefreshButton.png"))
            
        self.backgroundImage = self.backgroundImage.scaled(QSize(42,42)) 
        self.palette1 = QPalette()
        self.palette1.setBrush(1,QBrush(self.backgroundImage))                     # 1 = Buttonrole
        self.refreshButton.setPalette(self.palette1)
        self.refreshButton.setAutoFillBackground(True)
        
        #create ok Button
        self.okButton = QPushButton("", self)  
        self.okButton.setGeometry(int(ov[0]*0.01),int(ov[1]*0.935), 200, 45) 
        self.okButton.setFlat(True)
        self.okButton.clicked.connect(self.closeOverlay)
        
        if DEBUG:
            self.backgroundImage = QImage("Hardcodedpath, hidden here because it uses my network drive")
        else:
            self.backgroundImage = QImage(resource_path("OkButton.png"))
            
        self.backgroundImage = self.backgroundImage.scaled(QSize(200,45)) 
        self.palette1 = QPalette()
        self.palette1.setBrush(1,QBrush(self.backgroundImage))                     # 1 = Buttonrole
        self.okButton.setPalette(self.palette1)
        self.okButton.setAutoFillBackground(True)
       
    def requestSettings(self):
        self.openSettings.emit()

    def createGrid(self, startCoord, endCoord):

        self.grid = []
        self.deltaX = (endCoord[0] - startCoord[0])/inventoryRows
        self.deltaY = (endCoord[1] - startCoord[1])/inventoryColumns
        self.anchor = startCoord

        for box in range(0,inventoryBoxes):
            self.offset = (int(box//inventoryColumns*(self.deltaX)),int(box%inventoryColumns*(self.deltaY)))  
            self.start = tuple(map(operator.add, self.anchor, self.offset ))
 
            self.boxLabel = QLabel(self)
            self.boxLabel.setAlignment(Qt.AlignCenter | Qt.AlignBottom)
            self.boxLabel.setFont(QFont("Courier",int(self.deltaX/15)))
            self.boxLabel.setGeometry(self.start[0],self.start[1],int(self.deltaX),int(self.deltaY))
            self.boxLabel.setStyleSheet("QLabel { background-color : rgba(255,0,0,120); color : white; }")
            self.grid.append(self.boxLabel)
            
        return self.grid

    def closeOverlay(self):
        self.hide()

    def updateGUIInventory(self):
        self.tradePartnerInventoryEvaluatedContent.sort()
        self.ownInventoryEvaluatedContent.sort()
        self.summedUpCurrencyTradePartner = [0] * len(self.currencyIncluded)
        self.summedUpCurrencyOwn = [0] * len(self.currencyIncluded)

        for content, label in zip(self.tradePartnerInventoryEvaluatedContent, self.tradePartnerInventoryBoxes):
            self.currency = content[1]
            self.amount = content[2]

            #if no currency detected, but clear inventory
            if self.currency == 0:
                
                label.setText("empty")
                label.setStyleSheet("background-color : rgba(128,128,128,50); color : grey;")
                
            #if currency inside  
            elif 0 < self.currency < len(self.currencyIncluded): 
                #full stack
                if self.amount == self.currencyIncluded[self.currency][1]:
                    label.setStyleSheet("background-color : rgba(0,255,0,50); color : white;")

                else:
                    label.setStyleSheet("background-color : rgba(255,255,0,50); color : white;")
                    
                self.labelText = self.currencyIncluded[self.currency][2] + ":" + str(self.amount)
                label.setText(self.labelText)

                #add to summed up list
                self.summedUpCurrencyTradePartner[self.currency] += self.amount

            #if empty
            elif self.currency == (len(self.currencyIncluded)+1):
                label.setStyleSheet("background-color : rgba(255,0,0,50); color : white;")
                self.labelText = "n.a." 
                label.setText(self.labelText)

        for content, label in zip(self.ownInventoryEvaluatedContent, self.ownInventoryBoxes):
            self.currency = content[1]
            self.amount = content[2]

            #if no currency detected, but clear inventory
            if self.currency == 0:
                label.setText("empty")
                label.setStyleSheet("background-color : rgba(128,128,128,50); color : grey;")
                
            #if currency inside 
            elif 0 < self.currency < len(self.currencyIncluded): 
                if self.amount == self.currencyIncluded[self.currency][1]:
                    label.setStyleSheet("background-color : rgba(0,255,0,50); color : white;")
                else:
                    label.setStyleSheet("background-color : rgba(255,255,0,50); color : white;")
                    
                self.labelText = self.currencyIncluded[self.currency][2] + ":" + str(self.amount)
                label.setText(self.labelText)

                #add to summed up list
                self.summedUpCurrencyOwn[self.currency] += self.amount

            #if empty
            elif self.currency == (len(self.currencyIncluded)+1):
                label.setStyleSheet("background-color : rgba(255,0,0,50); color : white;")
                self.labelText = "n.a." 
                label.setText(self.labelText)

        #now update summary

        #trade partner
        self.listmemebers = len([x for x in self.summedUpCurrencyTradePartner if x > 0])
        self.width = self.tradePartnerSummary.width()
        self.height = self.tradePartnerSummary.height()/self.listmemebers if self.listmemebers > 0 else 0
        self.height = self.tradePartnerSummary.height()/3 if self.listmemebers <3 else self.height

        self.tradePartnerSummary.setIconSize(QSize(self.width,int(self.height)))
        self.tradePartnerSummary.setFont(QFont("Courier",int(self.height/3)))
        self.tradePartnerSummary.clear()

        for cur, ind in zip(self.summedUpCurrencyTradePartner,range(0,len(self.summedUpCurrencyTradePartner))):
            #if something is found in the trade screen
            if cur > 0:
                self.item = QListWidgetItem()
                self.item.setSizeHint(QSize(int(self.width),int(self.height)))
                self.item.setIcon(self.currencyIcons[ind])
                self.item.setText(" x " + str(cur))
                self.item.setFlags(self.item.flags() & ~Qt.ItemIsSelectable)
                self.tradePartnerSummary.addItem(self.item)

        #own inventory
        self.listmemebers = len([x for x in self.summedUpCurrencyOwn if x > 0])
        self.width = self.ownInventorySummary.width()
        self.height = self.ownInventorySummary.height()/self.listmemebers if self.listmemebers > 0 else 0
        self.height = self.ownInventorySummary.height()/3 if self.listmemebers <3 else self.height

        self.ownInventorySummary.setIconSize(QSize(self.width,int(self.height)))
        self.ownInventorySummary.setFont(QFont("Courier",int(self.height/3)))
        self.ownInventorySummary.clear()

        for cur, ind in zip(self.summedUpCurrencyOwn,range(0,len(self.summedUpCurrencyOwn))):
            #if something is found in the trade screen
            if cur > 0:
                self.item = QListWidgetItem()
                self.item.setSizeHint(QSize(int(self.width),int(self.height)))
                self.item.setIcon(self.currencyIcons[ind])
                self.item.setText(" x " + str(cur))
                self.item.setFlags(self.item.flags() & ~Qt.ItemIsSelectable)
                self.ownInventorySummary.addItem(self.item)
                      
    def evaluateContent(self):
        self.hide()
        screenshot = self.getScreen()
        self.show()
        self.activateWindow()
        
        #clear previous content
        self.tradePartnerInventoryEvaluatedContent = []
        self.ownInventoryEvaluatedContent = []

        #start with the trading partern's inventory
        for square in range(0,inventoryBoxes):
            offsetFromAnchor = self.findBox(square,tradePartnerAnchor,tradePartnerAnchorBottomRight)
            start = tuple(map(operator.add, tradeWindowMainAnchor, tradePartnerAnchor))
            start = tuple(map(operator.add, start, offsetFromAnchor[0]))

            end = tuple(map(operator.add, tradeWindowMainAnchor, tradePartnerAnchor))
            end = tuple(map(operator.add, end, offsetFromAnchor[1]))
            snip = screenshot[start[1]:end[1],start[0]:end[0]]

            self.worker = SnipWorker(square,snip,self.allCurrenciesLowerHalf,self.allCurrencies)
            self.worker.signals.outputSignal.connect(self.handleSnipWorkerOutputTradePartner)
            self.threadpool.start(self.worker)

        #now looking at the own inventory
        for square in range(0,inventoryBoxes):
            offsetFromAnchor = self.findBox(square,ownTradeAnchor,ownTradeAnchorButtomRight)
            start = tuple(map(operator.add, tradeWindowMainAnchor, ownTradeAnchor))
            start = tuple(map(operator.add, start, offsetFromAnchor[0]))

            end = tuple(map(operator.add, tradeWindowMainAnchor, ownTradeAnchor))
            end = tuple(map(operator.add, end, offsetFromAnchor[1]))
            snip = screenshot[start[1]:end[1],start[0]:end[0]]

            self.worker = SnipWorker(square,snip,self.allCurrenciesLowerHalf,self.allCurrencies)
            self.worker.signals.outputSignal.connect(self.handleSnipWorkerOutputOwnInventory)
            self.threadpool.start(self.worker)

    def handleSnipWorkerOutputTradePartner(self, square, currency, amount):
        self.tradePartnerInventoryEvaluatedContent.append((square,currency, amount))

        if (len(self.tradePartnerInventoryEvaluatedContent) == inventoryBoxes) and (len(self.ownInventoryEvaluatedContent) == inventoryBoxes):
            self.doneComputing.emit()

    def handleSnipWorkerOutputOwnInventory(self, square, currency, amount):
        self.ownInventoryEvaluatedContent.append((square,currency, amount))
        if (len(self.tradePartnerInventoryEvaluatedContent) == inventoryBoxes) and (len(self.ownInventoryEvaluatedContent) == inventoryBoxes):
            self.doneComputing.emit()

    def loadCurrencyPictures(self):
        self.allCurrencies = [] 
        self.allCurrenciesLowerHalf = []

        for cur in self.currencyIncluded:
            picName = str(cur[0]+".png")
            self.allCurrencies.append(self.importStacksFromSinglePicture(picName, cur[1] , invAnchor,margin,offset,shrink=4))

        for currency ,x in zip(self.currencyIncluded, range(0,len(self.currencyIncluded))):
            #if max stack is only one
            if currency[1] == 1:
                cur = self.allCurrencies[x]
                self.allCurrenciesLowerHalf.append(cur[0])    
            else:
                cur = self.allCurrencies[x]
                self.allCurrenciesLowerHalf.append(cur[0][:,int(offset/2):int(offset)-1])

    def importStacksFromSinglePicture(self, filename ,maxStackSize, anchor, borderWidth, squareSize, shrink=0):
        self.filename = filename
        self.prefix = "ref"
        if DEBUG:    
            self.iconRootFolder = "Hardcodedpath, hidden here because it uses my network drive"
            self.loc = self.iconRootFolder +  self.filename
            self.img = self.loc
            printSpecPath(self.loc,self.prefix + self.filename)
        else:
            self.img = resource_path(self.prefix + self.filename)

        rootImage = cv.imread(self.img, cv.IMREAD_UNCHANGED)
        pictureStack = []
        
        for possibleStackSize in range(0,maxStackSize):
            shift = self.findCoordinates(possibleStackSize,squareSize,borderWidth)
            start = tuple(map(operator.add, anchor, shift[0]))
            end = tuple(map(operator.add, anchor, shift[1]))
            #arrays are inverted in numpy, change x and y coordinates
            pictureStack.append(rootImage[start[1]+shrink:end[1]-shrink,start[0]+shrink:end[0]-shrink])
        return pictureStack

    def findCoordinates(self, squareNo,squareSize,borderWidth):
        cutout = []
        start = (int(squareNo//inventoryColumns*(squareSize+borderWidth)),int(squareNo%inventoryColumns*(squareSize+borderWidth)))
        end = tuple(map(operator.add, start, (int(squareSize),int(squareSize))))

        cutout.append(start)
        cutout.append(end)
        return cutout

    def getScreen(self):

        img = pyautogui.screenshot()
        pic = np.array(img)
        pic = cv.cvtColor(pic, cv.COLOR_BGR2RGB)  
        return pic

    def findBox(self, squareNo, start, end):
        self.deltaXpBox = (end[0]-start[0])/inventoryRows
        self.deltaYpBox = (end[1]-start[1])/inventoryColumns
        cutout = []
        start = (int(squareNo//inventoryColumns*(self.deltaXpBox)),int(squareNo%inventoryColumns*(self.deltaYpBox)))
        end = tuple(map(operator.add, start, (int(self.deltaXpBox),int(self.deltaYpBox))))
        cutout.append(start)
        cutout.append(end)
        return cutout

class Tray(QSystemTrayIcon):
    closeApplication = pyqtSignal()
    reopenSetupWindow = pyqtSignal() 
    evalRequest = pyqtSignal()
    requestsAllowedSignal = pyqtSignal()

    def __init__(self):
        super().__init__() 

        #if running with debug flag, use hard coded path, else look for path in .spec file. 
        if DEBUG:
            self.icon = QIcon("Hardcodedpath, hidden here because it uses my network drive")
        else:
            self.icon = QIcon(resource_path("CCIcon.png"))
        
        self.setIcon(self.icon)
        self.setVisible(True)
        self.menu = QMenu()     
        self.settings = QAction("Settings")
        self.settings.triggered.connect(self.notifyMainReopen)
        self.menu.addAction(self.settings)

        self.eval = QAction("Evaluate...")
        self.eval.triggered.connect(self.notifyMainEval)
        self.eval.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_E))
        self.menu.addAction(self.eval)

        self.quit = QAction("Quit")
        self.quit.triggered.connect(self.notifyMainClose)
        self.menu.addAction(self.quit)

        self.setContextMenu(self.menu)

        self.requestsAllowed = False

    def toggleAllowance(self, permission):
        self.requestsAllowed = permission

    def notifyMainClose(self):
        self.closeApplication.emit()
    
    def notifyMainReopen(self):
        self.reopenSetupWindow.emit()

    def notifyMainEval(self):
        if self.requestsAllowed:
            self.evalRequest.emit()
        else:
            print("Request blocked as setting window is opened")
    
class Controller(QWidget):
    togglePermissionToEval = pyqtSignal(bool)
    def __init__(self):
        super().__init__() 
        self.setupWindow = SetupWindow()
        self.overlayWindow = OverlayWindow()  
        self.donationWindow = DonateWindow()

        self.setupWindow.startClicked.connect(self.hideSetupWindow)
        self.setupWindow.popupOnStart.connect(self.disableStartPopup)
        self.setupWindow.resolution.connect(self.saveResolution)
        self.overlayWindow.openSettings.connect(self.showSetupWindow)
        self.setupWindow.donationClicked.connect(self.showInfoWindow)

        self.popupflag = settings.value("disableStartPopup",True,bool)
        self.resolution = settings.value("resolution","1920x1080",str)

    def setStartingSignals(self):
        if self.popupflag:
            self.setupWindow.show()
            self.togglePermissionToEval.emit(False)
        else:
            self.togglePermissionToEval.emit(True)

    def showSetupWindow(self):
        self.overlayWindow.hide()
        self.setupWindow.show()
        self.togglePermissionToEval.emit(False)

    def hideSetupWindow(self):
        self.setupWindow.hide()
        self.togglePermissionToEval.emit(True)

    def showInfoWindow(self):
        self.donationWindow.show()
    def showOverlay(self):
        self.overlayWindow.newRequestSignal.emit()
        if (self.overlayWindow.isVisible() == False):
            self.setupWindow.hide()


        
    def disableStartPopup(self, flag):
        settings.setValue("disableStartPopup", flag)

    def saveResolution(self, resName):
        settings.setValue("resolution", resName)

    def quitApplication(self):
        QCoreApplication.quit()

def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    controller = Controller()

    #code for system tray items 
    tray = Tray()
    tray.closeApplication.connect(controller.quitApplication)
    tray.reopenSetupWindow.connect(controller.showSetupWindow)
    tray.evalRequest.connect(controller.showOverlay)

    controller.togglePermissionToEval.connect(tray.toggleAllowance)
    controller.setStartingSignals()

    keybinder.init()
    unregistered = False
    keybinder.register_hotkey(controller.winId(), "Ctrl+E", controller.showOverlay)

    win_event_filter = WinEventFilter(keybinder)
    event_dispatcher = QAbstractEventDispatcher.instance()
    event_dispatcher.installNativeEventFilter(win_event_filter)

    sys.exit(app.exec_())
    keybinder.unregister_hotkey(controller.winId(), "Ctrl+E")

if __name__ == '__main__':
    main()

