#!/bin/bash
set -e

python manage.py makemigrations document user
python manage.py migrate --no-input

python manage.py database_init

if [ "$RUN_FLAG" = "DEV" ]
then
  echo "from django.contrib.auth import get_user_model; User = get_user_model();"\
  "print('admin user already exists. Starting...') "\
  "if User.objects.filter(email='admin@admin.com').exists() "\
  "else User.objects.create_superuser('admin@admin.com', 'admin')" |
   python manage.py shell
fi

python manage.py runserver 0.0.0.0:8000