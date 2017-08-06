
# References
* ASN.1 conversion tools for CDR/NRT data:
 * Open source for C++: http://www.tap3edit.com/de_4_1_tools.php
 * Open source module for Python:
  * PyASN1 home page: http://pyasn1.sourceforge.net
  * PyASN1 programmer's manual: http://www.red-bean.com/doc/python-pyasn1/pyasn1-tutorial.html
 * Proprietary: http://www.marben-products.com/asn.1/cdr-converter.html
 * Fraud detection: https://docs.oracle.com/cd/E16754_01/doc.75/e16717/rmg_nrtrde_about.htm#BRMRO338
* ASN.1 specifications:
 * NRT: http://cpansearch.perl.org/src/MRJONES/TAP3-Tap3edit-0.33/lib/TAP3/Spec/NRT0201.asn
 * Call Event Details: http://www.tapeditor.com/OnlineDemo/301/type_CallEventDetail.html
 * General: http://luca.ntop.org/Teaching/Appunti/asn1.html
* ASN.1 BCD (Binary Coded Decimal) strings:
 * http://stackoverflow.com/questions/11668969/python-how-to-decode-binary-coded-decimal-bcd
 * http://stackoverflow.com/questions/462970/most-efficient-way-to-convert-bcd-to-binary
* Python date-time format directives: https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior

## Glossary
* [MOC - Mobile Originated Call](http://www.tapeditor.com/OnlineDemo/301/type_MobileOriginatedCall.html)
* [MTC - Mobile Terminated Call](http://www.tapeditor.com/OnlineDemo/301/type_MobileTerminatedCall.html)
* [GRPS - General Packet Radio Service](http://www.tapeditor.com/OnlineDemo/301/type_GprsCall.html) 

# Installation

## Python ```virtualenv```

### Installation
#### On CentOS
As the administrator (```root```), to be done just once:
```bash
$ su - # As root, to be done just once
$ yum -y install epel-release
$ yum -y install python34 python-pip
$ yum remove python-virtualenv
$ pip install --upgrade pip
$ pip install virtualenv
$ exit
```

#### On MacOS
* Install Python (version 2 by default) and Python3 with Homebrew
```bash
$ brew install python python3 pyenv-virtualenv
```
* Install ``libmagic`` (see http://github.com/ahupp/python-magic)
```bash
$ brew install libmagic
```
* In order for Matplotlib to work, a ''framework'' version of Python
must be used. A way to achieve that is define a Shell function,
which will call the framework Python version from within the virtual
environment, while hinting to that Python version where to find the Python
home directory
```bash
cat >> ~/.bashrc << _EOF

# Python
# http://matplotlib.org/faq/osx_framework.html#osxframework-faq
function frameworkpython {
        if [[ ! -z "$VIRTUAL_ENV" ]]
        then
                PYTHONHOME=$VIRTUAL_ENV /usr/local/bin/python "$@"
        else
                /usr/local/bin/python "$@"
        fi
}

_EOF

```
Example of usage:
```bash
$ frameworkpython myPythonScript.py
```

### Activation
As a normal user:
```bash
$ exit # The following is to be done as a normal user
$ mkdir -p ~/dev
$ cd ~/dev
$ virtualenv -p python3 venv34
$ cd ~/dev
$ ln -sf venv3? venv3
$ source ~/dev/venv3/bin/activate
```
As a reminder, in order to deactivate the virtual environment:
```bash
$ deactivate
```

### Cloning the project
```bash
$ mkdir -p ~/dev/ti
$ cd ~/dev/ti
$ git clone https://github.com/bom4v/ti-data-samples.git
$ cd ti-data-samples/python
```

### Dependencies
#### asn1ate
If, for some reason, the Python NRT encoder/decoder should be regenerated,
the [asn1ate utility](http://github.com/kimgr/asn1ate) is required. As a normal user:
```bash
$ pip install -U asn1ate
$ python ~/dev/venv3/lib/python3.?/site-packages/asn1ate/pyasn1gen.py ../src/main/resources/NRT0201.asn > nrtrde/Nrtrde.py
```
#### Python Magic
* See http://github.com/ahupp/python-magic
```bash
$ pip install -U python-magic
```

# Exploring NRT data files
```bash
$ ./nrt.py -i ../data/cdr/CDR-sample.csv
$ ls ../data/nrt/NRT_all.csv
$ ./nrt.py -i ../data/cdr/CDR-samples.tar.bz2
$ ls ../data/nrt/NRT_all.csv
```


