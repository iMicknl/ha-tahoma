FROM gitpod/workspace-full:latest

USER gitpod

RUN pyenv install 3.9.7 &&\
    pyenv global 3.9.7 &&\
    echo "export PIP_USER=no" >> /home/gitpod/.bashrc &&\
    python -m pip install virtualenv
