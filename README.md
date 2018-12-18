**Installation**
- Install Python
    - ClinTAD was build with Python 3.6, but other version of Python 3 may work
- Install the requirements in requirements.txt
    - `pip install -r requirements.txt`
- Create the database
    - `python manage.py makemigrations`
    - `python manage.py migrate`
    
    
**Getting Started**
- Load Basic Data
    - Some basic data (e.g. gene coordinates, gene names) required by ClinTAD is in various files in the home/files folder.
      In order to load the data into the database use the following command (note this may take a substantial amount of
      time due to the large amount of data):
      - `python manage.py load all`
      
- You should now be able to use ClinTAD.  You can create an account and log in to easily create custom tracks.