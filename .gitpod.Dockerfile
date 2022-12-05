FROM gitpod/workspace-full

# Install node https://www.gitpod.io/docs/introduction/languages/javascript
RUN bash -c 'VERSION="18.12.1" \
    && source $HOME/.nvm/nvm.sh && nvm install $VERSION \
    && nvm use $VERSION && nvm alias default $VERSION'
RUN echo "nvm use default &>/dev/null" >> ~/.bashrc.d/51-nvm-fix

# Install python
RUN pyenv install 3.11-dev && pyenv global 3.11-dev
