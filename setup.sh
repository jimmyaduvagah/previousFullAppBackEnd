python manage.py migrate;
python manage.py createsuperuser;
python manage.py migrate;
python manage.py loaddata cms_locations_initial_data.json;
python manage.py loaddata cms_locations_states;
#python manage.py loaddata section_types;
#python manage.py loaddata specialties;
python manage.py loaddata groups;
python manage.py loaddata institutions;
python manage.py loaddata user_experience;

