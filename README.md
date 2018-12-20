**Installation/Getting Started**
- If you are unfamiliar with Python, the video instructions on ClinTAD.com may be easier for you to follow
- Install Python
    - ClinTAD was build with Python 3.6, but other version of Python 3 may work
- Install git

- Download or clone the code from GitHub
    - This can be done in the command prompt / terminal by navigating to a folder where you want to keep the project, then:
        - `git clone https://github.com/JacobSpectorMD/ClinTAD.git`
        
- Create a virtual environment
    - Install virtualenv if you do not have it already
        - In command prompt/terminal type `pip install virtualenv`
    - Navigate to the folder where you want your virtual environment then
        - `virtualenv ChooseAName`
- Install the requirements in requirements.txt to your virtual environment
    - Activate the virtual environment by changing to the Scripts folder in your virtual environment folder then typing
        - `activate`
    - `pip install -r requirements.txt`

- Run the server
    - Use the terminal with the virtual environment activated to navigate to the ClinTAD folder, then:
    - `python manage.py runserver`     

- You should now be able to use ClinTAD.  You can create an account and log in to easily create custom tracks.
- To run ClinTAD in the future:
    - Navigate to the Scripts folder of your virtual environment in the terminal / command prompt
        - `activate`
    - Navigate to the ClinTAD folder
        - `python manage.py runserver`