rm -rf Department/migrations
rm -rf User/migrations
python3 manage.py makemigrations Department
python3 manage.py makemigrations User
python3 manage.py migrate

sh test.sh