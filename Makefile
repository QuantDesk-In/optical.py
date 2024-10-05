.PHONY: clean build

# Define variables
APP_NAME := "Optical"
ICON_FILE := "options.ico"
PY_FILES := main.py ui.py calculations.py data_fetch.py utils.py

# Define targets
clean:
	@echo "Cleaning up..."
	rm -fr build 
	rm -fr dist 
	rm -fr *.spec
	rm -fr __pycache__

build: clean
	@echo installing dependencies
	pip3 install -r requirements.txt
	@echo "Building $(APP_NAME)..."
	pyinstaller -w --name $(APP_NAME) --icon=$(ICON_FILE) $(PY_FILES)