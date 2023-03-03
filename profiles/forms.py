from django import forms
from django.contrib.auth import get_user_model
from .models import Profile

from crispy_forms.helper import FormHelper
from django.core.files.base import ContentFile

User = get_user_model()

#affects user update form





class ProfileForm(forms.ModelForm):
    last_name = forms.CharField(required=False)
    username = forms.CharField(required=False)
    first_name = forms.CharField(required=False)
    email = forms.CharField(required=False)
    satchel = forms.DecimalField(required=False)
    avatar = forms.ImageField(required=False)
    
    class Meta:
        model = Profile
        fields = ['satchel','last_name','first_name', 'username','location', 'avatar', 'bio','email']

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = True
        for field in ProfileForm.Meta.fields:
            self.fields[field].label = False
