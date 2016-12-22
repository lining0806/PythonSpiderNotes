"""Test for exceptions raised in the tesseract.exe logfile"""

class Tesser_General_Exception(Exception):
	pass

class Tesser_Invalid_Filetype(Tesser_General_Exception):
	pass

def check_for_errors(logfile = "tesseract.log"):
	inf = file(logfile)
	text = inf.read()
	inf.close()
	# All error conditions result in "Error" somewhere in logfile
	if text.find("Error") != -1:
		raise Tesser_General_Exception, text