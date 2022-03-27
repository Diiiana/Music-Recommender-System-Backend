from django.db import models


class Tag(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=40)
    
    class Meta:
        db_table = "tag"


