from django.db import models
from django.utils import timezone
from enum import Enum

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

"""Por ahora no sirve para nada, creo que la voy a eliminar"""
class ClassificationAndItems:
    itemClassification=models.ForeignKey(ItemClassification, related_name="itemClassification", on_delete=models.CASCADE,default=None)
    item=models.ForeignKey(Item, related_name="items", on_delete=models.CASCADE,default=None)

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

class Client(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    client_logo = models.CharField(max_length=100)
    contact = models.CharField(max_length=50)
    client_company_name = models.CharField(max_length=100)
    constitution_year = models.IntegerField()
    number_employees = models.IntegerField()
    is_corporate_group = models.BooleanField()
    is_family_company = models.BooleanField()


class Config_surveys_by_clients(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    instrument_header = models.ForeignKey(Instrument_header, on_delete=models.CASCADE)
    resulting_URL = models.URLField(default=None, null=True, blank=True)
    max_surveys= models.IntegerField(default=None, null=True, blank=True)
    used_surveys=  models.IntegerField(default=0)
    JSON_instrument_file = models.BinaryField(default=None, null=True, blank=True)

class Customized_instrument(models.Model):
    config_survey= models.ForeignKey(Config_surveys_by_clients, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    num_completed_responses = models.IntegerField(default=0)
    num_partial_responses = models.IntegerField(default=0)

    # None of these fields are mandatory
    custom_general_description = models.TextField(default=None, null=True, blank=True)
    custom_feature_description = models.TextField(default=None, null=True, blank=True)
    custom_disclaimer = models.TextField(default=None, null=True, blank=True)
    custom_user_instructions = models.TextField(default=None, null=True, blank=True)
    custom_contact_info=models.TextField(default=None, null=True, blank=True)

class Surveys_by_client(models.Model):
    config_survey= models.ForeignKey(Config_surveys_by_clients, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    acces_code = models.CharField(max_length=50)
    completed = models.BooleanField(default=False)
    #participant_response_header= models.ForeignKey(Participant_response_header, on_delete=models.CASCADE, default=None, null=True, blank=True)

class Participant_response_header(models.Model):
    customized_instrument = models.ForeignKey(Customized_instrument, on_delete=models.CASCADE)
    survey_by_client = models.ForeignKey(Surveys_by_client, on_delete=models.CASCADE)
    email = models.EmailField()
    last_update = models.DateTimeField()
    is_complete = models.BooleanField(default=None)
    comments = models.TextField(default=None, null=True, blank=True)
    isADirective =  models.BooleanField()
    position = models.IntegerField(default=None, null=True, blank=True)
    area = models.IntegerField()


class Items_respon_by_participants(models.Model):
    participant_response_header = models.ForeignKey(Participant_response_header, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    answer_numeric = models.IntegerField()
    answer_text = models.TextField()

class User (models.Model):
    username = models.CharField(max_length=50)
    password_hashed = models.CharField(max_length=30)
    organization = models.CharField(max_length=50)
    organization_department = models.CharField(max_length=50)
    email = models.EmailField()
    website = models.URLField()
    last_login = models.DateTimeField()
    active_account = models.BooleanField()
    registration_date = models.DateTimeField()
    prefered_language = models.CharField(max_length=30)

class Roles_by_user(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=50)
