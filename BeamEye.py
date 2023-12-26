import threading


def startUI():
	import uiElements.uiHandler


threading.Thread(target=startUI).start()
import detectionCode
