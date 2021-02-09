#filename : InstaBot.py
#author : PRAJWAL T R
#date last modified : Tue Feb  9 11:04:03 2021
#comments :

'''
    Selenium based Instagram BOT, designed to run as cron job in linux environment
'''

# imports
import socket
from datetime import datetime
import json
from selenium.webdriver.firefox.options import Options
from selenium.webdriver import Firefox
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time

# global contants
log_file_path = "./log.txt"
config_data_path = "./config_data.json"

# LOG FLAGS
ERROR = 0
INFO = 1

# flag store
flag_store = {
ERROR : "ERROR",
INFO : "INFO",
}
# message storecat
message_store = {
"NET_NO" : "No Active Internet Connection found\n",
"NET_ACT" : "Active Internet Connection found\n",
"CONFIG_SUCC" : "Configuration File Load succesful\n",
"CONFIG_FAIL" : "Configuration File Load failed\n",
"NAME_UNAME_FAIL" : "NAME : 'username' not Found\n",
"LOGIN_SUCC" : "Login succesful\n",
"LOGIN_FAILED" : "Login Failed Invalid username or password \n",
"XPATH_FOLLOWERS" : "XPATH : username/followers not Found\n"
}

# statistics store
statistics_store = {
"followers" : 0,
"following" : 0,
"added_following" : 0,
"removed_following" : 0
}

# browser element and its paths
login_url = "https://www.instagram.com/accounts/login/"
name_username = "username"
name_password = "password"
id_loginerror = "slfErrorAlert"
xpath_followers = "//a[@href='/%s/followers/']/span"
xpath_following = "//a[@href='/%s/following/']/span"

# global vairables
log_file = open(log_file_path, "a") # append to existing file or create new file

def getTimeStamp():
    '''
        return current timestamp with date time with seconds
    '''
    dt = datetime.now()
    timestamp = dt.__str__().split('.')[0] # remove micro seconds
    return timestamp

def cleanClose():
    '''
        exit by closing all open files and browser if active
    '''
    # close all open files
    log_file.close()
    browser.close()
    exit(0)

def writeLog(flag, message):
    '''
        log information with timestamp
    '''
    # write to log file
    timestamp = getTimeStamp()
    log_file.write(timestamp + " : " + flag_store[flag] + " : " + message)
    if flag == ERROR:
        cleanClose()

def CheckNetwork():
    '''
        check if working Internet Connection is available
    '''
    testurl = 'www.instagram.com'
    try:
        # see if we can resolve the host name -- tells us if there is a DNS listening
        host = socket.gethostbyname(testurl)
        # connect to the host -- tells us if the host is actually reachable
        s = socket.create_connection((host, 80), 2)
        s.close()
        writeLog(INFO, message_store['NET_ACT'])
    except:
        # no active internet connnection found
        writeLog(ERROR, message_store['NET_NO'])
        cleanClose()

def getConfigData():
    '''
        check if config.json is a valid json file and return json data
    '''
    config_file = open(config_data_path, 'r')
    config_data = ""
    try:
        config_data = json.load(config_file)
        writeLog(INFO, message_store["CONFIG_SUCC"])
    except:
        writeLog(ERROR, message_store["CONFIG_FAIL"])
        cleanClose()
    return config_data

def getBrowser(headless):
    '''
        launch active browser instance ex : Firefox
    '''
    if headless == "True":
        opts = Options()
        opts.set_headless()
        browser = Firefox(options=opts)
        return browser # without GUI
    browser = Firefox() # with GUI
    return browser

def login(browser):
    '''
        login using credentials specified in configuration file
    '''
    browser.get(login_url)
    try:
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.NAME, name_username))) # wait until name:username is found
    except TimeoutException:
        writeLog(ERROR, message_store["NAME_UNAME_FAIL"])
    # login page loaded, enter credentials
    user_name = browser.find_element_by_name(name_username)
    password_field = browser.find_element_by_name(name_password)
    username = config_data["username"]
    password = config_data["password"]
    #fill user login credentials
    user_name.send_keys(username)
    password_field.send_keys(password)
    password_field.submit()
    try:
        WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.ID, id_loginerror))) # check for presence of this element if username and password combination is wrong
        writeLog(ERROR, message_store['LOGIN_FAILED'])
    except TimeoutException:
        writeLog(INFO, message_store['LOGIN_SUCC'])

def collectStatisticsData(browser, username):
    '''
        collect statistics of current logged in user, ex : follower and following count
    '''
    # go to profile page of logged in user
    browser.get("https://www.instagram.com/"+username+"/")
    # check if page elements are loaded
    try:
        WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, xpath_followers % username))) # check for presence of this element, present -> then page is loaded
    except TimeoutException:
        writeLog(ERROR, message_store['XPATH_FOLLOWERS'])
    # read followers and following count
    followers = browser.find_elements_by_xpath(xpath_followers % username)[0].text
    following = browser.find_elements_by_xpath(xpath_following % username)[0].text
    statistics_store['followers'] = int(followers)
    statistics_store['following'] = int(following)

###############End of Utility functions declarations###########################

if __name__ == "__main__":
    # check if working internet connection is available
    CheckNetwork()
    # load json file with configuration data
    config_data = getConfigData()
    # launch browser
    browser = getBrowser(config_data['headless'])
    # login and collect statistics
    login(browser)
    # collect statistics of current logged in user
    collectStatisticsData(browser, config_data['username'])
    # perform actions specified in configuration file
