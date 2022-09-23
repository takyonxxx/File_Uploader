from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models, transaction
from django.utils import timezone

from main.utils import generate_pk


class Module(models.Model):
    id = models.CharField(primary_key=True, max_length=255, editable=False)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, null=True)
    created = models.DateTimeField(default=timezone.now)
    id_prefix = 'mod'

    def save(self, *args, **kwargs):
        if not self.id:
            id_prefix = getattr(self, 'id_prefix')
            if id_prefix is not None:
                setattr(self, 'id', generate_pk(self.id_prefix))
        super(Module, self).save(*args, **kwargs)
        return self

    class Meta:
        db_table = 'module'
        ordering = ('created',)


class Permission(models.Model):
    id = models.CharField(primary_key=True, max_length=255, editable=False)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, null=True)
    module = models.ForeignKey(Module, on_delete=models.CASCADE, null=True, related_name='children')
    created = models.DateTimeField(default=timezone.now)
    id_prefix = 'prm'

    def save(self, *args, **kwargs):
        if not self.id:
            id_prefix = getattr(self, 'id_prefix')
            if id_prefix is not None:
                setattr(self, 'id', generate_pk(self.id_prefix))
        super(Permission, self).save(*args, **kwargs)
        return self

    class Meta:
        db_table = 'permissions'
        ordering = ('created',)


class Role(models.Model):
    id = models.CharField(primary_key=True, max_length=255, editable=False)
    name = models.CharField(max_length=500, null=True)
    permissions = models.ManyToManyField(Permission, blank=True)
    created = models.DateTimeField(default=timezone.now)

    id_prefix = 'rol'

    def get_role_permissions(self):
        return list(Permission.objects.filter(role=self))

    def save(self, *args, **kwargs):
        if not self.id:
            id_prefix = getattr(self, 'id_prefix')
            if id_prefix is not None:
                setattr(self, 'id', generate_pk(self.id_prefix))
        super(Role, self).save(*args, **kwargs)
        return self

    class Meta:
        db_table = 'roles'
        ordering = ('created',)


class UserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email,and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        with transaction.atomic():
            user = self.model(email=email, **extra_fields)
            if not password:
                user.password = make_password('123')
            else:
                user.password = make_password(password)
            # if self:
            #     user.password = make_password('123')
            # else:
            #     user.password = make_password(password)
            user.save(using=self._db)
            if extra_fields.get('is_staff'):
                user.roles.add('rol-3c1bd4193t89f2d')
            user.save(using=self._db)
            return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(email, password=password, **extra_fields)


class User(AbstractBaseUser):
    ldap_domain = 'demo.com.tr'
    id = models.CharField(primary_key=True, max_length=255, editable=False)
    email = models.EmailField(max_length=99, unique=True)
    first_name = models.CharField(max_length=99, blank=False, null=False)
    last_name = models.CharField(max_length=99, blank=False, null=False)
    domain = models.CharField(max_length=99, blank=True, null=True, default=ldap_domain)
    roles = models.ManyToManyField(Role, blank=True)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    created = models.DateTimeField(default=timezone.now)
    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    id_prefix = 'usr'

    @property
    def full_name(self):
        return '%s %s' % (self.first_name, self.last_name)

    def get_user_roles(self):
        return Role.objects.filter(user=self)

    def save(self, *args, **kwargs):
        if not self.id:
            id_prefix = getattr(self, 'id_prefix')
            if id_prefix is not None:
                setattr(self, 'id', generate_pk(self.id_prefix))
        super(User, self).save(*args, **kwargs)
        return self

    class Meta:
        db_table = 'users'
        ordering = ('-created',)
