# InstaFollowers

## Python Automation Script to Add and Remove Follwers in Instagram

### Requirements:
```
Python3.x
Selenium
Firefox Browser
Working Internet connection
matplotlib(optional)
```
### note:
If you have multiple versions of python and want to install selenium to python3 instead of python2 (by default)
try:
```
  pip3 install selenium
```

instead of
```
  pip install selenium
```

Works only with good internet connection because a lot in this code depends on string manupulation
and regex so if pages are not loaded properly then chances of parsing garbage strings are high.

AND

New feature added : check for verified profiles ! control this behaviour in config.json

### How to use the script :

### After succesfully installing Requirements

1.edit config.json , this is a simple json file to set username and password or to change other defualt settings , it is self explanatory .

example :

username : instagram username

password : password in plain text

headless : "False"  #browser runs in full GUI mode (You can view the browser in Action !)  

followersToAdd : 20  #number of defualt followers to Add  

2.Run the Script by -  
```
  python3 InstaFollowers.py  
```  
3.Ploting Data by -
```
  python3 plotstatistics.py
```
THAT'S IT !  

Warning :  
  This is very Badly Written Code so just take this as an example for your instagram bot :)  
  and also this is barely a working example ( I mean it works on my computer XD)  
  This will be further Improved , and You can contribute too...

THINGS TO ADD:  
- [x] statitstics.py to plot and view instagram data and plot it
- [x] increase relability to make it work in background (schedule)  
- [x] add method to check Internet Connection

### PRO-TIP :

You Can run this as cron job , make sure you use the headless : True in config file .we dont want   browser window popup in middle while you are working XD . this was the original idea ,to have cron  job to automatically do the boring work for me as per my need in config.json.
