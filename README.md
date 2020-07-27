# ChaosCounter

Tala moana, warrior!

thanks for having a look at my little program. Chaos Counter is a program that helps you sum up currency of both trading inventories, so that even the laziest exiles can engage in currency flipping. When pressing **CTRL+E**, the content of the inventories will be analysed visually, and an overlay will show you just how much each inventory contains. Full stacks will be marked green, while all other stacks are marked yellow, in case somebody wants to do a little switcheroo and scam you with a non-full stack somewhere in the middle. The main advantages are that it is

* fast
* does not require permissions
* offline
* visual only (no memory access)

This means that if I understood the terms and conditions correctly, this tool does not violate any rules. This and the speed is achieved by 

* Using OpenCV and other great libraries written in c++
* Utilizing all your cores
* A little bit of a “close enough” approach

# Where I need help
Unfortunately, I myself am not a great Path of Exile players, and even though I have been playing for more leagues than I want to admit, I amassed a total of **seven** Exalted orbs. This in combination with the fact that I have seen a Hunter’s Exalted Orb once, results in my program not being able to comprehend these high value currencies stacks. If you however surpassed my immense wealth and wish to trade in multiple stacks of Exalted orbs, consider making my program smarter by showing me how such stacks look like. Don’t worry, I won’t try to scam you out of your valuables, I suggest you take little flex picture with the currency stacks ordered in the following way.

![following way](https://github.com/FTrygg/ChaosCounter/blob/master/concept.png?raw=true)
(Starting with the highest possible stack in the upper left corner and decreasing the stack by one each time)

Please make sure, that you do not have **any** colour correction turned on or that the stacks are covered by your mouse. With these pictures, I can teach my little program how to deal with aristocracy trades in this game. 
Right now, **only** 1080p is supported,which is what I assume the most used resolution. A 1440p version is likely added soon, since this is the biggest resolution size I own. Anything above requires me to either buy a 4k screen (which I cannot afford) or a lot of help from an owner of such a screen. This means this will probably be delayed by quite a bit.

# My motivation
This project was started as an excuse for me to investigate the OpenCV library. After playing around, I saw that it worked surprisingly well and because I was already burned out from the league, I spend some more time trying to fine tune it. The main reason for me to quit the league was that I could not raise my needed 2 exalted orbs for a craft, as my chaos income was outpaced by the steeply increasing exalted price. I will not start the whole discussion regarding bots in PoE as this has been discussed many times before. But I thought that maybe a tool like this makes currency trading a little more accessible and tolerable for actual human players. Hoping that the more convenient it gets, the less inclined a few players are to leave this part of the game to bots. This on the other hand made me realize, how my program can be abused to automate trades if paired with other programs. 
~~As a result, my program will only visually show you how much currency of each stack is found, and my source code will not be published. If you think there is a better way of dealing with this, let me know, as I usually am a big fan of sharing code. I just think I could make matters a lot worse, which is not what I strive for.~~  

# How to install
You will find a conveniently packed .exe file under the release section. I am working on veryfing its content, yet I cannot do that yet since I lack any relevant experience in that field.
If you do not wish to use the .exe file I provided, you can build this program yourself! 
In order to do so, make sure you have the newest version of python 3 installed, then you will need the following libraries:

Library name | more info | pip install
------------ | ------------ | ------------
Pyautogui|link: https://pyautogui.readthedocs.io/en/latest/|pip install pyautogui
OpeCV|link: https://opencv.org/|pip install opencv-python
PyQt5|link: https://pyautogui.readthedocs.io/en/latest/#|pip install PyQt5
Pyinstaller|link: https://www.pyinstaller.org/|pip install pyinstaller
Pyqtkeybind|link: https://github.com/codito/pyqtkeybind|pip install pyqtkeybind
(Setuptools)|https://setuptools.readthedocs.io/en/latest/|pip install setuptools

Also important: pyinstaller seems to have some weird issue with "setuptools" as seen here: https://github.com/pypa/setuptools/issues/1963
if you get an error likely the following will fix it: pip install --upgrade 'setuptools<45.0.0'

Once you have downloaded the .zip of this repository, unpack it. Now run pyinstaller with the "ChaosCounter.spec" file by entering 

"pyinstaller ChaosCounter.spec"

Make sure you either navigated to the folder where the spec file is located first or instead use the full path to the file.


Again, my tool is not perfect, make sure to double check the trade. I am open to suggestions, but understand that I am just a student doing this in my free time. 
Should you lack a meaningful way to invest your real world currency, after buying all supporter packs and MTXs, feel free to [donate](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=YUXL8CBVZJ94C&source=url) me some leftovers, so that maybe one day I can buy one myself. If not, no worries, I am a student and understand 😊

Thanks for reading and have a good one!

*NotAChineseTradingBot*





