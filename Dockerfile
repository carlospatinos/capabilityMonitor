FROM ubuntu:14.04


# Replace 1000 with your user / group id #id -u username #id -g username
ENV DEV_HOME /home/developer
ENV HOME $DEV_HOME
ENV SOFTWARE_HOME $DEV_HOME/3pp

COPY files $DEV_HOME/

ENV TZ=Europe/Dublin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

#add-apt-repository "deb http://archive.ubuntu.com/ubuntu $(lsb_release -sc) main universe restricted multiverse" && 
RUN export https_proxy=www-proxy.carloscompany.se && \
	apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10 && \
	echo "deb http://repo.mongodb.org/apt/ubuntu "$(lsb_release -sc)"/mongodb-org/3.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.0.list && \
	apt-get update -y && \
	apt-get install -qqy curl nano wget vim zlibc zlib1g zlib1g-dev git software-properties-common x11-apps mongodb-org && \
	chmod a+x $DEV_HOME/*.py 

RUN apt-get install -y python2.7-dev python-pip python-software-properties && \
	pip install $SOFTWARE_HOME/enm_client_scripting-1.2.16-py2.py3-none-any.whl && pip install tabulate
#&& pip install flask

RUN apt-get install -y nodejs npm && sudo ln -s /usr/bin/nodejs /usr/local/bin/node && \
	npm install -g express && npm install -g express-generator

#X11 part
RUN export uid=142995 gid=17465 && \ 
    mkdir -p $DEV_HOME/ && mkdir -p $SOFTWARE_HOME/ && \
    echo "developer:x:${uid}:${gid}:Developer,,,:/home/developer:/bin/bash" >> /etc/passwd && \
    echo "developer:x:${uid}:" >> /etc/group && \
    echo "developer ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/developer && \
    chmod 0440 /etc/sudoers.d/developer && \
    chown ${uid}:${gid} -R $DEV_HOME/

#RUN export uid=142995 gid=17465 && \
#    mkdir -p /home/developer && \
#    echo "developer:x:${uid}:${gid}:Developer,,,:/home/developer:/bin/bash" >> /etc/passwd && \
#    echo "developer:x:${uid}:" >> /etc/group && \
#    echo "developer ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/developer && \
#    chmod 0440 /etc/sudoers.d/developer && \
#    chown ${uid}:${gid} -R /home/developer

USER developer
