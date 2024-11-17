# Database KKI 2024/2025 - Group Assignment 2
## Group members
* [Bryant Warrick Cai](https://github.com/bryantwarrickcai)
* [Catherine Aurellia](https://github.com/neaurellia)
* [Chiara Aqmarina Diankusumo](https://github.com/caqqmarina)
* [Min Kim](https://github.com/wuyu0107)

## Instructions
### Step 1
Clone this repository using this command:
```
https://github.com/caqqmarina/GA2_KKI_ILoveBasdat.git
```

### Step 2
Inside the root directory of this repository, run:

On Windows:
```
python -m venv env
```

On Linux/Mac:
```
python3 -m venv env
```

### Step 3
Activate the virtual environment by running:

On Windows:
```
env\Scripts\activate
```

On Linux/Mac:
```
source env/bin/activate
```

Note: On Windows, if you get an error that running scripts is disabled on your system, follow these steps:
1. Open Windows PowerShell as an administrator. (Search "PowerShell" on start menu, then right-click -> Run as administrator)
2. Run the following command: `Set-ExecutionPolicy Unrestricted -Force`

### Step 4
Inside the virtual environment (with `(env)` indicated in the terminal input line), run:
```
pip install -r requirements.txt
```

### Step 5
Run the following commands:

On Windows:
```
python manage.py makemigrations
python manage.py migrate
```

On Linux/Mac:
```
python3 manage.py makemigrations
python3 manage.py migrate
```

### Step 6
Run the server using the following command:

On Windows:
```
python manage.py runserver
```

On Linux/Mac:
```
python3 manage.py runserver
```
