import json
from datetime import date
import sys
import socket
from selenium.webdriver import Firefox
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import remove

#Flags
closed = False
added = False

def CheckRun():
    global today_date
    #get script running date
    global ran
    ran = False
    today_date = str(date.today())
    stat_file = open("statistics.json","r") #appending new keys to already written json file test required
    try:
        statdata = json.load(stat_file)
        #print("loaded json")
    except:
        return #first time running the script proceed to other Steps
    if today_date in statdata.keys():
        #print("script already ran !!")
        ran = True
    else:
        ran = False
        #print("Script running for first time on given date")
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
def Close():
    closed = True
    stat_file = open("statistics.json","w")
    json.dump(statdata,stat_file)#write new stats to statistics.json file
    files_opened = [log_file,config_file,stat_file]
    log_file.write("Exiting Program\nClosing Files\n")
    for file in files_opened:
        if file:
            file.close()
    browser.close()
    sys.exit()
def CollectStatisticsData(flag):
    if not closed:
        browser.get("https://www.instagram.com/"+config_data["username"]+"/")
        follow_button_list = browser.find_elements_by_css_selector('ul li a')
        number_of_followers = remove.remove_space(follow_button_list[0].text)
        number_of_following = remove.remove_space(follow_button_list[1].text)
        #if flag = True -> collecting old data
        if flag:
            statdata[today_date]["oldfollowers"] = int(number_of_followers)
            statdata[today_date]["oldfollowing"] = int(number_of_following)
        else:
            statdata[today_date]["newfollowers"] = int(number_of_followers)
            statdata[today_date]["newfollowing"] = int(number_of_following)

def Init():
    global config_data
    global config_file
    global log_file
    global statdata
    global stat_file

    #append data to log file
    log_file = open("log.txt","a")
    log_file.write(today_date+':\n')
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
    except:
        statdata = {}
    statdata[today_date] = {
    "oldfollowers":0,
    "oldfollowing":0,
    "addedfollowing":0,
    "removedfollowing":0,
    "newfollowers":0,
    "newfollowing":0,
    }
    #check for internet connection
    response =  CheckNetwork()
    if not response:
        log_file.write("No internet Connection\n")
        Close()
    log_file.write("Active internet connection Found\n")
    try:
        config_file = open("config.json","r")
        log_file.write("config.json opened\n")
    except:
        log_file.write("config.json file error\n")
        Close()
    config_data = json.load(config_file)

    #print(config_data)
    #Close(log_file,config_file)
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
def Login():
    global login
    login = False
    base_url = "https://www.instagram.com/accounts/login/"
    browser.get(base_url)
    sleep(4)#wait for browser to load web page
    user_name = browser.find_element_by_name("username")
    password_field = browser.find_element_by_name("password")
    username = config_data["username"]
    password = config_data["password"]
    #fill user login credentials
    user_name.send_keys(username)
    password_field.send_keys(password)
    password_field.submit()
    sleep(3)
    try:
        login_result = browser.find_element_by_id("slfErrorAlert")
        if login_result:
            log_file.write(str(login_result.text)+'\n')
        return
    except:
        log_file.write("Login succesful \n")
    sleep(3)
    #look for turn on notification button if popped up
    turn_on = browser.find_element_by_xpath('//div/button[text()="Turn On"]')
    if turn_on:
        turn_on.click()
        login = True
        log_file.write("Turn On notification button found\n")
        #print("test")
        sleep(3)
    else:
        log_file.write("Turn On notification button not found\n")
        return
    #collect old data
    CollectStatisticsData(True)
def AddFollowers():
    #find explore more users link in Instagram Main Page
    sleep(3)

    #login = False
    browser.get("https://www.instagram.com/")#go to main page
    #handle turn on notifications button
    turn_on = browser.find_element_by_xpath('//div/button[text()="Turn On"]')
    if turn_on:
        turn_on.click()
        #login = True
    see_all = browser.find_element_by_xpath('//a[@href="/explore/people/"]')
    if see_all:
        see_all.click()
    else:
        log_file.write("Explore Link NOT found \n")
        Close()
    sleep(10)
    usersFoundOnPage = browser.find_elements_by_css_selector("div[aria-labelledby]")
    #print("number of users found",len(usersFoundOnPage))
    area = browser.find_elements_by_css_selector('body span section main')
    #if number of users to follow is less than then continue to follow procedure
    if len(usersFoundOnPage) < config_data['followersToAdd']:
        while(len(usersFoundOnPage))>config_data['followersToAdd']:
            actionChain = webdriver.ActionChains(browser)
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
        return
    #else press space till users to follow >= users found on Page
    #log number of users followed
    log_file.write("Number of New followers Added : "+str(Number_of_followers_added)+'\n')
    log_file.write("Adding New Users Complete\n")
    added = True
    statdata[today_date]["addedfollowing"] = Number_of_followers_added

def RemoveFollowers():
    browser.get("https://www.instagram.com/"+config_data["username"]+"/")
    follow_button_list = browser.find_elements_by_css_selector('ul li a')
    number_of_followers = remove.remove_space(follow_button_list[0].text)
    number_of_following = remove.remove_space(follow_button_list[1].text)
    #get all follwers usernames
    follow_button_list[0].click()#followers list button
    sleep(5)
    followersList = browser.find_element_by_css_selector('div[role=\'dialog\'] ul')
    numberOfFollowersInList = len(followersList.find_elements_by_css_selector('li'))
    followersList.find_element_by_css_selector('li').click()#change focus on followers list by clicking it
    actionChain = webdriver.ActionChains(browser)
    sleep(5)
    while (numberOfFollowersInList < number_of_followers):
        actionChain.key_down(Keys.SPACE).key_up(Keys.SPACE).perform()
        numberOfFollowersInList = len(followersList.find_elements_by_css_selector('li'))
        sleep(4)
        #print("current followers found",numberOfFollowersInList)

    followers = []
    for user in followersList.find_elements_by_css_selector('li'):
        userLink = user.find_element_by_css_selector('a[title]').get_attribute('text')
        #print(userLink)
        followers.append(userLink)
        if (len(followers) == number_of_followers):
            break
    #comment in final version
    '''
    print(followers)
    print(len(followers))
    '''
    log_file.write("Followers UserNames Read\n")
    sleep(4)
    close_button = browser.find_element_by_css_selector('div button span[aria-label="Close"]')
    close_button.click()
    follow_button_list = browser.find_elements_by_css_selector('ul li a')
    follow_button_list[1].click()#following list button
    sleep(2)
    followingList = browser.find_element_by_css_selector('div[role=\'dialog\'] ul')
    numberOfFollowingInList = len(followingList.find_elements_by_css_selector('li'))
    followingList.click()#change focus on followers list by clicking it
    actionChain = webdriver.ActionChains(browser)
    while (numberOfFollowingInList < number_of_following):
        actionChain.key_down(Keys.SPACE).key_up(Keys.SPACE).perform()
        numberOfFollowingInList = len(followingList.find_elements_by_css_selector('li'))
        sleep(4)
        #print("current following found",numberOfFollowingInList)
        if numberOfFollowingInList==number_of_following-1:
            break

    following = []
    following_table = {}
    for user in followingList.find_elements_by_css_selector('li'):
        userLink = user.find_element_by_css_selector('a[title]').get_attribute('text')
        #find the corresponding following button and create a dic of key:value = user:following_button
        follow_button = user.find_element_by_css_selector("div button")
        following_table[userLink] = follow_button
        following.append(userLink)
        if (len(following) == number_of_following):
            break
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
    actionChain = webdriver.ActionChains(browser)
    for user in users_to_unfollow:

        if Number_of_following_removed == config_data["unfollowThreshold"]:
            break
        following_table[user].click()
        sleep(1)
        confirmButton = browser.find_element_by_xpath('//button[text() = "Unfollow"]')
        confirmButton.click()
        sleep(3)
        Number_of_following_removed += 1
        followingList.click()#change focus on followers list by clicking it
        #scroll down the list
        actionChain.key_down(Keys.SPACE).key_up(Keys.SPACE).perform()
    statdata[today_date]["removedfollowing"] = Number_of_following_removed
        #print("number of users unfollowed")
        #count += 1

    #unfollow users

    close_button = browser.find_element_by_css_selector('div button span[aria-label="Close"]')
    close_button.click()
def Logout():
    if not closed:
        browser.get("https://www.instagram.com/"+config_data["username"]+"/")
        settings = browser.find_element_by_css_selector('div button span[aria-label]')
        settings.click()
        sleep(2)
        logout = browser.find_element_by_xpath('//button[text()="Log Out"]')
        logout.click()



#Steps :
#0.Check whether script was ran before on the same day
#1.open all files for logging and info
#2.start browser
#3.login
#4.AddFollowers()
#5.RemoveFollowers()
#6.Logout()
if __name__ == "__main__":
    CheckRun()
    if not ran:

        Init()
        StartBrowser()
        Login()
        if login:
            #comment pass and uncomment AddFollowers() to add followers
            #pass

            if config_data["RemoveFollowing"]=="True":
                RemoveFollowers()
            if config_data["AddFollowers"]=="True":
                AddFollowers()

        CollectStatisticsData(False)
        Logout()
        Close()
    else:
        exit()
