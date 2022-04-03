from django.db import models

class Artist(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=80)
    
    class Meta:
        db_table = "artist"
        