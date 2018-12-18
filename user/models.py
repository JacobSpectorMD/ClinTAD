from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from datetime import datetime


class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None, editor=False, admin=False):
        if not email:
            raise ValueError("Please enter an email address.")
        if not password:
            raise ValueError("Please enter a password.")
        user = self.model(
            email = self.normalize_email(email)
        )
        user.set_password(password)
        user.name = name
        user.editor = editor
        user.admin = admin
        user.save(using=self._db)
        return user

    def create_editor(self, email, name, password=None):
        user = self.create_user(email, name, password=password, editor=True, admin=False)
        return user

    def create_superuser(self, email, name, password=None):
        user = self.create_user(email, name, password=password, editor=True, admin=True)
        return user

    def get_by_natural_key(self, username):
        case_insensitive_username_field = '{}__iexact'.format(self.model.USERNAME_FIELD)
        return self.get(**{case_insensitive_username_field: username})


class User(AbstractBaseUser):
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=100, default='')
    password = models.CharField(max_length=500, default='')
    staff = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    confirmed = models.BooleanField(default=False)
    last_login = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    objects = UserManager()

    def __str__(self):
        return self.name

    @property
    def get_name(self):
        return self.name

    @property
    def is_staff(self):
        return self.staff

    @property
    def is_admin(self):
        return self.admin

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def get_tracks(self):
        return self.tracks.all()  # tracks here refers to the home.UT model

    def get_tad_track(self):
        return self.tracks.filter(track__track_type='TAD', active=True).first()


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')


class TrackManager(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='track_manager')
    default_tads = models.BooleanField(default=True)
    default_enhancers = models.BooleanField(default=True)

    def track_json(self):
        tracks = [track.to_dict() for track in self.user.tracks.all()]
        return {'default_tads': self.default_tads, 'default_enhancers': self.default_enhancers, 'tracks': tracks}