# 🛠️ Development Setup

## 📁 Maintain Your Local `.env` File

Create a `.env` file at the project root with your environment-specific settings.

make sure that in you `.env` should contain the JWT_SECRET to maintain the core authentication


## Migration setup

# 📌 View all migrations and their status
python manage.py showmigrations

# 🛠️ Create migration files after model changes
python manage.py makemigrations

# 🚚 Apply all pending migrations
python manage.py migrate



## If you are going to migrate to a specific application make like this  ('sales', 'task', 'quotation')

#  View migrations for the 'sales' app
python manage.py showmigrations sales

# 🛠️ Create migrations only for the 'sales' app
python manage.py makemigrations sales

# 🚀 Apply migrations for the 'sales' app
python manage.py migrate sales






if you are using the djmigrator for the migration you can use this command only 

python manage.py smart_makemigrations