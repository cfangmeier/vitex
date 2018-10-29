# Source this script to setup ViTeX
python -m virtualenv env
source env/bin/activate
pip install -r requirements.txt
git submodule update --init nvim_config/bundle/Vundle.vim
