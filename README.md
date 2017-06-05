# Introduction
This repo contains a basic setup to enable some web-based conversion analysis, i.e., an evaluation of what 
web-site visits result in sales, based on the location and channel etc. 

## Installation
The basic dataset is a XLSX file, which is read using a Python script into a MySQL database, and 
from there queried to reveal the timeseries conversion data. 

The following setup was performed on an AWS EC2 instance (T2.micro instance) using the Ubuntu 14.04 LTS AMI. 

<pre>
sudo apt-get update
sudo apt-get install python-pip git virtualenv xlrd python-dev libmysqlclient-dev
sudo apt-get install mysql-server MySQL-Python
pip install MySQL-python
git clone <repo-url>
cd ConversionAnalysis
</pre>


### Analysis Packages
A number of analysis packages are used to present the flow of visits and signups.

#### R
The statistical language R is quite useful to perform a basic exploratory data analysis. 
The <b>parsetR</b> library is particularly well suited to the sort of flow-level analysis 
present in the dataset - http://personal.tcu.edu/kylewalker/interactive-flow-visualization-in-r.html
<pre>
devtools::install_github("timelyportfolio/parsetR")
</pre>
