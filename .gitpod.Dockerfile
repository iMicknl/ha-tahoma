FROM gitpod/workspace-full:latest

USER gitpod

RUN pip3 install black && echo "export PIP_USER=no" >> /home/gitpod/.bashrc