#!/bin/bash
# Request user to run script without sudo in order to figure out who the actualy user is, then run the script in sudo

printf "\e[93mPlease note, some parts of the installation might take long without feedback. There will also be use input required early on for Brew, Xcode and Mono (if not installed).\n\e[0m"

echo 'Checking if Brew is installed'
which -s brew > /dev/null 2>&1
if [ $? != 0 ]
then
    # Install Homebrew
    printf "\e[93mBrew is not installed, installing it. This will take a while\n\e[0m"
    sleep 2 # let user see warning...
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
    if [ $? != 0 ] ; then printf "\e[91m╳ Brew failed to install.\n\e[0m" ; exit 1 ; fi ;
    printf "\e[32m✓ Brew is now installed\n\e[0m"
else
    echo 'Brew is already installed, updating'
    brew update
    if [ $? != 0 ] ; then printf "\e[91m╳ Brew failed to update.\n\e[0m" ; exit 1 ; fi ;
    printf "\e[32m✓ Brew updated\n\e[0m"
fi

# check if installed, somewhat faster than always trying to reinstall
echo 'Checking if pkg-config is installed'
which -s pkg-config > /dev/null 2>&1
if [ $? != 0 ]
then
    echo 'pkg-config is not installed, installing it. This may take a while'
    brew install pkg-config
    if [ $? != 0 ] ; then printf "\e[91m╳ pkg-config failed to install.\n\e[0m" ; exit 1 ; fi ;
    printf "\e[32m✓ pkg-config is now installed\n\e[0m"
else
    printf "\e[32m✓ pkg-config is already installed\n\e[0m"
fi

echo 'Checking if mono is installed'
which -s mono
if [ $? != 0 ]
then
    # Maybe it is installed, just not linked to path
    if [ -d '/Library/Frameworks/Mono.framework/Versions/Current/Commands' ] 
    then
        printf "\e[32m✓ Mono is already installed\n\e[0m"
    else
        echo 'Mono is not installed, downloading and installing it. This may take a while'
        brew install mono
        if [ $? != 0 ] ; then printf "\e[91m╳ Mono failed to install.\n\e[0m" ; exit 1 ; fi ;
        printf "\e[32m✓ Mono is now installed\n\e[0m"
    fi
else
    printf "\e[32m✓ Mono is already installed\n\e[0m"
fi

echo 'Checking if mono is in path'
case ":$PATH:" in
  *:/Library/Frameworks/Mono.framework/Versions/Current/Commands:*) printf "\e[32m✓ Mono is in path\n\e[0m" ;;
  *) export PATH=/Library/Frameworks/Mono.framework/Versions/Current/Commands:${PATH} ; printf "\e[32m✓ Mono is now in path\n\e[0m" ;;
esac


echo 'Checking if mono is correctly linked for pkg-config'
pkg-config --libs mono-2 > /dev/null 2>&1
if [ $? != 0 ]
then
    export PKG_CONFIG_PATH=/Library/Frameworks/Mono.framework/Versions/5.20.1/lib/pkgconfig:$PKG_CONFIG_PATH
    printf "\e[32m✓ Mono is now configured for pkg-config\n\e[0m"   
else
    printf "\e[32m✓✓ Mono is already configured for pkg-config\n\e[0m"
fi

echo 'Checking if python 3.8.7 is installed'
installPython=true
which -s python3 > /dev/null 2>&1
if [ $? = 0 ]
then
    pythonVerison="$(python3 -V)"
    if [ "$pythonVerison" != "Python 3.8.7" ]
    then
      # TODO maybe look up what version it is linked to and try to update to 3.8 and hope for the best?
      echo "Found python, but not 3.8.7, it is $pythonVerison"
    else
        installPython=false
    fi
fi
if [ $installPython = true ]
then
    echo 'Python 3.8.7 is not installed, downloading and installing it. This may take a while'
    mkdir -p downloads
    curl https://www.python.org/ftp/python/3.8.7/python-3.8.7-macosx10.9.pkg --output ./downloads/python3.8.7.pkg
    echo 'Python 3.8.7 downloaded. Installing now.'
    sudo installer -verbose -pkg downloads/python3.8.7.pkg -target /
    if [ $? != 0 ] ; then printf "\e[91m╳ Python failed to install.\n\e[0m" ; exit 1 ; fi ;
    printf "\e[32m✓ Python 3.8.7 is now installed\n\e[0m"
else
    printf "\e[32m✓ Python 3.8.7 is already installed\n\e[0m"
fi

echo 'Checking if pip is installed'
python3 -m pip > /dev/null 2>&1
if [ $? != 0 ]
then
  echo "Pip not installed, downloading and installing it."
  mkdir -p downloads
  curl https://bootstrap.pypa.io/get-pip.py --output ./downloads/get-pip.py
  echo 'Pip downloaded. Installing now.'
  python downloads/get-pip.py
  if [ $? != 0 ] ; then printf "\e[91m╳ Pip failed to install.\n\e[0m" ; exit 1 ; fi ;
  printf "\e[32m✓ Pip installed.\n\e[0m"
else
  printf "\e[32m✓ Pip is already installed.\n\e[0m"
fi

if [ ! -d './env' ] 
then
    echo 'Ensuring virtualenv is installed'
    python3 -m pip install virtualenv --user
    if [ $? != 0 ] ; then printf "\e[91m╳ virtualenv failed to install.\n\e[0m" ; exit 1 ; fi ;
    echo 'Creating virtualenv'
    python3 -m virtualenv env
    chmod +x ./env/bin/activate
    printf "\e[32m✓ Created virtualenv\n\e[0m"
else    
    printf "\e[32m✓ Virtual env is already created\n\e[0m"
fi

source ./env/bin/activate

echo 'Ensuring wheel is installed'
python3 -m pip install wheel
if [ $? != 0 ] ; then printf "\e[91m╳ wheel failed to install.\n\e[0m" ; exit 1 ; fi ;

echo 'Ensuring pycparser is installed'
python3 -m pip install pycparser
if [ $? != 0 ] ; then printf "\e[91m╳ pycparser failed to install.\n\e[0m" ; exit 1 ; fi ;

echo 'Installing requirements'
python3 -m pip install -r requirements.txt --extra-index-url https://pkgs.dev.azure.com/quix-analytics/53f7fe95-59fe-4307-b479-2473b96de6d1/_packaging/public/pypi/simple/
if [ $? != 0 ]
then
 printf '\e[91m╳ Failed to install requirements, try running the following manually:\n \e[93mpython3 -m pip install -r requirements.txt --extra-index-url https://pkgs.dev.azure.com/quix-analytics/53f7fe95-59fe-4307-b479-2473b96de6d1/_packaging/public/pypi/simple/\n\e[0m'
 exit $?
fi
printf "\e[32m✓ Installed requirements\n\e[0m"

printf "\e[94mYour environment is ready. To activate it in your terminal, enter\n\e[93m source ./env/bin/activate\n\e[0m"
printf "\e[94mAfter that, to run the sample code, enter\n\e[93m python3 main.py\n\e[0m"