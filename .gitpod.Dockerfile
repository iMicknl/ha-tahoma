FROM gitpod/workspace-full:latest

USER gitpod

RUN pyenv install 3.9.7 && pyenv global 3.9.7 && pip3 install black && echo "export PIP_USER=no" >> /home/gitpod/.bashrc
