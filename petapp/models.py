from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Pet(models.Model):
    name=models.CharField(max_length=50)
    type=models.CharField(max_length=20)
    breed = models.CharField(max_length=40)
    gender = models.CharField(max_length=6)
    age = models.IntegerField()
    price=models.FloatField()
    details=models.CharField(max_length=100)
    imagepath= models.ImageField(upload_to='image',default='')


class Cart(models.Model):
    uid = models.ForeignKey(User, on_delete=models.CASCADE, db_column='uid')
    petid = models.ForeignKey(Pet, on_delete=models.CASCADE, db_column='petid')
    quantity = models.IntegerField(default=1)

class Profile(models.Model):
    id= models.ForeignKey(User, on_delete=models.CASCADE, db_column="id", primary_key=True)
    mobile = models.CharField(max_length=10)
    address = models.TextField(max_length=100)

class Order(models.Model):
    orderid=models.CharField(max_length=50)
    userid= models.ForeignKey(User, on_delete=models.CASCADE, db_column="userid")
    petid= models.ForeignKey(Pet, on_delete=models.CASCADE, db_column="petid")
    quantity = models.IntegerField()
    