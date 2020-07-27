# How to install
If you do not wish to use the .exe file I provided, you can build this program yourself! 
In order to do so, make sure you have the newest version of python 3 installed, then you will need the following libraries:

Library name | more info | pip install
------------ | ------------ | ------------
pyautogui|link: https://pyautogui.readthedocs.io/en/latest/|pip install pyautogui
2. OpeCV|link: https://opencv.org/|pip install opencv-python
3. PyQt5      |   link: https://pyautogui.readthedocs.io/en/latest/#|pip install PyQt5
4. Pyinstaller|  link: https://www.pyinstaller.org/|pip install pyinstaller
5. pyqtkeybind|  link: https://github.com/codito/pyqtkeybind|pip install pyqtkeybind

Also important: pyinstaller seems to have some weird issue with "setuptools" as seen here: https://github.com/pypa/setuptools/issues/1963
if you get an error likely the following will fix it: pip install --upgrade 'setuptools<45.0.0'

Once you have downloaded the .zip of this repository, unpack it. Now run pyinstaller with the "ChaosCounter.spec" file by entering 

"pyinstaller ChaosCounter.spec"

Make sure you either navigated to the folder where the spec file is located first or instead use the full path to the file.
