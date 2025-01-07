from django.db import models

class Person(models.Model):
    id = models.BigAutoField(primary_key=True) # Création d'une clé primaire automatiquement via Django
    last_name= models.CharField(max_length=30)
    first_name=models.CharField(max_length=30)
    email=models.EmailField()
    phone=models.CharField(max_length=30)
    password=models.CharField(max_length=32)

    def __str__(self):
        return f"{self.first_name}   {self.last_name}"
class Plante(models.Model):
    author = models.ForeignKey('Person', on_delete=models.SET_NULL, null=True)
    publication_date = models.DateField()
    type_plante=models.TextField()
    description=models.CharField(max_length=100)
    def __str__(self):
        return self.type_plante

class Adress(models.Model):
    city=models.CharField(max_length=30)
    street=models.CharField(max_length=30)
    street_number=models.CharField(max_length=30)
    def __str__(self):
        return f"{self.city} and {self.street}"

class Quality(models.Model):
    diplome = models.CharField(max_length=30)
    details = models.CharField(max_length=100)
    def __str__(self):
        return self.diplome
class Professionnel(Person):
    quality=models.ForeignKey('quality', on_delete=models.SET_NULL, null=True)

class Classiq_User(Person):
    adress= models.ForeignKey('Adress', on_delete=models.SET_NULL, null=True)

