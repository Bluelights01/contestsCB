from django.db import models

class Students(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
class Contest(models.Model):
    name = models.CharField(max_length=200, unique=True)      # Contest name
    date = models.DateField()                                  # Contest date
    start_time = models.TimeField()                            # Start time
    end_time = models.TimeField()                              # End time

    # Questions
    question_1 = models.CharField(max_length=300, blank=True)
    question_1_link = models.URLField(blank=True)

    question_2 = models.CharField(max_length=300, blank=True)
    question_2_link = models.URLField(blank=True)

    question_3 = models.CharField(max_length=300, blank=True)
    question_3_link = models.URLField(blank=True)

    def __str__(self):
        return f"{self.name} on {self.date}"
class IsLogin(models.Model):
    email = models.EmailField(unique=True)
    is_logged_in = models.BooleanField(default=False)
    leetcode_username = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.email} - {'Logged In' if self.is_logged_in else 'Logged Out'}"
from django.db import models

class ContestLeaderboard(models.Model):
    contest_name = models.CharField(max_length=100)
    user_name = models.CharField(max_length=100)
    marks = models.IntegerField(default=0)
    
    question1 = models.BooleanField(default=False)
    question2 = models.BooleanField(default=False)
    question3 = models.BooleanField(default=False)
    
    contest_date = models.DateField()

    def __str__(self):
        return f"{self.user_name} - {self.contest_name}"
