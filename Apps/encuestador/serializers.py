from Apps.encuestador.models import ItemClassification
from Apps.encuestador.models import Item
from Apps.encuestador.models import Instrument_header
from Apps.encuestador.models import Response_format
from Apps.encuestador.models import Trans_item
from Apps.encuestador.models import Company
from Apps.encuestador.models import Client
from Apps.encuestador.models import Participant_response_header
from Apps.encuestador.models import Trans_instrument_header
from Apps.encuestador.models import Instrument_structure_history
from Apps.encuestador.models import Surveys_by_client
from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework.response import Response


class CompanySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Company
        #fields = ('name', 'description','i18n_code','translations')
        fields = ('company_contact_name')

class ClientSerializer(serializers.HyperlinkedModelSerializer):
    company = CompanySerializer(many=False, read_only=True)
    class Meta:
        model = Client
        #fields = ('name', 'description','i18n_code','translations')
        fields = ('company','max_surveys','used_surveys','contact')

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


class TranslatedInstrumentSerializer(serializers.HyperlinkedModelSerializer):
    instrument_header = InstrumentHeaderSerializer(many=False, read_only=True)
    class Meta:
        model = Trans_instrument_header
        fields = ( 'instrument_header','id', 'general_description', 'feature_description', 'disclaimer', 'user_instructions',
        'contact_info', 'i18n_code')


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

class ParticipantResponseHeaderSerializer(serializers.HyperlinkedModelSerializer):
    instrument_header=InstrumentHeaderSerializer(many=False,read_only=False)
    class Meta:
        model = Participant_response_header
        #fields = ('name', 'description','i18n_code','translations')
        fields = ('id','instrument_header','participant_name','email','last_update','is_complete','comments')

class SurveysByClientSerializer(serializers.HyperlinkedModelSerializer):
    # client=ClientSerializer (many=False, read_only=True)
    class Meta:
        model = Surveys_by_client
        #fields = ('name', 'description','i18n_code','translations')
        fields = ('participant_response_header','acces_code')


class ItemSerializer(serializers.HyperlinkedModelSerializer):
    translations=serializers.StringRelatedField(many=True)
    dimension=SimpleItemClassificationSerializer(many=False,read_only=True)
    #category = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
    category = SimpleItemClassificationSerializer(many=False,read_only=True)
    response_format = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
    component=SimpleItemClassificationSerializer(many=False,read_only=True)

    class Meta:
        model = Item
        #fields = ('name', 'description','i18n_code','translations')
        fields = ('id','response_format','item_order', 'dimension','category','component','translations')

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
        #fields = ('id','name', 'itemsByCategory','itemsByDimension','itemsByComponent')
        fields = ('id','name', 'itemsByCategory')


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