from django.db import models
from account.models import CustomUser
# Create your models here.


class Voter(models.Model):
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    phone = models.CharField(max_length=11, unique=True)  # Used for OTP
    voted = models.BooleanField(default=False)

    def __str__(self):
        return self.admin.username


class Position(models.Model):
    name = models.CharField(max_length=50, unique=True)
    priority = models.IntegerField()
   
    def __str__(self):
        return self.name


class Candidate(models.Model):
    fullname = models.CharField(max_length=50)
    photo = models.ImageField(default="avatar.jpg", upload_to="candidates")
    bio = models.TextField()
    position = models.ForeignKey(Position, on_delete=models.CASCADE)

    def __str__(self):
        return self.fullname


class Votes(models.Model):
    voter = models.ForeignKey(Voter, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    yes_vote = models.BooleanField(default=False)
    no_vote = models.BooleanField(default=False)


class countDown(models.Model):
    # start_time_counter = models.DateTimeField(auto_now_add=True)
    flag = (
    ('true', 'True'),
    ('false', 'False'),
)
    title = models.CharField(max_length=50)
    end_time_counter = models.DateTimeField()
    result_photo = models.ImageField(default="resultlist.jpg", upload_to="results")

    view_flag =  models.CharField(
        max_length=10,
        choices=flag,
        default='true',
    )

    def __str__(self):
        return self.title
    