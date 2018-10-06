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
from Apps.encuestador.models import Surveys_by_client
from Apps.encuestador.models import LanguageChoice
from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework.response import Response


class CompanySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Company
        #fields = ('company_contact_name','company_email')
        fields = ('__all__')

class ClientSerializer(serializers.HyperlinkedModelSerializer):
    company = CompanySerializer(many=False, read_only=True)
    class Meta:
        model = Client
        #fields = ('max_surveys','used_surveys','contact')
        fields =('__all__')

class ResponseFormatSerializer(serializers.HyperlinkedModelSerializer):
    parametric_table=serializers.PrimaryKeyRelatedField(many=False, read_only=True)
    class Meta:
        model = Response_format
        #fields = ('name', 'description','i18n_code','translations')
        fields = ('name','type','parametric_table')


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
        fields = ('response_format','item_order', 'dimension','category','component')


# Serializador usado para dibujar el instrumento
class TranslatedItemSerializer(serializers.HyperlinkedModelSerializer):
    item=ItemSimpleSerializer(many=False,read_only=True)
    class Meta:
        model = Trans_item
        fields = ('id','name','item')

class ConfigSurveysByClientsSerializer(serializers.HyperlinkedModelSerializer):
    client = ClientSerializer(many=False,read_only=False)
    instrument_header = InstrumentHeaderSerializer(many=False, read_only=False)
    class Meta:
        model = Config_surveys_by_clients
        fields = ('__all__')


class CustomizedInstrumentSerializer(serializers.HyperlinkedModelSerializer):
    """
    config_survey = serializers.HyperlinkedRelatedField(
        many=False,
        read_only=True,
        view_name='config_surveys_by_clients-detail'
    ) """
    config_survey= ConfigSurveysByClientsSerializer (many=False,read_only=False)
    #client = ClientSerializer(many=False,read_only=False)

    class Meta:
        model = Customized_instrument
        fields = ('__all__')
        # fields = ('custom_general_description',)

class SurveysByClientSerializer(serializers.HyperlinkedModelSerializer):
    config_survey = ConfigSurveysByClientsSerializer(many=False, read_only=False)
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

class ItemResponByParticipantsSerializer(serializers.HyperlinkedModelSerializer):
    #participant_response_header_id =serializers.IntegerField(write_only=True)
    item = ItemSerializer(many=False, read_only=True)
    item_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = Items_respon_by_participants
        #fields = ('__all__')
        fields = ('id','item','item_id','answer_numeric')
        #fields = ('id','item','item_id','participant_response_header_id')


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
        fields = ('id','email','comments','position','area','is_directive','customized_instrument_id','responsesList', 'is_complete')

    def create(self, validated_data):
        print ("Entre al create del responses del instrument")
        responses_list_data = validated_data.pop('responsesList')
        print(validated_data)
        participant_response_header = Participant_response_header.objects.create(**validated_data)
        print ("Guarde el participant response")
        for response in responses_list_data:
            Items_respon_by_participants.objects.create(participant_response_header=participant_response_header,**response)
        print ("Guarde las respuestas de los participantes")
        print (participant_response_header.responsesList)
        return participant_response_header