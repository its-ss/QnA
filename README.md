# Django Q&A
Django Q&A is online social media platform to ask question, answer, comment and upload media file.

## Technology
- Python-Django
- HTML,CSS & JS

## Steps To Startup Project
- - -

### Navigate to root folder and create virtual env

    python -m venv venv

### Activate virtual env

    source venv/bin/activate

### Update pip to latest version

    python -m pip install --upgrade pip setuptools wheel

### Install pip requirements

    pip3 install -r requirements.txt

### Makemigrations

    python manage.py makemigrations

### Migrate

    python manage.py migrate

### Create Superuser Account

    python manage.py createsuperuser

### Start server

    python manage.py runserver