1. Go to project folder and Exec following command 'python manage.py migrate nlp'
1. install python 3.6+ and install all packages from requirements.txt
   - Don't forget to Add "C:\Users\username\AppData\Local\Programs\Python\Python36-32", "C:\Users\username\AppData\Local\Programs\Python\Python36-32\Scripts" to your systempath.
   - Open command prompt and go to "needed_tools" folder.
     Type "pip install opencv_python-3.4.3-cp36-cp36m-win32.whl" in order to install opencv-python.
   - Type "pip install -r requirements.txt" in order to install all packages from requirements.txt

2. Softwares for converting .pdf to .jpg	
   - Install ImageMagick-6.9.9-37-Q8-x64-dll.exe.
     Add "C:\Program Files\ImageMagick-6.9.9-Q8" to your systempath.
   - Install gs922w64.exe.
     Add "C:\Program Files\gs\gs9.22\bin" to your systempath  


3. Run the Python interpreter and type the commands.
	>>>import nltk
	>>>nltk.download()
	A new window should open, showing the NLTK Downloader.
	Click on the File menu and select Change Donwload Directory. For central installation, set this to c:\nltk_data (Windows). If you don't install the data to central location, you will need to set the NLTK_DATA environment variable to specify the location of the data. And Click "Donwload" button.
	Test that the data has been installed as follows.
	>>>from nltk.corpus import brown
	>>> brown.words()
	>>> ['The', 'Fulton', 'County', 'Grand', 'Jury', 'said', ...]

4. Install tesseract-ocr-w64-setup-v4.0.0.20181030.exe
   - Don't forget to add the path to your systempath
5. If JDK isn't installed on your system, then pls install JDK 8+ (jdk-8u151-windows-x64) and Add path to your systempath.
   - And replace of java path of java_path = "C:/Program Files/Java/jdk1.8.0_151/bin" in "extract.py"