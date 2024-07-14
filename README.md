```
 ||||   ||   ||  ||||   ||||||    ||    ||||||    |||   ||||||  
  ||    |||  || ||  ||  | || |   ||||    ||  ||  || ||  | || |  
  ||    |||| || |||       ||    ||  ||   ||  || ||   ||   ||    
  ||    || ||||  |||      ||    ||  ||   |||||  ||   ||   ||    
  ||    ||  |||    |||    ||    ||||||   ||  || ||   ||   ||    
  ||    ||   || ||  ||    ||    ||  ||   ||  ||  || ||    ||    
 ||||   ||   ||  ||||    ||||   ||  ||  ||||||    |||    ||||   

```

Bot for Instagram based on Selenium.

Logins, adds Following, Removes Following if not followed back after waiting N days and Collects statistics !, just like most Instagram users do.

```
# to run script
python3 InstaBot.py
```

#### Configuring the bot using config.json

Bot behaviour and user account details can be controlled using json file, key-value pairs are self explainatory. currently password is specified in plain text, this will be improved in further commits.

config.json
```
{
  "username": "yyyyyyyyttttttt1111111",
  "password": "Abom6lg058",
  "headless": "True",
  "add_following" : "True",
  "random_add" : "True",
  "max_follower_add" : 100,
  "remove_following" : "True",
  "days_to_wait" : 0
}
```

**headless** - this controls whether browser should run in Full GUI or not.

**add_following** - set this to "True" if you want to add followers next time the script runs.

**random_add** - usually following are added linearly as shown in the explore page, if following to add is a large number(controlled using max_follower_add) this marks your account as a bot, so to avoid this set this to "True".

**max_follower_add** - number of following to add from explore page, if random_add is set "True", this number is used as a upper limit to generate a random max_follower_add.

**removed_following** - if set to "True", checks if days_to_wait has elapsed, and removes following of the users cached in cache pickle file.

**days_to_wait** - number of days to wait after added following to remove the users if not followed back.

### Running as anacron job

The whole idea of this project being if just adding and removing following after N days will get you followers. since thats what most users do to get people followng them aka mutual following.
running this script daily to achieve above mentioned task can be tedious, thats where anacron comes to play.

**modfiying /etc/anacrontab**

```
<days>   <delay>   <job-id>   python3 /home/<sys_user>/<path_to_InstaBot_directory>
```

**days** - 1, 7, 30 for daily weekly and monthly requirements

**delay** - minutes of delay before running after system startup

**job-id** - unique job-id, choose one which does not conflict with existing system anacron jobs.

### Adding new behaviours

Adding new behaviours is simple as defining new routines and calling them from "\__main\__" following existing methods to log any info or errors, ex: for removing all followers at once. any contributions and feedback are welcome :^).

## TODO :

- [x] Update logic for scrolling down in explore page

- [ ] Update logic to use one function for scrolling

- [x] add anacron file/Instructions
