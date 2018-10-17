# Chicago Assistant

The Chicago Assistant is a text and voice interface for requesting and inquiring about city services. Functionalities we are currently exploring include:
 - Submit 311 Service Requests
 - Get transit arrival times and station accessibility information
 - Request information about common city services such as getting a vehicle city sticker, school closures, street cleaning schedules, etc.
 - Contacting your alderman
 - Got an idea? [Share it with us!](google.com)

The text and voice interface will be accessible via SMS, popular messaging platforms like Facebook Messenger and voice interfaces like Amazon Alexa and Google Assistant.

The project aims to improve ease of accessibility to city services and information about city services by creating a text and voice channel, complimenting existing web and telephone (311) channels.

**Depricated Prototype:** http://chicago-assistant-depricated.herokuapp.com/

### Current Functionality in Development
 - Submit 311 Requests


### Join Us At Chi Hack Night
**Slack Channel** #chivirtualassistant


### Getting Started and Connected

 - [Trello Board](https://trello.com/b/6EPQugQN/chicago-virtual-assistant)
 - [Google Drive](https://drive.google.com/drive/u/0/folders/1DqmKrKWWF3-UyAipF8fifp9cPf-4Dn4S)

#### Learning to Build Conversation Interfaces
The learning curve for building conversational interfaces can be a steep. We have been curating a [Get Started](https://docs.google.com/document/d/1x4VDO_P0xF3DU7roLi8Uey2zNs308GA9i625JU1c_oE/edit?usp=drive_web&ouid=109439844092806383542**) document that covers our groups mission in addition to pointing you to helpful resources for learning about conversational interfaces. 
**Helpful Learning Resources***
 - Read - [Rasa Documentation](https://www.rasa.com/docs/nlu)
 - Watch - [Helpful Technical Video](https://www.youtube.com/watch?v=zRqjH7fT0G0)
 - Listen - [DataFramed Podcast Interview with Rasa Founder](https://www.datacamp.com/community/podcast/chatbots)


# Getting Started [Mac OS]

## Installing Docker
Install Docker  

`brew cask install docker`

Once it's done installing, open up the application Launcher and start Docker. You'll be prompted for your password to complete the installation.

**At this time, there is no need to create a Docker ID if you don't have one.**


## Clone Repository
Open up a **Terminal** and navigate to a folder where you maintain your projects. In my case, I keep my projects in a **Projects** folder within my home directory.

To clone the repository, run  

`git clone --single-branch -b get-started https://github.com/ChicagoAssistant/chicago-assistant.git`

If you already have the repository cloned to your computer, copy the get-started repo to your machine by running

`git checkout --track origin/get-started`


## Create Your Own Branch
Create your own branch by running (**NOTE: do not use the brackets**):  

`git branch [yourname]-dev`  

Switch to your newly created branch:  

`git checkout [yourname]-dev`

Add everything and push your changes:  

`git add .`  
`git commit -m"initial commit"`  
`git push`

## Build Docker Image (Alternative Below)
Now, we're going to build the Docker Image. This make take around 10 minutes to complete.  

`docker build -t chicago-assistant .`

Once complete, you should be all set to start building a Chicago Assistant functionality! Before we get there, though, let's see exactly how that would happen.

## Alternative to Building Docker Image

1. Create a [Docker ID](https://cloud.docker.com/).

2. Get added to the Chicago Assistant Team on Docker. Ask Vidal to add you by giving him your Docker ID username.

3. Login using `docker login -u [username] -p`

4. Run `docker pull chicagoassistant/chicago-assistant`




## Starting Up the Container

You can start our virtual container environment by running:

`docker run --rm --name chicago-assistant -it -v [path for repo]:/chicago-assistant chicago-assistant bash`

Make sure to replace [path for repo] with the full path of your local repository for this project. So, in my case, my full path would be

`docker run --rm --name chicago-assistant -it -v /Users/vanguiano/Projects/chicago-assistant:/chicago-assistant chicago-assistant bash`

You'll know you've successfully started up the virtual container when you see:

`root@[somenum_letters]:/#`

Finally, you should navigate to your project repository by running:

`cd chicago-assistant`

## Training the Models

You can train the NLU and core functions of our project by running the following:

`make train-nlu`

`make train-core`

Running these commands should create a new folder in your repo called `models`.


## Chatting with the Bot

To chat with the newly trained bot, you can run:

`make run-cmdline`

and after a few seconds you should see (**Ignore the warnings**):

```
WARNING  py.warnings  - /usr/local/lib/python3.5/site-packages/pykwalify/core.py:99: UnsafeLoaderWarning:
The default 'Loader' for 'load(stream)' without further arguments can be unsafe.
Use 'load(stream, Loader=ruamel.yaml.Loader)' explicitly if that is OK.
Alternatively include the following in your code:

  import warnings
  warnings.simplefilter('ignore', ruamel.yaml.error.UnsafeLoaderWarning)

In most other cases you should consider using 'safe_load(stream)'
  data = yaml.load(stream)

Bot loaded. Type a message and press enter: ```

Try talking to it!

You can exit the chat by hitting **CNTL + C**. Finally, you can exit the created container by typing `exit`.
