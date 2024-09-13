# Django bookmarks project
Bookmark images, share them, follow other people and explore what content they like to see and share. 

To use the project clone it to your local repo

Install the dependency's 
```
pip install -r requirements.txt
```
Apply django migrations 
```bash
python manage.py makemigrations
python manage.py migrate
```
install redis in docker
```bash
docker pull redis:7.2.4
```
up docker container 
```bash
docker run -it --name redis -p 6379:6379 redis:7.2.4
```

finally run 
```bash
python manage.py runserver 127.0.0.1:8000
```

Create an account to test the app

