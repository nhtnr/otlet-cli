<div align="center">
    <img src="https://commedesgarcons.s-ul.eu/zSyAjvoO" alt="otlet_cli readme image"><br>
    CLI tool for querying the Python Packaging Index using <a href="https://github.com/nhtnr/otlet">Otlet</a>. 

[![license-mit](https://img.shields.io/pypi/l/otlet-cli)](https://github.com/nhtnr/otlet/blob/main/LICENSE)
[![github-issues](https://img.shields.io/github/issues/nhtnr/otlet-cli)](https://github.com/nhtnr/otlet-cli/issues)
[![github-pull-requests](https://img.shields.io/github/issues-pr/nhtnr/otlet-cli)](https://github.com/nhtnr/otlet-cli/pulls)
![pypi-python-versions](https://img.shields.io/pypi/pyversions/otlet-cli)
[![pypi-package-version](https://img.shields.io/pypi/v/otlet-cli)](https://pypi.org/project/otlet-cli/)

</div>

# Installing
Otlet-cli can be installed from pip using the following command:  
  
```
pip install -U otlet-cli
```  
  
To install from source, please see the [INSTALLING](https://github.com/nhtnr/otlet-cli/INSTALLING.md) file.
  
# Usage
Get info about a particular package:  
  
  ```
  otlet samplepackage
  ```  
  
Or a specific version:  
  
  ```
  otlet django 4.0.6
  ```  
  
Check out all available releases for a package:  
  
  ```
  otlet releases tensorflow
  ```  

List all available wheels:  
  
  ```
  otlet download torch -l
  ``` 
  
Then download a wheel for Python 3.9 on x86_64 macOS:  
  
  ```
  otlet download torch -w "python_tag:3.9,platform_tag:macosx*x86_64"
  ```
  
And more... just run:  
  
  ```
  otlet --help
  ```  
   
# Contributing
If you notice any issues, or think a new feature would be nice, feel free to open an [issue](https://github.com/nhtnr/otlet-cli/issues).
