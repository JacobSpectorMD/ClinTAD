**Required Software**
- Install Python
    - ClinTAD was build with Python 3.6, but other version of Python 3 may work
- Install git
- Install PyCharm
    - The community edition is free
    
**Installation/Getting Started**
- Download or clone the code from GitHub
    - This can be done in the command prompt / terminal by navigating to a folder where you want to keep the project.
    I keep my projects in c:\apps so I would do:
        - `cd c:\apps `   
    - Then:
        - `git clone https://github.com/JacobSpectorMD/ClinTAD.git`
- Open PyCharm, and then open the ClinTAD folder in PyCharm
- Create a virtual environment in PyCharm
    - Go to File > Settings > Project:clintad > Project Interpreter
    - Click on the "Project Interpreter" dropdown menu towards the top, then "Show All" 
    - Click on the "+" button towards the right
    - Make sure "New Environment" is checked. Choose a location. Make sure Python 3.6 is the base interpreter
    - Click Ok and the virtual environment will be created
- Click on the "Terminal" button at the bottom-left of PyCharm
    - Make sure the name of your virtual environment shows in parenthesis, e.g.
        - `(clintad) C:\apps\clintad>` 
        - If it does not show up, close the terminal by clicking the X button on the left and re-open it
    - Install the required packages by typing:
        - `pip install -r requirements.txt`
- Run the server
    - `python manage.py runserver`     

- You should now be able to use ClinTAD by visiting 127.0.0.1:8000.  
- You can create an account and log in to easily create custom tracks.
- To run ClinTAD in the future you just need to:
    - Open the project in PyCharm
    - In the terminal type:
        - `python manage.py runserver`

- You can get updates for ClinTAD by typing:
    - `git pull`
    - It's possible this could cause you to lose your custom tracks, so make sure to have that data backed up!

- That's it!