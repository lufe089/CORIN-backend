from calendar import timegm, calendar

from Apps.encuestador.models import ItemClassification
from Apps.encuestador.models import Item
from Apps.encuestador.models import Instrument_header
from Apps.encuestador.models import Response_format
from Apps.encuestador.models import Trans_item
from Apps.encuestador.models import Company
from Apps.encuestador.models import Client
from Apps.encuestador.models import Participant_response_header
from Apps.encuestador.models import Customized_instrument
from Apps.encuestador.models import Config_surveys_by_clients
from Apps.encuestador.models import Trans_instrument_header
from Apps.encuestador.models import Items_respon_by_participants
from Apps.encuestador.models import Instrument_structure_history
from Apps.encuestador.models import Surveys_by_client,Trans_parametric_table
from Apps.encuestador.models import LanguageChoice
from rest_framework.views import APIView
from rest_framework import serializers
from django.conf import settings
from datetime import datetime, timedelta

from rest_framework.response import Response

import jwt

class CompanySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Company
        #fields = ('company_contact_name','company_email')
        fields = ('__all__')

class ClientSerializer(serializers.HyperlinkedModelSerializer):
    company = CompanySerializer(many=False, read_only=True)
    company_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = Client
        #fields = ('max_surveys','used_surveys','contact')
        fields =('id','identification','company','company_id','client_company_name','constitution_year','number_employees','is_corporate_group','is_family_company')


class ResponseFormatSerializer(serializers.HyperlinkedModelSerializer):
    #parametric_table=serializers.PrimaryKeyRelatedField(many=False, read_only=True)
    parametric_table_id=serializers.IntegerField(write_only=True)
    class Meta:
        model = Response_format
        #fields = ('name', 'description','i18n_code','translations')
        #fields = ('name','type','numeric_value','parametric_table_id')

# Serializa el instrumento
class InstrumentHeaderSerializer(serializers.HyperlinkedModelSerializer):
    # itemsByInstrument=InstrumentStructureHistorySerializerOnlyActiveItems(many=True,read_only=True)
    # itemsByInstrumentSet = Instrument_header.objects.filter(itemsByInstrument__is_active=True).values(
    #   'itemsByInstrument__new_item')
    # itemClassification = ItemClassification.objects.filter(itemsByCategory__in=itemsByInstrumentSet)
    # classificationByCategory=ItemClassificationSerializer(many=False, read_only=True)

    class Meta:
        model = Instrument_header
        # fields = ('name', 'description','i18n_code','translations')
        fields = ('version_name', 'is_active', 'start_date', 'end_date', "translations")

def consultActiveInstrument():
    try:
        active_instrument = Instrument_header.objects.filter(is_active=1)[0]
        # active_instrument = None
        #active_instrument = Instrument_header.objects.all().first()
        return active_instrument
    except Exception as e:
        print("ERROR: Excepcion consultando instrument_header , el get no arrojo resultados en el metodo ConsultActiveInstrument")
        return None



class TranslatedInstrumentSerializer(serializers.HyperlinkedModelSerializer):
    instrument_header = InstrumentHeaderSerializer(many=False, read_only=True)
    instrument_header_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = Trans_instrument_header
        #fields = ( 'instrument_header','id', 'general_description', 'feature_description', 'disclaimer', 'user_instructions',
        #'contact_info', 'i18n_code')
        fields = ("__all__")

    """ Prueba sobre como personalizar query sets
    def get_queryset(self):
        print("personalizado query set")
        active_instrument = consultActiveInstrument()
        return Trans_instrument_header.objects.filter(instrument_header=active_instrument).filter(
            i18n_code=LanguageChoice.ES.name)
    """

# Serializar los items x categoria
class SimpleItemClassificationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ItemClassification
        fields = ('id','name','type')

class ItemSimpleSerializer(serializers.HyperlinkedModelSerializer):

    dimension=SimpleItemClassificationSerializer(many=False,read_only=True)
    #category = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
    category = SimpleItemClassificationSerializer(many=False,read_only=True)
    response_format = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
    component=SimpleItemClassificationSerializer(many=False,read_only=True)

    class Meta:
        model = Item
        #fields = ('name', 'description','i18n_code','translations')
        fields = ('id','response_format','item_order', 'dimension','category','component')


# Serializador usado para dibujar el instrumento
class TranslatedItemSerializer(serializers.HyperlinkedModelSerializer):
    item=ItemSimpleSerializer(many=False,read_only=True)
    class Meta:
        model = Trans_item
        fields = ('id','name','item')

class ConfigSurveysByClientsSerializer(serializers.HyperlinkedModelSerializer):
    client_id = serializers.IntegerField(write_only=True)
    instrument_header_id = serializers.IntegerField()
    client=ClientSerializer(read_only=True)
    class Meta:
        model = Config_surveys_by_clients
        fields = ('id','client_id','client',"instrument_header_id","max_surveys","used_surveys","survey_conf_desc")


class CustomizedInstrumentSerializer(serializers.HyperlinkedModelSerializer):
    """
    config_survey = serializers.HyperlinkedRelatedField(
        many=False,
        read_only=True,
        view_name='config_surveys_by_clients-detail'
    ) """
    config_survey = ConfigSurveysByClientsSerializer(many=False, read_only=True)
    prefix = serializers.CharField(max_length=255, write_only=True)
    access_code = serializers.CharField(max_length=255, write_only=True)
    config_survey_id = serializers.IntegerField()
    class Meta:
        model = Customized_instrument
        fields = ('id','config_survey_id','config_survey','custom_user_instructions','custom_contact_info','custom_thanks','prefix','access_code')

class SurveysByClientSerializer(serializers.HyperlinkedModelSerializer):
    config_survey = ConfigSurveysByClientsSerializer(many=False, read_only=False)
    config_survey_id = serializers.IntegerField()
    class Meta:
        model = Surveys_by_client
        fields = ('__all__')

class ItemSerializer(serializers.HyperlinkedModelSerializer):
    #translations=serializers.StringRelatedField(many=True)
    dimension=SimpleItemClassificationSerializer(many=False,read_only=True)
    #category = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
    category = SimpleItemClassificationSerializer(many=False,read_only=True)
    # response_format = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
    component=SimpleItemClassificationSerializer(many=False,read_only=True)

    class Meta:
        model = Item
        #fields = ('name', 'description','i18n_code','translations')
        fields = ('id','response_format','item_order', 'dimension','category','component')

""" Retorna solo los ids de los campso asociados para reducir tiempo de carga"""
class ItemSimpleSerializer(serializers.HyperlinkedModelSerializer):
    dimension_id = serializers.IntegerField()
    category_id = serializers.IntegerField()
    component_id = serializers.IntegerField()

    class Meta:
        model = Item
        #fields = ('name', 'description','i18n_code','translations')
        fields = ('id','dimension_id','category_id','component_id')


class ItemResponByParticipantsSerializer(serializers.HyperlinkedModelSerializer):
    #participant_response_header_id =serializers.IntegerField(write_only=True)
    item = ItemSimpleSerializer(many=False, read_only=True)
    item_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = Items_respon_by_participants
        #fields = ('__all__')
        fields = ('id','item','item_id','answer_numeric')
        #fields = ('id','item','item_id','participant_response_header_id')

class AverageResponsesSerializer(serializers.Serializer):
    item__dimension = serializers.IntegerField(read_only=True)
    item__dimension__name = serializers.CharField()
    average = serializers.FloatField(read_only=True)

class ItemClassificationSerializer(serializers.HyperlinkedModelSerializer):
    #itemsBycategory = serializers.StringRelatedField(many=True)
    # Se serializan los datos aprovechando las relaciones entre los atributos de llavesprimarias y foraneas
    #itemsByCategory = ItemSerializer(many=True,read_only=True)
    #itemsByCategory = ItemSerializer(many=True,read_only=True)

    #itemsByCategory = serializers.SlugRelatedField (queryset=itemsByInstrument,many=True,slug_field='category')
    itemsByCategory = ItemSerializer(many=True,read_only=True)
    itemsByDimension = ItemSerializer(many=True,read_only=True)
    itemsByComponent = ItemSerializer(many=True,read_only=True)

    class Meta:
        model = ItemClassification
        # fields = ('name', 'description','i18n_code','translations')
        fields = ('id','name', 'itemsByCategory','itemsByDimension','itemsByComponent')


# Serializa el historico de un item
class InstrumentStructureHistorySerializerFull(serializers.HyperlinkedModelSerializer):
    #instrument_header = models.ForeignKey(Instrument_header, on_delete=models.CASCADE, related_name="itemsByInstrument")
    original_item = ItemSerializer(many=False,read_only=True)
    new_item = ItemSerializer(many=False,read_only=True)
    previous_item = ItemSerializer(many=False,read_only=True)

    class Meta:
        model = Instrument_structure_history
        fields = ('original_item', 'new_item', 'previous_item', 'item_minor_version', 'change_reason','is_active','start_date')

class InstrumentStructureHistorySerializerOnlyActiveItems(serializers.HyperlinkedModelSerializer):
        # instrument_header = models.ForeignKey(Instrument_header, on_delete=models.CASCADE, related_name="itemsByInstrument")
        new_item = ItemSerializer(many=False, read_only=True)

        class Meta:
            model = Instrument_structure_history
            fields = ('new_item', 'is_active','start_date')

class ParticipantResponseHeaderSerializer(serializers.HyperlinkedModelSerializer):
    # instrument_header=InstrumentHeaderSerializer(many=False,read_only=False)
    # customized_instrument = CustomizedInstrumentSerializer(many=False, read_only=True)
    #survey_by_client = SurveysByClientSerializer(many=False, read_only=True)

    customized_instrument_id = serializers.IntegerField(write_only=True)
    area_id = serializers.IntegerField(write_only=True)
    #survey_by_client_id = serializers.IntegerField(write_only=True)

    #responsesList = serializers.StringRelatedField(many=True)
    responsesList = ItemResponByParticipantsSerializer(many=True)

    """
    customized_instrument = serializers.HyperlinkedRelatedField(
        many=False,
        read_only=True,
        view_name='customized_instrument-detail'
    )


    def to_internal_value(self, data):
        try:
            obj_id = data['id']
        except KeyError:
            raise serializers.ValidationError(
                'id is a required field.'
            )
        except ValueError:
            raise serializers.ValidationError(
                'id must be an integer.'
            )
     """

    class Meta:
        model = Participant_response_header
        # fields = ('__all__')
        #fields = ('id','email','comments','position','area','customized_instrument','customized_instrument_id','responsesList')
        fields = ('id','email','comments','area_id','is_directive','customized_instrument_id','responsesList', 'is_complete')

    def create(self, validated_data):
        print ("Entre al create del responses del instrument")
        responses_list_data = validated_data.pop('responsesList')
        print(validated_data)

        # Se consultan cuando surveys tiene aun disponibles el cliente
        try:
            config_survey = Customized_instrument.objects.get(
                id=validated_data['customized_instrument_id']).config_survey
            if config_survey.used_surveys < config_survey.max_surveys:
                print('Hay espacio')
                participant_response_header=Participant_response_header.objects.create(**validated_data)
                print("Guarde el participant response")
                for response in responses_list_data:
                    Items_respon_by_participants.objects.create(participant_response_header=participant_response_header,
                                                                **response)
                print("Guarde las respuestas de los participantes")
                print(participant_response_header.responsesList)

                print("Se actualiza la configuración del survey para indicar que se guardo una respuesta nueva")
                config_survey.used_surveys= config_survey.used_surveys + 1
                config_survey.save()
                return participant_response_header
            else:
                # Se retorna algun error pq no se puede guardar las respuestas de los participantes
                print("ERROR: No se guardan las respuestas no hay espacio, y el front end no controlo el error ")
                 # Esto genera una excepcion que psoiblemente diga algo de email o algo asi,
                 # a este camino no deberia llegar , por eso voy a dejar q arroje la excepcion
                return  {}
        except:
            return {'error': 'No space'}
            return {}

class LoginByCodeSerializer(serializers.Serializer):

    # Estos campos aqui son super importanes pq si el serializador no viene de un modelo entonces solo va entender lo que este aqui definido.
    access_code = serializers.CharField(max_length=255,write_only=True)
    prefix = serializers.CharField(max_length=255,write_only=True)
    customized_instrument = CustomizedInstrumentSerializer(many=False, read_only=True, required=False)
    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        # The `validate` method is where we make sure that the current
        # instance of `LoginByCodeSerializer` has "valid". In the case of logging a
        # user in, this means validating that they've provided an access_code
        # and prfeix and that this combination matches one of the surveys in
        # our database.
        access_code = data.get('access_code', None)
        prefix = data.get('prefix', None)

        # Raise an exception if an
        # email is not provided.
        if access_code is None:
            raise serializers.ValidationError(
                'El código de acceso es requerido para iniciar la encuesta.'
            )

        # Raise an exception if a
        # password is not provided.
        if prefix is None:
            raise serializers.ValidationError(
                'El prefijo es requerido para iniciar la encuesta'
            )
        try:
            customized_instrument_to_client = Customized_instrument.objects.get(prefix=prefix,
                                                                                    access_code=access_code)

            #Estos datos estaran disponibles en views en el atributo validated_data
            data= {
                'customized_instrument': CustomizedInstrumentSerializer(customized_instrument_to_client, context={'request': None}).data,  #FIXME para retirar las credenciales de acceso
                'token': self._generate_jwt_token(customized_instrument_to_client),
            }
            return data
        except Customized_instrument.DoesNotExist:
            raise serializers.ValidationError(
                'No existe ninguna encuesta para los valores de inicio proporcionados.'
            )

    def _generate_jwt_token(self, customized_instrument):
        """
        Generates a JSON Web Token that stores the customized_instrument_id and has an expiry
        date set to 60 days into the future.
        """
        #dt = datetime.now() + timedelta(days=60)
        # exp_time = datetime.now() + timedelta(days=60)
        now = timegm(datetime.utcnow().utctimetuple())

        future = datetime.now() + timedelta(days=60)
        future_int=timegm(future.timetuple())
        # future_int = timegm(future.timetuple())
        # now_int = timegm(now.timetuple())
        print("future " + str(future))
        print("future number" + str(timegm(future.timetuple())))

        exp_time =  timegm(datetime.utcnow().utctimetuple())
        payload =  {
            'customized_instrument_id': customized_instrument.id,
            'config_survey_id':customized_instrument.config_survey.id,
            'mode': 'byAccessCode', #Indica que la autenticación fue por codigo de acceso
            'exp': future_int
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

        if payload['exp'] < now:
            print("ya expiro")
        else:
            print("no expero")
        return token.decode('utf-8')