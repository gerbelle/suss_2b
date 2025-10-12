# Prerequisites
1. Git: For cloning the repository.
2. Python 3.x
3. MongoDB

# Installation and Setup
1. Clone the Repository
Open your terminal (or VSCode's bash Terminal) and use Git to download the project files:
```
git clone https://github.com/gerbelle/tma_qn2b_3
cd tma_qn2b_3
```
2. Create and Activate a Virtual Environment
```
#delete the venv folder and create your own virtual envrioment in your terminal 

1. python -m venv venv
2. source venv/Scripts/activate
```

# install dependencies
```
pip install -r requirements.txt
```

# connect to Mongodb
```
1. install Mongodb extension on vsc
add connection string
2. mongodb://localhost:27017
```

# run the application 
```
1. cd app
2. flask run --debug OR python -m flask --debug run
3. open web browser and go to http://127.0.0.1:5000/
