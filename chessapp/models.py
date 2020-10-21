from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    realname = models.CharField(max_length=20, blank=True)
    currentELO = models.IntegerField(default=1200)
    highestELO = models.IntegerField(default=1200)
    lowestELO = models.IntegerField(default=1200)


    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)


    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()


class Game(models.Model):


    player1 = models.CharField(max_length=20)
    player2 = models.CharField(max_length=20)
    result = models.FloatField()
    player1ELO = models.IntegerField()
    player2ELO = models.IntegerField()
    dateTime = models.DateTimeField(auto_now_add=True)


    def save_result(self, *args, **kwargs):
        self.result = round(self.result, 1)
        super(Game, self).save(*args, **kwargs)
