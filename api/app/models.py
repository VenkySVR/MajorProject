from unittest import result
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
# from django.contrib.auth.models import User
# Create your models here.

def check(text):
        if text.upper() != 'SOLVED' and text.upper() != 'UNSOLVED':
            raise Exception('Status must be either Solved or Unsolved')

def score_check(score):
    if score < 0 :
        raise Exception('Score must be greter than 0')

class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        """
        Creates and saves a new user instance.
        """
        if not username:
            raise ValueError('The Username field must be set')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        """
        Creates and saves a new superuser instance.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, password, **extra_fields)

# class CustomUserManager(BaseUserManager):
#     def create_user(self, username, password=None, **extra_fields):
#         if not username:
#             raise ValueError('The Username field must be set')
#         user = self.model(username=username, **extra_fields)
#         user.set_password(password)
#         user.save(using=self._db)
#         return user

#     def create_superuser(self, username, password=None, **extra_fields):
#         extra_fields.setdefault('is_staff', True)
#         extra_fields.setdefault('is_superuser', True)
#         return self.create_user(username, password, **extra_fields)

class CustomUser(AbstractBaseUser,PermissionsMixin):
    username = models.CharField(unique=True, max_length=30)
    email = models.EmailField(unique=True, max_length=255)
    # first_name = models.CharField(max_length=30)
    # last_name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    # is_superuser = models.BooleanField(default=False)
    score = models.FloatField(default=0, validators=[score_check])
    solved = models.IntegerField(default=0)

    USERNAME_FIELD = 'username'
    # REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    objects = CustomUserManager()


# class CustomUser(User):
#     email = models.EmailField(unique=True, max_length=255)
#     score = models.FloatField(default=0, validators=[score_check])
#     solved = models.IntegerField(default=0)

#     class Meta:
#         ordering = ['-score']

#     def __str__(self):
#         return self.username


class Problem(models.Model):
    class Meta:
        ordering = ['-date_created']
    title = models.CharField(max_length=300)
    description = models.TextField()
    status = models.CharField(max_length=10, default='Unsolved',validators=[check,])
    difficulty = models.CharField(max_length=10, default='Easy')
    time_limit = models.IntegerField(default=1)
    memory_limit = models.IntegerField(default=128)
    score = models.FloatField(default=0, validators=[score_check])
    user = models.ManyToManyField(CustomUser)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class TestCases(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    input = models.TextField()
    output = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.problem.title + 'testcases set ' + str(self.id)

class Submissions(models.Model):
    
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    result = models.CharField(max_length=200)
    previous_submission = models.TextField(null=True, blank=True)
    language = models.CharField(max_length=10,null=True, blank=True)

    class Meta:
        ordering = ['-date_created']

    def __str__(self):
        return self.problem.title +'---' +self.user.username + "---"+self.result[:9]

class Code(models.Model):
    code = models.TextField()
    language = models.CharField(max_length=10)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    
class Stats(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    no_of_solutions = models.IntegerField(null=False, default=0)
    no_of_success = models.IntegerField(null=False, default=0)
    no_of_failure = models.IntegerField(null=False, default= 0)
    no_of_inprogress = models.IntegerField(null=False, default= 0)
    def __str__(self):
        return self.problem.title +"---" +self.no_of_solutions + "---"+self.no_of_inprogress