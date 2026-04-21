# 🛠️ Development Setup

## 📁 Maintain Your Local `.env` File

Create a `.env` file at the project root with your environment-specific settings.



## Migration setup

# 📌 View all migrations and their status
python manage.py showmigrations

# 🛠️ Create migration files after model changes
python manage.py makemigrations

# 🚚 Apply all pending migrations
python manage.py migrate



## If you are going to migrate to a specific application make like this 

# 🔍 View migrations for the 'envoy' app
python manage.py showmigrations envoy

# 🛠️ Create migrations only for the 'envoy' app
python manage.py makemigrations envoy

# 🚀 Apply migrations for the 'envoy' app
python manage.py migrate envoy
