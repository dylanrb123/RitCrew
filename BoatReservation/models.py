from django.contrib.auth.models import User
from django.db import models

class Boat(models.Model):
    def __str__(self):
        return str(self.name) + ': ' + str(self.weight_class) + " " + str(self.model) + " " + str(self.type)

    name = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    weight_class = models.CharField(max_length=100)
    type = models.CharField(max_length=100)


class Reservation(models.Model):
    def __str__(self):
        return str(self.user.username) + ": " + str(self.start_time) + " to " + str(self.end_time)

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    user = models.ForeignKey(User)
    boat = models.ForeignKey(Boat)

