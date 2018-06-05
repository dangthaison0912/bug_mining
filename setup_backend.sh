# RUNNING THIS FILE SHOULD INSTALL ALL DEV TOOLS
# INSTALLATION OF BACKEND

# INSTALLING PIP
echo [INSTALLING PIP]
python get-pip.py && echo [INSTALLED PIP SUCCESSFULLY]

# INSTALLS VIRTUALENV
echo [INSTALLING VIRTUALENV]
pip install virtualenv && echo [INSTALLED VIRTUALENV SUCCESSFULLY]

# CREATES AND ACTIVATES PYTHON VIRTUAL ENVIRONMENT
echo [CREATING VIRTUALENV FOLDER]
# mkdir virtualenvfolder
# sudo virtualenv ./virtualenvfolder/doctimetable  # creates virtualenv folder
cd virtualenvfolder/bin/            # goes to bin dir of the virtualenv
source activate && echo [ACTIVATE Virtualenv]    # activates virtualenv
cd ../../                                   # returns to root

# INSTALLS DJANGO/PYTHON AND RELATING DEPENDENCIES
echo [INSTALLING DEPENDENCIES]
cd virtualenvfolder
./install_dependencies.sh
pip3 install -U Django && echo [FINISHED INSTALLING DEPENDENCIES]

# SETUP DJANGO DB USER AND DATABASE
# logs as user "postgres" and create the user and database and grants permission of the new user to it
echo [SETTING UP DB USER AND DATABASE]
echo [PLEASE FOLLOW INSTRUCTIONS IN THE README FILE TO SKIP OR END TYPE "exit"]
# sudo su - postgres && echo [CONTINUING SETUP]

# INSTALLS FRONTEND REACT AND OTHER DEPENDENCIES
# echo [INSTALLING FRONTEND]
# cd ../Frontend
# npm i webpack -S
# npm i npm i babel-core babel-loader babel-preset-es2015 babel-preset-react -S
# npm i react react-dom -S
# # TODO:
