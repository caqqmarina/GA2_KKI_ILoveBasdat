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

### Roles

min
- subcategory services and service sessions
- service booking

bryant
- mypay
- mypay transactions

chi
- homepage
- discount

Cath
- profile
- logout
- testimonials
- service job and service job status


Docker configuration:

since we're using docker to manage postgres, its optimal to disable local postgres services

``Exporting:``

docker exec -i ga2_kki_ilovebasdat-postgres-1 pg_dump -U postgres -C -c postgres > db_dump.sql

``Copy the dump file into the container:``

docker cp db_dump.sql ga2_kki_ilovebasdat-postgres-1:/db_dump.sql

``Run the psql command to import the dump file:``

docker exec -i ga2_kki_ilovebasdat-postgres-1 psql -U postgres -d postgres -f /db_dump.sql