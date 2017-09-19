from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User
import datetime

MAX_USERNAME_LENGTH = 12
MAX_PASSWORD_LENGTH = 30
MAX_COURSECODE_LENGTH = 4
MAX_TITLE_LENGTH = 50


class PaperTitle(models.Model):
    title = models.TextField(max_length=MAX_TITLE_LENGTH)

    def __unicode__(self):
        return self.title


# TODO: Create Course -> Title functional dependency
class Paper(models.Model):
    course = models.CharField(max_length=MAX_COURSECODE_LENGTH)
    year = models.IntegerField()
    title = models.ForeignKey(PaperTitle)
    pdf = models.TextField()

    # Ensure year is greater then zero and less then current year.
    # Check that course code is valid?
    # NB: Must call full_clean() manually before calling save().
    def clean(self):
        if self.year < 0 or self.year > datetime.datetime.now().year:
            raise ValidationError('Year is not valid... fix this write a proper thing')

    class Meta:
        unique_together = ('course', 'year',)


class Question(models.Model):
    number = models.TextField()
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('paper', 'number')


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user = models.ForeignKey('auth.User', related_name='owner_of_answer', on_delete=models.CASCADE)
    votes = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)
    html = models.TextField()
    user_voted = models.TextField(default="", null=True, blank=True)


class Comment(models.Model):
    user = models.ForeignKey('auth.User', related_name='owner_of_comment', on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='child')
    timestamp = models.DateTimeField(auto_now_add=True)
    html = models.TextField()
