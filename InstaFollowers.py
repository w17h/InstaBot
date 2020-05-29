#!/usr/bin/python3

#final version for instafollwers
import json
from datetime import date
import sys
import socket
from selenium.webdriver import Firefox
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import remove
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
from selenium.webdriver.common.by import By
#add a feature to skip unfollow procedure for black listed users
#open all files for debug and logging
def Init():
    #global variables
    global config_data
    global config_file
    global log_file
    global statdata
    global stat_file
    global today_date

    #get date
    today_date = str(date.today())
    #append data to log file
    log_file = open("log.txt","a")

    #open the statistics.json file and load the last stats data
    try:
        stat_file = open("statistics.json","r") #appending new keys to already written json file test required
    except:
        log_file.write("Error opening statistics.json file")
        Close()
    #create stat_table to store instagram statistics data
    statdata = {}#by default statdata = dictionary
    try:
        statdata = json.load(stat_file)
        stat_file.close()
    except:
        statdata = {}
    log_file.write(today_date+':\n')
    statdata[today_date] = {
    "followers":0,
    "following":0,
    "addedfollowing":0,
    "removedfollowing":0,
    }
    #check for internet connection
    response =  CheckNetwork()
    try:
        config_file = open("config.json","r")
        log_file.write("config.json opened\n")
    except:
        log_file.write("config.json file error\n")
        Close()
    if not response:
        log_file.write("No internet Connection\n")
        Close()
    log_file.write("Active internet connection Found\n")

    config_data = json.load(config_file)

#check internet Connection
def CheckNetwork():
    testurl = 'www.google.com'
    try:
      # see if we can resolve the host name -- tells us if there is
      # a DNS listening
      host = socket.gethostbyname(testurl)
      # connect to the host -- tells us if the host is actually
      # reachable
      s = socket.create_connection((host, 80), 2)
      s.close()
      return True
    except:
       pass
    return False
#start browser
def StartBrowser():
    global browser
    if config_data["headless"] == "True":
        #browser in headless mode
        from selenium.webdriver.firefox.options import Options
        opts = Options()
        opts.set_headless()
        assert opts.headless  # Operating in headless mode
        browser = Firefox(options=opts)
    else:
        browser = Firefox()
#log in
def Login():
    base_url = "https://www.instagram.com/accounts/login/"
    browser.get(base_url)
    username_element = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.NAME, 'username')))
    if username_element:
        user_name = browser.find_element_by_name("username")
        password_field = browser.find_element_by_name("password")
        username = config_data["username"]
        password = config_data["password"]
        #fill user login credentials
        user_name.send_keys(username)
        password_field.send_keys(password)
        password_field.submit()
        try:
            login_result = browser.find_element_by_id("slfErrorAlert")
            if login_result:
                log_file.write(str(login_result.text)+'\n')
                #login unsuccesfull close the program
                Close()
        except:
            log_file.write("Login succesful \n")
    else:
        #username element not loaded
        log_file.write("Login form Failed to load\n")
        Close()
    #look for turn on notification button if popped up
    turn_on_element = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//div/button[text()="Turn On"]')))
    if turn_on_element:
        turn_on = browser.find_element_by_xpath('//div/button[text()="Turn On"]')
        turn_on.click()
    else:
        log_file.write("Turn on element not Found !\n")
        Close()
    #collect old data
    CollectStatisticsData()
#collect data
def CollectStatisticsData():
    browser.get("https://www.instagram.com/"+config_data["username"]+"/")
    follow_button_list = browser.find_elements_by_css_selector('ul li a')
    number_of_followers = remove.remove_space(follow_button_list[0].text)
    number_of_following = remove.remove_space(follow_button_list[1].text)
    statdata[today_date]["followers"] = int(number_of_followers)
    statdata[today_date]["following"] = int(number_of_following)
#remove following
def RemoveFollowing():
    #get actiom chain variable
    actionChain = webdriver.ActionChains(browser)
    browser.get("https://www.instagram.com/"+config_data["username"]+"/")
    follow_button_list = browser.find_elements_by_css_selector('ul li a')
    number_of_followers = remove.remove_space(follow_button_list[0].text)
    number_of_following = remove.remove_space(follow_button_list[1].text)
    #get all follwers usernames
    follow_button_list[0].click()#followers list button
    followerList_element =  WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role=\'dialog\'] ul')))
    if followerList_element:
        followersList = browser.find_element_by_css_selector('div[role=\'dialog\'] ul')
        numberOfFollowersInList = len(followersList.find_elements_by_css_selector('li'))
        followersList.find_element_by_css_selector('li').click()#change focus on followers list by clicking it
        while (numberOfFollowersInList < number_of_followers):
            actionChain.key_down(Keys.SPACE).key_up(Keys.SPACE).perform()
            numberOfFollowersInList = len(followersList.find_elements_by_css_selector('li'))
            sleep(1)
        #print("current followers found",numberOfFollowersInList)
    else:
        log_file.write("Followers not Found \n")
        Close()
    followers = []
    for user in followersList.find_elements_by_css_selector('li'):
        userLink = user.find_element_by_css_selector('a[title]').get_attribute('text')
        #print(userLink)
        followers.append(userLink)
        '''
        if (len(followers) == number_of_followers):
            break
        '''
    #comment in final version
    '''
    print(followers)
    print(len(followers))
    '''
    log_file.write("Followers UserNames Read\n")
    #sleep(4)
    close_button = browser.find_element_by_css_selector('div button svg[aria-label="Close"]')
    close_button.click()
    follow_button_list = browser.find_elements_by_css_selector('ul li a')
    follow_button_list[1].click()#following list button
    followingList_element =  WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role=\'dialog\'] ul')))

    #sleep(2)
    if followingList_element:

        followingList = browser.find_element_by_css_selector('div[role=\'dialog\'] ul')
        numberOfFollowingInList = len(followingList.find_elements_by_css_selector('li'))

        followingList.click()#change focus on followers list by clicking it
        #print(number_of_following)
        prev_numberOfFollowingInList = 0
        while (numberOfFollowingInList < number_of_following):
            if prev_numberOfFollowingInList == numberOfFollowingInList:
                followingList.click()
                sleep(2)
            actionChain.key_down(Keys.SPACE).perform()

            numberOfFollowingInList = len(followingList.find_elements_by_css_selector('li'))
            prev_numberOfFollowingInList = numberOfFollowingInList
            #followingList.find_element_by_css_selector('li').click()
            #print(numberOfFollowingInList)
            #print("current following found",numberOfFollowingInList)

    else:
        log_file.write("Following element not found \n")
        Close()
    following = []
    following_table = {}
    for user in followingList.find_elements_by_css_selector('li'):
        #dont remove verified profiles if specified in json
        if config_data["RemoveVerified"] == "False" :
            try :
                user.find_element_by_css_selector('div span[title="Verified"]') #verified profile ->  do not add to list
            except :
                userLink = user.find_element_by_css_selector('a[title]').get_attribute('text')
                #find the corresponding following button and create a dic of key:value = user:following_button
                follow_button = user.find_element_by_css_selector("div button")
                following_table[userLink] = follow_button
                following.append(userLink)
        else :
            userLink = user.find_element_by_css_selector('a[title]').get_attribute('text')
            #find the corresponding following button and create a dic of key:value = user:following_button
            follow_button = user.find_element_by_css_selector("div button")
            following_table[userLink] = follow_button
            following.append(userLink)

    '''
    print(following)
    print(len(following))
    '''
    log_file.write("Following UserNames Read\n")

    users_to_unfollow = []
    for following_variable in following:
        if following_variable not in followers:
            users_to_unfollow.append(following_variable)
    '''
    print(users_to_unfollow)
    print(len(users_to_unfollow))
    '''

    Number_of_following_removed = 0
    for user in users_to_unfollow:
        if Number_of_following_removed == config_data["unfollowThreshold"]:
            break
        following_table[user].click()
        #print("clicked!!")
        confirmButton_element =  WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//button[text() = "Unfollow"]')))
        if confirmButton_element:
            confirmButton = browser.find_element_by_xpath('//button[text() = "Unfollow"]')
            confirmButton.click()
            Number_of_following_removed += 1
        else:
            continue
        followingList.click()#change focus on followers list by clicking it
        #scroll down the list
        #unciomment if user is not found
        #actionChain.key_down(Keys.SPACE).key_up(Keys.SPACE).perform()
    statdata[today_date]["removedfollowing"] = Number_of_following_removed
        #print("number of users unfollowed")
        #count += 1

    #unfollow users

    close_button = browser.find_element_by_css_selector('div button svg[aria-label="Close"]')
    close_button.click()
#add following
def AddFollowing():
    actionChain = webdriver.ActionChains(browser)
    #find explore more users link in Instagram Main Page

    #login = False
    browser.get("https://www.instagram.com/")#go to main page
    #handle turn on notifications button
    turn_on_element = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//div/button[text()="Turn On"]')))
    if turn_on_element:
        turn_on = browser.find_element_by_xpath('//div/button[text()="Turn On"]')
        turn_on.click()
        #login = True
    see_all_element = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//a[@href="/explore/people/"]')))
    if see_all_element:
        see_all = browser.find_element_by_xpath('//a[@href="/explore/people/"]')
        see_all.click()
    else:
        log_file.write("Explore Link NOT found \n")
        Close()
    usersFoundOnPage = browser.find_elements_by_css_selector("div[aria-labelledby]")
    #print("number of users found",len(usersFoundOnPage))
    area_element = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'body span section main')))
    if area_element:
        area = browser.find_elements_by_css_selector('body span section main')
        area[0].click()
    else:
        log_file.write("Area Element not Found\n")
        Close()
    #if number of users to follow is less than then continue to follow procedure
    if len(usersFoundOnPage) < config_data['followersToAdd']:
        while(len(usersFoundOnPage))>config_data['followersToAdd']:

            area[0].click()
            sleep(1)
            actionChain.key_down(Keys.SPACE).key_up(Keys.SPACE).perform()
            sleep(2)
            usersFoundOnPage = browser.find_elements_by_css_selector("div[aria-labelledby]")
            #print(len(usersFoundOnPage))
        #print(len(usersFoundOnPage),"target REached...")
    #find all follow follow_buttons
    #change browser to usersFoundOnPage if possible
    Number_of_followers_added = 0
    follow_buttons = browser.find_elements_by_css_selector("div button[type][class]")
    if len(follow_buttons) >= config_data['followersToAdd']:
        for num in range(0,config_data['followersToAdd']):
            follow_buttons[num].click()
            Number_of_followers_added += 1
            sleep(2)
    else:
        log_file.write("Space Bar Error\n")
        Close()
    #else press space till users to follow >= users found on Page
    #log number of users followed
    log_file.write("Number of New followers Added : "+str(Number_of_followers_added)+'\n')
    log_file.write("Adding New Users Complete\n")
    statdata[today_date]["addedfollowing"] = Number_of_followers_added
#logout
def Logout():
    browser.get("https://www.instagram.com/"+config_data["username"]+"/")
    if WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div button svg[aria-label]'))):
        settings = browser.find_element_by_css_selector('div button svg[aria-label]')
        settings.click()
        if WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//button[text()="Log Out"]'))):
            logout = browser.find_element_by_xpath('//button[text()="Log Out"]')
            logout.click()
        else:
            log_file("Element Changed : Log Out\n")
    else:
        log_file.write("Element Changed : Settings\n")

#close and exit
def Close():
    stat_file = open("statistics.json","w")
    json.dump(statdata,stat_file)#write new stats to statistics.json file
    files_opened = [log_file,config_file,stat_file]
    log_file.write("Exiting Program\nClosing Files\n")
    for file in files_opened:
        if file:
            file.close()
    browser.close()
    sys.exit()
#main
if __name__ == "__main__":
    Init()
    StartBrowser()
    Login()
    if config_data["AddFollowers"] == "True" :
        AddFollowing()
    if config_data["RemoveFollowing"] == "True" :
        RemoveFollowing()
    Logout()
    Close()
