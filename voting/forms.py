from django import forms
from .models import *
from account.forms import FormSettings


class VoterForm(FormSettings):
    class Meta:
        model = Voter
        fields = ['phone']


class PositionForm(FormSettings):
    class Meta:
        model = Position
        fields = ['name']


class CandidateForm(FormSettings):
    class Meta:
        model = Candidate
        fields = ['fullname', 'bio', 'position', 'photo']


class CountDownForm(FormSettings):
    class Meta:
        model = countDown
        fields = ['title', 'end_time_counter', 'view_flag', 'result_photo']
