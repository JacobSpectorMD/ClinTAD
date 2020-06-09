from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from .tokens import account_activation_token
from user.models import Profile, TrackManager, User


class PasswordResetForm(forms.ModelForm):
    email = forms.EmailField(label='Email')


class RegisterForm(forms.ModelForm):
    email = forms.EmailField(label='Email')
    name = forms.CharField(label='Name')
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', 'name',)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = User.objects.filter(email=email)
        if qs.exists():
            raise forms.ValidationError("email is taken")
        return email

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(RegisterForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            Profile.objects.create(user=user)
            TrackManager.objects.create(user=user)
            mail_subject = 'Activate your ClinTAD account.'
            message = render_to_string('activation_email.html',
                                       {'user': user, 'domain': 'www.clintad.com',
                                        'uid': urlsafe_base64_encode(force_bytes(user.id)).decode(),
                                        'token': account_activation_token.make_token(user)})
            email = EmailMessage(mail_subject, message, to=[user.email])
            email.send()

        return user


class LoginForm(forms.Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(widget=forms.PasswordInput)


class UserAdminCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', 'name')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserAdminCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            Profile.objects.create(user=user)
            TrackManager.objects.create(user=user)
        return user


class UserAdminChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('email', 'name', 'password', 'admin')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class TrackForm(forms.Form):
    builds_list = (('hg18 / 36.1', 'hg18 / 36.1'), ('hg19 / GRCh37', 'hg19 / GRCh37'),
                   ('hg38 / GRCh38', 'hg38 / GRCh38'))
    track_types = (('CNV', 'CNV'), ('Enhancer', 'Enhancer'), ('TAD', 'TAD'), )

    build = forms.ChoiceField(required=True, choices=builds_list)
    label = forms.CharField(required=True, max_length=200)
    track_type = forms.ChoiceField(required=True, choices=track_types)
    details = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 2}), max_length=2000)
    uploaded_file = forms.FileField(required=True)
