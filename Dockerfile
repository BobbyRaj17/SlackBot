FROM ubuntu:16.04

MAINTAINER HUD-BLR<#hud-baagh>

# get up to date
RUN apt-get update --fix-missing

#Installing PIP
RUN apt-get install -y python python-dev python-setuptools
RUN apt-get install -y python-pip

# set /app directory as default working directory
WORKDIR /usr/src/app

# copying requirement.txt to working dir
COPY requirement.txt /usr/src/app

#Install Python libraries
RUN pip install -r requirement.txt
RUN [ "python", "-c", "import nltk; nltk.download('punkt')" ]

#Installing supervisord
RUN apt-get update && apt-get install -y supervisor
RUN pip install supervisor-stdout
#setting up workspace and copying files
WORKDIR /usr/src/app
COPY . /usr/src/app

#Creating log directory for supervisor
RUN mkdir -p /var/log/supervisord

#supervisord has instruction for both Flask and slack bot
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# set enviornemt variable
# Follow the link to create your own webhook token - https://get.slack.help/hc/en-us/articles/215770388-Create-and-regenerate-API-tokens
ENV SLACK_BOT_TOKEN <SLACK BOT TOKEN>
ENV SLACK_WEBHOOK_SECRET <SLACK WEBHOOK SECRET>

#Default Flask runs on 5000 port
EXPOSE 5000 443 8080

#Starting flask and slack Bot
CMD ["/usr/bin/supervisord"]
