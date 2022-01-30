from django.db import models

# Create your models here.
from django.contrib.auth.models import User


class Sheet (models.Model):
    Majentoid = models.ForeignKey(User, related_name='majentoname', on_delete=models.CASCADE)
    Uploaderid = models.ForeignKey(User, related_name='uploadername', on_delete=models.CASCADE)
    sheeturl = models.FileField(upload_to='Files/')
    ticketname = models.IntegerField()
    batchNumber = models.IntegerField()
    MajentoDate = models.DateTimeField()
    UploadedDate = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('ticketname','batchNumber')


    # def __str__(self):
    #     return self.


class Data_Field (models.Model):
    SKU = models.CharField(max_length=50,unique=True)
    Creatorid = models.ForeignKey(User, related_name='creatorname', on_delete=models.CASCADE)
    Qualityid = models.ForeignKey(User, related_name='qualityname', on_delete=models.CASCADE)
    Sheetid = models.ForeignKey(Sheet, related_name='ticket', on_delete=models.CASCADE)
    isRejected = models.BooleanField()
