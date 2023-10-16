
<p align="center">
<img height="200px" src="https://i.ibb.co/wyWh7s5/technex.jpg" alt="Loading img..."/>
<img height="200px"  src="https://user-images.githubusercontent.com/78701055/155997992-04602a01-5dd9-41c3-a563-597fabf7d8d1.jpg" alt="Loading img..."/>
</p>
<h1 align="center"> Technex-CA'23 Backend </h1>

### Working with repo:
1. Clone the repo in which you have to work in your system.
2. Create or do your work in other branch with relevant name.
3. After completing your work, commit your changes and push them.
4. Create a pull request (PR).

### Setting up the project(Backend) :

1. Creating virtual environment:
```bash
python -m venv venv
```
2. Activate virtual environment

Linux:
```bash
source venv/bin/activate
```
Windows:
```cmd
./venv/Scripts/activate
```
3. Install dependencies
```bash
pip install -r requirements.txt
```
4. Move to main folder: 
```bash
cd ca_backend
```
5. Apply migrations: 
```bash
python manage.py migrate
```
6. Collect static files : 
```bash
python manage.py collectstatic
```
7. Start the development server: 
```bash
python manage.py runserver
```