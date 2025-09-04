from django.db import models
from django.conf import settings
# Create your models here.
class User(models.Model):
    First_name=models.CharField(max_length=100)
    Last_name=models.CharField(max_length=100)
    Email=models.CharField(max_length=50,unique=True)
    Password=models.CharField(max_length=20)
    Bank_Name=models.CharField(max_length=10)
    Account_number=models.CharField(max_length=15,unique=True)


class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('credit', 'Credit'),
        ('debit', 'Debit'),
    ]

    transaction_id = models.AutoField(primary_key=True)
    transaction_type = models.CharField(max_length=6, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    remark = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.CharField(max_length=50,blank=True,null=True)    
    to=models.CharField(max_length=10,blank=True,null=True)

    def __str__(self):
        return f'{self.transaction_type} - {self.amount} for {self.user}'
