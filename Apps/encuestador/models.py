from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.contrib.auth.models import BaseUserManager
from enum import Enum
from django.conf import settings
from datetime import datetime, timedelta
from calendar import timegm
import jwt

##########################  ENUMS ##########################

class ClassificationChoice(Enum): # A subclass of Enum
    COMPONENT = 1
    DIMENSION = 2
    CATEGORY = 3

class LanguageChoice(Enum): # A subclass of Enum
    ES = "ESP"
    EN = "ENG"

class ResponseFormatType(Enum): # A subclass of Enum
    BOOL = "Yes/No"
    LIKERT_NINE = "Likert 9 points"
    LIKERT_SIX = "Likert 6 points"

class ProfileEnum(Enum):
    ADMIN = 1
    COMPANY = 2
    CLIENT = 3
    PARTICIPANT = 4

#######################  CLASES ################################

class Parametric_master (models.Model):
    name = models.CharField(max_length = 50)
    description = models.TextField()
    start_date = models.DateTimeField(auto_now=True)
    end_date = models.DateTimeField(default=None, null=True, blank=True)
    #option_group_id = models.IntegerField()

    def __str__(self):  # __unicode__ on Python 2
        return self.name


class Trans_parametric_table(models.Model):
    parametric_master = models.ForeignKey(Parametric_master, on_delete=models.CASCADE,related_name="detailsParameters")
    option_label = models.CharField(max_length=50)
    i18n_code = models.CharField(max_length=2)
    numeric_value = models.IntegerField()
    start_date = models.DateTimeField(auto_now=True)
    end_date = models.DateTimeField(default=None, null=True, blank=True)

    def __str__(self):  # __unicode__ on Python 2
        return self.option_label


class Response_format (models.Model):
    parametric_table = models.ForeignKey(Parametric_master, on_delete=models.CASCADE,)
    name = models.CharField(max_length = 50)
    type = models.CharField ( choices=[(tag, tag.value) for tag in ResponseFormatType],max_length = 15 ) # Choices is a list of Tuple)


    def __str__(self):  # __unicode__ on Python 2
        return self.name


#class item_hierarchy(models.Model):
    #ancestor = models.IntegerField()
    #descendant = models.IntegerField()
    #length = models.IntegerField()
    #length = models.IntegerField()



class ItemClassification(models.Model):
    name = models.CharField(max_length=50)
    type = models.IntegerField(
        choices=[(tag, tag.value) for tag in ClassificationChoice]  # Choices is a list of Tuple
    )
    i18n_code = models.CharField(max_length=40)

    def __str__(self):  # __unicode__ on Python 2
        return self.name + " -- type" + str(self.type)


class Item (models.Model):
    response_format = models.ForeignKey(Response_format, on_delete=models.CASCADE)
    item_order = models.IntegerField()
    dimension = models.ForeignKey(ItemClassification, related_name="itemsByDimension", on_delete=models.CASCADE,default=None)
    category = models.ForeignKey(ItemClassification,related_name="itemsByCategory", on_delete=models.CASCADE,default=None)
    component = models.ForeignKey(ItemClassification,related_name="itemsByComponent", on_delete=models.CASCADE,default=None,null=True,blank=True)


class Trans_item(models.Model):
    item = models.ForeignKey(Item, related_name='translations',on_delete=models.CASCADE)
    name = models.CharField(max_length=300)
    description = models.TextField(default=None,null=True,blank=True)
    i18n_code = models.CharField(max_length=40)

    def __str__(self):  # __unicode__ on Python 2
        return self.name

class Instrument_header(models.Model):
    version_name = models.CharField(max_length=50)
    is_active = models.BooleanField()
    start_date = models.DateTimeField(auto_now=True)
    end_date = models.DateTimeField(default=None, null=True, blank=True)


class Trans_instrument_header(models.Model):
    instrument_header = models.ForeignKey(Instrument_header, on_delete=models.CASCADE,related_name="translations")
    # None of these fields are mandatory
    general_description = models.TextField(default=None, null=True, blank=True)
    feature_description = models.TextField(default=None, null=True, blank=True)
    disclaimer = models.TextField(default=None, null=True, blank=True)
    user_instructions = models.TextField(default=None, null=True, blank=True)
    contact_info=models.TextField(default=None, null=True, blank=True)
    thanks=models.TextField(default=None, null=True, blank=True)
    i18n_code = models.CharField(max_length=2)


    def __str__(self):  # __unicode__ on Python 2
         # Control instruction in case the description is null
        if self.general_description ==None:
            description = ""
        else:
            description=self.general_description

        return "vesion: "+ self.instrument_header.version_name + " description: "+ description  + " " + " instructions: "+ " " + self.user_instructions



class Instrument_structure_history(models.Model):
    instrument_header = models.ForeignKey(Instrument_header, on_delete=models.CASCADE,related_name="itemsByInstrument")
    original_item = models.ForeignKey(Item,related_name="item_originalItem", on_delete=models.CASCADE,default=None)
    item_minor_version = models.CharField(max_length=20)
    new_item = models.ForeignKey(Item, related_name="item_newItem", on_delete=models.CASCADE, default=None)
    previous_item = models.ForeignKey(Item, related_name="item_previousItem", on_delete=models.CASCADE, default=None,null=True, blank=True)
    change_reason = models.TextField()
    is_active = models.BooleanField()
    start_date = models.DateTimeField(auto_now=True)
    end_date = models.DateTimeField(default=None, null=True, blank=True)

class Company(models.Model):
    company_contact_name = models.CharField(max_length=50)
    company_email = models.EmailField()
    name = models.CharField(max_length=100)

class Client(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    identification = models.CharField(max_length=50)
    client_logo = models.CharField(max_length=100, default=None, null=True, blank=True)
    contact = models.CharField(max_length=50)
    client_company_name = models.CharField(max_length=100)
    constitution_year = models.IntegerField()
    number_employees = models.IntegerField()
    is_corporate_group = models.BooleanField()
    is_family_company = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Config_surveys_by_clients(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    instrument_header = models.ForeignKey(Instrument_header, on_delete=models.CASCADE)
    # resulting_URL = models.URLField(default=None, null=True, blank=True)
    max_surveys= models.IntegerField(default=None, null=True, blank=True)
    used_surveys=  models.IntegerField(default=0)
    #JSON_instrument_file = models.BinaryField(default=None, null=True, blank=True)
    survey_conf_desc = models.TextField(default=None, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Customized_instrument(models.Model):
    config_survey= models.ForeignKey(Config_surveys_by_clients, on_delete=models.CASCADE)
    # Se quitan campos que ya estaban en config_survey
    # client = models.ForeignKey(Client, on_delete=models.CASCADE)
    # num_completed_responses = models.IntegerField(default=0)
    # num_partial_responses = models.IntegerField(default=0)

    # None of these fields are mandatory
    custom_general_description = models.TextField(default=None, null=True, blank=True)
    custom_feature_description = models.TextField(default=None, null=True, blank=True)
    custom_disclaimer = models.TextField(default=None, null=True, blank=True)
    custom_user_instructions = models.TextField(default=None, null=True, blank=True)
    custom_contact_info=models.TextField(default=None, null=True, blank=True)
    custom_thanks=models.TextField(default=None, null=True, blank=True)
    access_code = models.CharField(max_length=50,default=None)
    prefix= models.CharField(max_length=6,default=None)

class Surveys_by_client(models.Model):
    config_survey= models.ForeignKey(Config_surveys_by_clients, on_delete=models.CASCADE)
    # company = models.ForeignKey(Company, on_delete=models.CASCADE)
    # client = models.ForeignKey(Client, on_delete=models.CASCADE)
    acces_code = models.CharField(max_length=50)
    completed = models.BooleanField(default=False)
    #participant_response_header= models.ForeignKey(Participant_response_header, on_delete=models.CASCADE, default=None, null=True, blank=True)

class Participant_response_header(models.Model):
    customized_instrument = models.ForeignKey(Customized_instrument, on_delete=models.CASCADE)
    email = models.EmailField()
    last_update = models.DateTimeField(auto_now=True)
    is_complete = models.BooleanField(default=None)
    comments = models.TextField(default=None, null=True, blank=True)
    is_directive =  models.BooleanField()
    area = models.ForeignKey(Trans_parametric_table, related_name="area", on_delete=models.SET_NULL,
                                  default=None, null=True, blank=True)


class Items_respon_by_participants(models.Model):
    participant_response_header = models.ForeignKey(Participant_response_header, related_name="responsesList", on_delete=models.CASCADE,default=None, null=True, blank=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    answer_numeric = models.IntegerField()

class Item_classification_structure (models.Model):
    dimension = models.ForeignKey(ItemClassification, related_name="itemsClass_Dimension", on_delete=models.CASCADE,
                                  default=None)
    category = models.ForeignKey(ItemClassification, related_name="itemsClass_Category", on_delete=models.CASCADE,
                                 default=None)
    component = models.ForeignKey(ItemClassification, related_name="itemsClass_Component", on_delete=models.CASCADE,
                                  default=None, null=True, blank=True)


########################### User manager ########################################

class UserManager(BaseUserManager):
    """
    Django requires that custom users define their own Manager class. By
    inheriting from `BaseUserManager`, we get a lot of the same code used by
    Django to create a `User`.

    All we have to do is override the `create_user` function which we will use
    to create `User` objects.
    https://thinkster.io/tutorials/django-json-api/authentication
    """

    def _create_user(self, username, email, profileType, password=None, **extra_fields):
        """ Metodo privado para crear el usuario """
        if not username:
            raise ValueError('Se requiere un nombre de usuario')

        if not email:
            raise ValueError('Se requiere un email')

        email = self.normalize_email(email)
        user = self.model(username=username, email=self.normalize_email(email), profileType=profileType, **extra_fields)
        user.set_password(password)
        user.save()

        return user

    # By default profile 3 que es client
    def create_user(self, username, email, profileType=3, password=None, **extra_fields):
        """
        Create and return a `User` with an email, username and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email, profileType, password, **extra_fields)


    def create_superuser(self, username, email, profileType=1, password=None, **extra_fields):

      """
      Create and return a `User` with superuser (admin) permissions.
      Es obligatorio sobreescribir esta clase
      """
      if password is None:
          raise TypeError('Los superusuarios deben tener un password')

      """if extra_fields.get('is_staff') is not True:
        raise ValueError('Superuser must have is_staff=True.')

      if extra_fields.get('is_superuser') is not True:
        raise ValueError('Superuser must have is_superuser=True.')
      """
      extra_fields.setdefault('is_staff', True)
      extra_fields.setdefault('is_superuser', True)

      return self._create_user(username, email, profileType, password, **extra_fields)

# Clases asociadas a la autenticacion. Hereda de las clases principales de autenticacion de django
class User (AbstractBaseUser, PermissionsMixin):
    """
      Defines our custom user class.
      Username, email and password are required.
      Adapted from https://medium.com/@sebastianojeda/user-authentication-with-django-rest-framework-and-json-web-tokens-747ea4d84b9f
      """

    username = models.CharField(max_length=50)
    password_hashed = models.CharField(max_length=30)
    # Como puse al email como campo de autenticación tiene que ponerse unique=True
    email = models.EmailField(max_length=254, unique=True)

    # Campos que agregué pq no queda en el modelo aunque se deberia heredar de la clase abtracta
    # The `is_staff` flag is expected by Django to determine who can and cannot
    # log into the Django admin site. For most users this flag will always be
    # false.
    is_staff = models.BooleanField(default=False)

    # A timestamp representing when this object was created.
    created_at = models.DateTimeField(auto_now_add=True)

    # A timestamp reprensenting when this object was last updated.
    updated_at = models.DateTimeField(auto_now=True)

    # The `USERNAME_FIELD` property tells us which field we will use to log in.
    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ('username',)

    # Campos propios del modelo
    company = models.ForeignKey(Company, on_delete=models.SET_DEFAULT,
                                  default=None)
    client = models.ForeignKey(Client, on_delete=models.SET_DEFAULT,
                                default=None, null=True, blank=True)

    models.ForeignKey(Company, on_delete=models.CASCADE)

    profileType = models.IntegerField(
        choices=[(tag, tag.value) for tag in ProfileEnum]  # Choices is a list of Tuple
    )

    # Tells Django that the UserManager class defined above should manage
    # objects of this type.
    objects = UserManager()

    @property
    def token(self):
        """
        Allows us to get a user's token by calling `user.token` instead of
        `user.generate_jwt_token().

        The `@property` decorator above makes this possible. `token` is called
        a "dynamic property".
        """
        return self._generate_jwt_token()

    def get_full_name(self):
        """
        This method is required by Django for things like handling emails.
        Typically this would be the user's first and last name. Since we do
        not store the user's real name, we return their username instead.
        """
        return self.email

    def get_short_name(self):
        """
        This method is required by Django for things like handling emails.
        Typically, this would be the user's first name. Since we do not store
        the user's real name, we return their username instead.
        """
        return self.email

    def _generate_jwt_token(self):
        """
               Generates a JSON Web Token that stores the customized_instrument_id and has an expiry
               date set to 60 days into the future.
               """
        # dt = datetime.now() + timedelta(days=60)
        # exp_time = datetime.now() + timedelta(days=60)
        now = timegm(datetime.utcnow().utctimetuple())

        future = datetime.now() + timedelta(days=60)
        future_int = timegm(future.timetuple())
        # future_int = timegm(future.timetuple())
        # now_int = timegm(now.timetuple())
        print("future " + str(future))
        print("future number" + str(timegm(future.timetuple())))

        exp_time = timegm(datetime.utcnow().utctimetuple())
        id_client =None
        if (self.client != None):
            id_client = self.client.id
        payload = {
            #'email': self.email,
            'company_id':self.company.id,
            'client_id': id_client,
            'profile': self.profileType,
            'mode': 'byPwd',  # Indica que la autenticación fue por codigo de acceso, importante en la clase backend
            'exp': future_int
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

        if payload['exp'] < now:
            print("MODELS: El token expiró desde su creación. ERROR")
        return token.decode('utf-8')


    def __str__(self):
        """
        Returns a string representation of this `User`.
        This string is used when a `User` is printed in the console.
        """
        return self.username +' Profile ' +str(self.profileType)

