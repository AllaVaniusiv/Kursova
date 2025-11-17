# Kursova
# 1. Встановити залежності
pip install -r requirements.txt

# 2. Створити БД
python manage.py migrate

# 3. Створити суперкористувача
python manage.py createsuperuser

# 4. Заповнити тестовими даними
python populate_db.py

# 5. Запустити сервер
python manage.py runserver

# 6. Відкрити в браузері
http://localhost:8000
