# **************************************************************************** #
# General Make configuration

# This suppresses make's command echoing. This suppression produces a cleaner output. 
# If you need to see the full commands being issued by make, comment this out.
MAKEFLAGS += -s

# **************************************************************************** #
# Targets

# run the application using the main venv
run: venv
	$(VENV_PYTHON) src/main.py

# run the application in pdb
debug: venv
	$(VENV_PYTHON) -m pdb src/main.py

# build an executable using cx_Freeze
build: venv
	$(VENV_PYTHON) setup.py build_exe

# build a windows installer using cx_Freeze
installer: venv
	$(VENV_PYTHON) setup.py bdist_msi
# remove pyinstaller's output
clean:
	echo cleaning build 

# **************************************************************************** #
# python venv settings
VENV_NAME := .venv

ifeq ($(OS),Windows_NT)
	VENV_DIR := $(VENV_NAME)
	VENV := $(VENV_DIR)\Scripts
	PYTHON := python
	VENV_PYTHON := $(VENV)\$(PYTHON)
else
	VENV_DIR := $(VENV_NAME)
	VENV := $(VENV_DIR)/bin
	PYTHON := python3
	VENV_PYTHON := $(VENV)/$(PYTHON)
endif

# Add this as a requirement to any make target that relies on the venv
.PHONY: venv
venv: $(VENV_DIR)

# Create the venv if it doesn't exist
$(VENV_DIR):
	$(PYTHON) -m venv $(VENV_DIR)
	$(VENV_PYTHON) -m pip install --upgrade pip
	$(VENV_PYTHON) -m pip install -r requirements.txt

# deletes the venv
clean_venv:
ifeq ($(OS),Windows_NT)
	rd /s /q $(VENV_DIR)
else
	rm -rf $(VENV_DIR)
endif

# deletes the venv and rebuilds it
reset_venv: clean_venv venv