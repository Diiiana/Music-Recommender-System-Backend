# MusicRecommenderSystem_backend


Limbajul de programare folosit: Python 3.10 <br />
<br />
Pentru instalarea proiectului, se utilieaza comenzile:

1. ```git clone https://github.com/Diiiana/MusicRecommenderSystem_backend.git```      &emsp; - descarcare proiect
2. ```python pthon -m venv env```                                                     &emsp; - creare environment
3. ```env\Scripts\activate```                                                         &emsp; - activare environment
<hr />
Instalare biblioteci utilizate<br />

4. ```pip install django``` <br />
5. ```pip install djangorestframework``` <br />
6. ```pip install django-cors-headers``` <br />
7. ```pip install --upgrade djangorestframework-simplejwt``` <br />
8. ```pip install psycopg2``` <br />
9. ```pip install numpy``` <br />
10. ```pip install pandas``` <br />
11. ```pip install tensorflow``` <br />
12. ```pip install sklearn``` <br />
13. ```pip install cython``` <br />
14. ```pip install git+https://github.com/ing-bank/sparse_dot_topn.git``` <br />
15. ```pip install lightfm``` <br />

Dupa instalarea proiectului, se ruleaza comenzile pentru a migra baza de date: <br />
python manage.py makemigrations <br />
python manage.py migrate <br />

Ulterior, datele sunt adaugate in baza de date de la https://www.kaggle.com/datasets/dianaurcan/music-recommendations <br />
Pasi: <br />
1. COPY (id, name) FROM '/artists.csv' WITH (FORMAT csv);<br />
2. Selectare optiune restore pentru 'backup_songs'<br />
3. COPY (id, name) FROM '/tag.csv' WITH (FORMAT csv);<br />
4. COPY (song_id, tag_id) FROM '/song_tag.csv' WITH (FORMAT csv);<br />
5. COPY (id, user_id, song_id, liked, user_int_id) FROM '/likes.csv' WITH (FORMAT csv);<br />
