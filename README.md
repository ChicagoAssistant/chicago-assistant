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

## Build Docker Image
