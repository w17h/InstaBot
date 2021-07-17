#filename : InstaBot.py
#author : PRAJWAL T R
#date last modified : Tue Feb  9 11:04:03 2021
#comments :

'''
    Selenium based Instagram BOT
'''

# imports
import socket
from datetime import datetime
from datetime import date
import json
from selenium.webdriver.firefox.options import Options
from selenium.webdriver import Firefox
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from random import randint
from random import shuffle
import time
import pickle as pic
from os import path

# file paths
log_file_path = "log.txt"
config_data_path = "config_data.json"
cache_path = "cache"
statistics_file_path = "statistics.csv"
stat_columns = "date, followers, following, added_following, removed_following\n"
stat_write_format = "%s, %d, %d, %d, %d\n"

# LOG FLAGS
ERROR = 0
INFO = 1

# flag store
flag_store = {
ERROR : "ERROR",
INFO : "INFO",
}

# message store
message_store = {
"NET_NO" : "No Active Internet Connection found\n",
"NET_ACT" : "Active Internet Connection found\n",
"CONFIG_SUCC" : "Configuration File Load succesful\n",
"CONFIG_FAIL" : "Configuration File Load failed\n",
"NAME_UNAME_FAIL" : "NAME : 'username' not Found\n",
"LOGIN_SUCC" : "Login succesful\n",
"LOGIN_FAILED" : "Login Failed Invalid username or password \n",
"XPATH_FOLLOWERS" : "XPATH : username/followers not Found\n",
"XPATH_EXPLORE" : "XPATH : explore not found\n",
"XPATH_SUGGETED_WINDOW" : "XPATH : suggested not found\n",
"FOLLOWING_ADD_SUCC" : "Following added\n",
"FOLLOWING_REM_SUCC" : "Following Removed\n",
"XPATH_FOLLOWING\ERS_WINDOW" : "XPATH : followers/following windows not found\n"
}

# statistics store
statistics_store = {
"followers" : 0,
"following" : 0,
"added_following" : 0,
"removed_following" : 0
}

# browser element and its paths
url_login = "https://www.instagram.com/accounts/login/"
url_profile = "https://www.instagram.com/%s/"
name_username = "username"
name_password = "password"
id_loginerror = "slfErrorAlert"
xpath_followers = "//a[@href='/%s/followers/']/span"
xpath_following = "//a[@href='/%s/following/']/span"
xpath_home = "//div/a[@href='/']"
xpath_explore = "//a[@href='/explore/people/']"
xpath_suggested_window = "//main[@role='main']"
xpath_turn_on_notification = "//div/button[text()='Not Now']"
xpath_suggestion_usernames = "//div/span/a[@href][@title]"
xpath_follow_buttons = "//button[@type='button'][text()='Follow']"
xpath_followers_usernames = "//div/span/a[@href][@title]"
xpath_following_buttons = "//button[text()='Following']"
xpath_followers_window = "//div[@class]/li"
xpath_close_followers_window = "//*[local-name() = 'svg'][@aria-label='Close']"
xpath_unfollow_button = "//button[@tabindex='0'][text()='Unfollow']"

# global vairables
setup_path = path.dirname(path.realpath(__file__)) + "/"
log_file = open(setup_path + log_file_path, "a") # append to existing file or create new file

def getTimeStamp():
    '''
        return current timestamp with date time with seconds
    '''
    dt = datetime.now()
    timestamp = dt.__str__().split('.')[0] # remove micro seconds
    return timestamp

def getDateStamp():
    '''
        return current date only
    '''
    dt = date.today()
    return dt.__str__()

def cleanClose():
    '''
        exit by closing all open files and browser if active
    '''
    # close all open files
    log_file.close()
    try:
        browser.close()
    except:
        # no active browser instance running
        pass
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
    config_file = open(setup_path + config_data_path, 'r')
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
    browser.get(url_login)
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

def addRandomFollowers(browser, config_data):
    # if browser in profile page
    username = config_data["username"]
    if browser.current_url != "https://www.instagram.com":
        # redirect to home page
        browser.find_element_by_xpath(xpath_home).click() # element is already loaded when collecing statistics
    # handle turn on notification popup
    turn_on_button = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, xpath_turn_on_notification)))
    if turn_on_button:
        turn_on_button.click()
    # on home page find explore link to add random people
    try:
        WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, xpath_explore)))
    except NoSuchElementException:
        writeLog(ERROR, message_store['XPATH_EXPLORE'])
    browser.find_element_by_xpath(xpath_explore).click()
    # load all following suggestion
    try:
        browser.find_element_by_xpath(xpath_suggested_window)
    except NoSuchElementException:
        writeLog(ERROR, message_store['XPATH_SUGGETED_WINDOW'])
    suggestion_window = browser.find_element_by_xpath(xpath_suggested_window)
    users_found = len(suggestion_window.find_elements_by_xpath(xpath_suggestion_usernames))
    while True:
        # scroll down
        actions = ActionChains(browser)
        actions.key_down(Keys.CONTROL).key_down(Keys.END).perform()
        time.sleep(3)# TODO : find better method, remove explicit wait
        # break if prev_height == new_height
        new_users_found = len(suggestion_window.find_elements_by_xpath(xpath_suggestion_usernames))
        if users_found == new_users_found:
            break
        users_found = new_users_found
    # get data on how many followers to add
    followers_to_add =  0
    if config_data["random_add"] == "True":
        followers_to_add = randint(config_data["max_follower_add"] // 2, config_data["max_follower_add"])
    else:
        followers_to_add = config_data["max_follower_add"]
    # page fully loaded, srap usernames and follow buttons
    suggestion_window = browser.find_element_by_xpath(xpath_suggested_window)
    usernames_found = suggestion_window.find_elements_by_xpath(xpath_suggestion_usernames)
    usernames_found = [user.text for user in usernames_found] # get text attributes
    follow_buttons_found = suggestion_window.find_elements_by_xpath(xpath_follow_buttons)
    user_map = dict(zip(usernames_found, follow_buttons_found))
    shuffle(usernames_found)
    users_added = []
    for i in range(followers_to_add):
        user_map[usernames_found[i]].click()
        users_added.append(usernames_found[i])
    appendCache(users_added)
    writeLog(INFO, message_store["FOLLOWING_ADD_SUCC"])
    # update statdata for users added
    statistics_store["added_following"] = len(users_added)

def appendCache(users):
    dt = getDateStamp()
    # check if cache file exists
    cache_data = {}
    if path.isfile(setup_path + cache_path):
        cache_file = open(setup_path + cache_path, "rb")
        cache_data = pic.load(cache_file, encoding="bytes") # load previous data if any
        cache_file.close()
    try:
        cache_data[dt] += users # if the script ran more than one time on the same day
    except KeyError:
        cache_data[dt] = users
    cache_file = open(setup_path + cache_path, "wb") # open file for appends
    pic.dump(cache_data, cache_file)
    cache_file.close()

def loadLastRecord():
    '''
        return the date of first record in cache
    '''
    # check if cache file exists
    cache_data = {}
    if path.isfile(setup_path + cache_path):
        cache_file = open(setup_path + cache_path, "rb")
        cache_data = pic.load(cache_file, encoding="bytes") # load previous data if any
        cache_file.close()
        try:
            date = cache_data.keys().__iter__().__next__()
        except StopIteration:
            return None
    else:
        return None

def daysElapsed(config_data):
    '''
        check if today - last record days >=  daysToWait
    '''
    first_record = loadLastRecord()
    if(first_record):
        # record exist
        first_record_day = datetime.strptime(first_record, "%Y-%m-%d")
        today = datetime.strptime(date.today().__str__(), "%Y-%m-%d")
        days_to_wait = config_data["days_to_wait"]
        if((today - first_record_day).days >= days_to_wait): # days have elapsed, contiue to remove cached following
            return True
    return False # if no record found or days have not elapsed

def removeCachedFollowing(browser, config_data):
    '''
        remove following of cached users, if not found in followers list
    '''
    if(not daysElapsed(config_data)):
        return # removing following can wait
    # daysToWait days have elapsed, remove followers from oldest record
    cache_file = open(setup_path + cache_path, "rb")
    cache_data = pic.load(cache_file, encoding="bytes") # load previous data if any
    cache_file.close()
    remove_date = cache_data.keys().__iter__().__next__()
    followers_to_check = cache_data[remove_date]
    # load followers page
    browser.get(url_profile % config_data['username'])
    # click link to followers
    followers_button = browser.find_element_by_xpath(xpath_followers % config_data['username'])
    followers_button.click()
    # find window containing followers list and focus by clicking it
    try:
        WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, xpath_followers_window)))
    except NoSuchElementException:
        writeLog(ERROR, message_store['XPATH_FOLLOWING\ERS_WINDOW'])
    followers_window = browser.find_element_by_xpath(xpath_followers_window)
    followers_window.click()
    # scroll followers windows to load all followers
    current_followers_found = len(followers_window.find_elements_by_xpath(xpath_suggestion_usernames))
    while True:
        # scroll down
        actions = ActionChains(browser)
        actions.key_down(Keys.CONTROL).key_down(Keys.END).perform()
        time.sleep(3)# TODO : find better method, remove explicit wait
        # break if prev_height == new_height
        new_followers_found = len(followers_window.find_elements_by_xpath(xpath_suggestion_usernames))
        if current_followers_found == new_followers_found:
            break
        current_followers_found = new_followers_found

    # cross check followers to check list
    following_to_remove = []
    followers = [user.text for user in followers_window.find_elements_by_xpath(xpath_suggestion_usernames)]
    for f_c in  followers_to_check:
        if f_c not in followers:
            following_to_remove.append(f_c)
    followers_window.find_element_by_xpath(xpath_close_followers_window).click()

    # find all following
    following_button = browser.find_element_by_xpath(xpath_following % config_data['username'])
    following_button.click()
    try:
        WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, xpath_followers_window)))
    except NoSuchElementException:
        writeLog(ERROR, message_store['XPATH_FOLLOWING\ERS_WINDOW'])
    following_window = browser.find_element_by_xpath(xpath_followers_window)
    following_window.click()

    # scroll followers windows to load all followers
    current_following_found = len(following_window.find_elements_by_xpath(xpath_suggestion_usernames))
    while True:
        # scroll down
        actions = ActionChains(browser)
        actions.key_down(Keys.CONTROL).key_down(Keys.END).perform()
        time.sleep(3)# TODO : find better method, remove explicit wait
        # break if prev_height == new_height
        new_following_found = len(following_window.find_elements_by_xpath(xpath_suggestion_usernames))
        if current_following_found == new_following_found:
            break
        current_following_found = new_following_found
    # remove users followers_to_remove
    following = [user.text for user in following_window.find_elements_by_xpath(xpath_suggestion_usernames)]
    following_buttons = following_window.find_elements_by_xpath(xpath_following_buttons)
    following_map = dict(zip(following, following_buttons))
    unfollowed_count = 0
    for user in following_to_remove:
        try:
            following_map[user].click()
            following_window.find_element_by_xpath(xpath_unfollow_button).click()
            unfollowed_count += 1
            time.sleep(2)
        except KeyError:
            # user not in Following list (not accepted request or deleted account)
            pass
    statistics_store['removed_following'] = unfollowed_count
    writeLog(INFO, message_store['FOLLOWING_REM_SUCC'])
    # modify cache
    cache_data.pop(remove_date)
    cache_file = open(setup_path + cache_path, "wb")
    pic.dump(cache_data, cache_file) # load previous data if any
    cache_file.close()

def writeStatistics():
    '''
        write statistics_store data to file ex : .csv
    '''
    # check if statistics.csv exists, if not create one with column names
    # columns : date, followers, following, added_following, removed_following
    if(not path.isfile(setup_path + statistics_file_path)):
        stat_file = open(setup_path + statistics_file_path, "w")
        stat_file.write(stat_columns)
        stat_file.close()
    # get today date
    today_date = getDateStamp()
    # append to existing records
    stat_file = open(setup_path + statistics_file_path, "a")
    stat_file.write(stat_write_format % (today_date, statistics_store['followers'], statistics_store['following'], statistics_store['added_following'], statistics_store['removed_following']))
    stat_file.close()

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
    if config_data["add_following"] == "True":
        addRandomFollowers(browser, config_data)
    if config_data["remove_following"] == "True":
        removeCachedFollowing(browser, config_data)
    writeStatistics()
    cleanClose()
