from django.shortcuts import render

from Apps.encuestador.models import Item
from Apps.encuestador.models import ClassificationChoice
from Apps.encuestador.models import ItemClassification
from Apps.encuestador.models import Item
from Apps.encuestador.models import Instrument_header
from Apps.encuestador.models import Instrument_structure_history
from Apps.encuestador.models import Customized_instrument
from Apps.encuestador.models import Trans_instrument_header
from Apps.encuestador.models import LanguageChoice
from Apps.encuestador.models import Trans_item
from Apps.encuestador.models import Participant_response_header
from Apps.encuestador.models import Company, Client,Config_surveys_by_clients
from Apps.encuestador.models import Response_format
from Apps.encuestador.models import Surveys_by_client
from rest_framework import viewsets
import logging


from Apps.encuestador.serializers import CompanySerializer,ConfigSurveysByClientsSerializer
from Apps.encuestador.serializers import ResponseFormatSerializer
from Apps.encuestador.serializers import ClientSerializer
from Apps.encuestador.serializers import TranslatedInstrumentSerializer
from Apps.encuestador.serializers import TranslatedItemSerializer
from Apps.encuestador.serializers import ItemSerializer
from Apps.encuestador.serializers import SimpleItemClassificationSerializer
from Apps.encuestador.serializers import ItemClassificationSerializer
from Apps.encuestador.serializers import ParticipantResponseHeaderSerializer
from Apps.encuestador.serializers import SurveysByClientSerializer
"""
"""

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from rest_framework.decorators import action


# Create your views here.

"""Endpoint that allows the database objects to be viewed or edited."""

def consultActiveInstrument():
    try:
        active_instrument = Instrument_header.objects.filter(is_active=1)[0]
        # active_instrument = None
        #active_instrument = Instrument_header.objects.all().first()
        return active_instrument
    except Exception as e:
        print("ERROR: Excepcion consultando instrument_header , el get no arrojo resultados en el metodo ConsultActiveInstrument")
        return None

class CustomizedInstrumentViewSet (viewsets.ModelViewSet):
    serializer_class = Customized_instrument
    queryset = Customized_instrument.objects.all()


class CompanyViewSet (viewsets.ModelViewSet):
    serializer_class = CompanySerializer
    queryset = Company.objects.all()

class ClientViewSet (viewsets.ModelViewSet):
    serializer_class = ClientSerializer
    queryset = Client.objects.all()

class ConfigSurveysByClientsViewSet (viewsets.ModelViewSet):
    serializer_class = ConfigSurveysByClientsSerializer
    queryset = Config_surveys_by_clients.objects.all()


class ResponseFormatViewSet(viewsets.ModelViewSet):
    serializer_class = ResponseFormatSerializer
    queryset = Response_format.objects.all()

class InstructionsSpanishViewSet(viewsets.ModelViewSet):
    serializer_class = TranslatedInstrumentSerializer
    active_instrument=consultActiveInstrument()
    queryset = Trans_instrument_header.objects.filter(instrument_header=active_instrument).filter(
            i18n_code=LanguageChoice.ES.name)
    #queryset = Trans_instrument_header.objects.all()

class SpanishActiveItemsViewSet (viewsets.ModelViewSet):
    serializer_class = TranslatedItemSerializer
    # Traigo el instrumento activo
    active_instrument = consultActiveInstrument()
    # Traigo el id de los items asociadas al instrumento activo y que esten activos
    activeItemsId = Instrument_structure_history.objects.filter(instrument_header=active_instrument).filter(
        is_active=True).values('new_item__id')
    #Agregue filtro para facilitar pruebas
    #queryset = Trans_item.objects.filter(item__in=activeItemsId).filter(i18n_code=LanguageChoice.ES.name).filter(item__dimension__id = 7)
    queryset = Trans_item.objects.filter(item__in=activeItemsId).filter(i18n_code=LanguageChoice.ES.name)

class ItemsViewSet(viewsets.ModelViewSet):
    serializer_class = ItemSerializer
    #queryset = Item.objects.all()
    # Traigo el instrumento activo
    active_instrument = consultActiveInstrument()
    # Traigo el id de los items asociadas al instrumento activo y que esten activos
    activeItems = Instrument_structure_history.objects.filter(instrument_header=active_instrument).filter(
        is_active=True).values('new_item__id')
    queryset = Item.objects.filter(id__in=activeItems)

class OnlyActiveItems (viewsets.ModelViewSet):
    serializer_class = ItemSerializer
    # Traigo el instrumento activo
    active_instrument =  consultActiveInstrument()
    print ("Imprimo lo que tiene el instrumento")
    print (active_instrument)
    # Traigo el id de los items asociadas al instrumento activo y que esten activos
    activeItems = Instrument_structure_history.objects.filter(instrument_header=active_instrument).filter(is_active=True).values('new_item__id')
    queryset = Item.objects.filter(id__in=activeItems)


class ParticipantResponseViewSet (viewsets.ModelViewSet):
    serializer_class = ParticipantResponseHeaderSerializer
    queryset = Participant_response_header.objects.all()

    """
    @action(methods=['post'], detail=True)
    def save_participant(self, request, pk=None):
        participant_response_header = self.get_object()
        serializer = ParticipantResponseHeaderSerializer(data=request.data)
        if serializer.is_valid():
            participant_response_header.save()
            return Response({'id': participant_response_header.id})
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
    """

class SurveysByClientViewSet (viewsets.ModelViewSet):
    serializer_class = SurveysByClientSerializer
    queryset = Surveys_by_client.objects.all()


class SimpleActiveCategoriesViewSet(viewsets.ModelViewSet):
    serializer_class = SimpleItemClassificationSerializer
    # Traigo el instrumento activo
    active_instrument = consultActiveInstrument()
    # Traigo el id de los items asociadas al instrumento activo y que esten activos
    categoriesId = Instrument_structure_history.objects.filter(instrument_header=active_instrument).filter(
        is_active=True).values('new_item__category__id').distinct()
    queryset = ItemClassification.objects.filter(id__in=categoriesId)


class SimpleActiveDimensionsViewSet(viewsets.ModelViewSet):
    serializer_class = SimpleItemClassificationSerializer
    # Traigo el instrumento activo
    active_instrument = consultActiveInstrument()
    # Traigo el id de los items asociadas al instrumento activo y que esten activos
    dimensionsId = Instrument_structure_history.objects.filter(instrument_header=active_instrument).filter(
        is_active=True).values('new_item__dimension__id').distinct()
    queryset = ItemClassification.objects.filter(id__in=dimensionsId)

class SimpleActiveComponentsViewSet(viewsets.ModelViewSet):
    serializer_class = SimpleItemClassificationSerializer
    # Traigo el instrumento activo
    active_instrument = consultActiveInstrument()
    # Traigo el id de los items asociadas al instrumento activo y que esten activos
    dimensionsId = Instrument_structure_history.objects.filter(instrument_header=active_instrument).filter(
        is_active=True).values('new_item__component__id').distinct()
    queryset = ItemClassification.objects.filter(id__in=dimensionsId)

# Retorna el Json con los items y sus traducciones agrupados por categoria, el mismo serializar se usa para agrupar por dimension y por componente
"""
class CategoriesViewSet(viewsets.ModelViewSet):
    serializer_class = ItemClassificationSerializer
    queryset = ItemClassification.objects.filter(type=ClassificationChoice.CATEGORY.value)

class DimensionsViewSet(viewsets.ModelViewSet):
    serializer_class = ItemClassificationSerializer
    queryset = ItemClassification.objects.filter(type=ClassificationChoice.DIMENSION.value)

class ComponentsViewSet(viewsets.ModelViewSet):
    serializer_class = ItemClassificationSerializer
    queryset = ItemClassification.objects.filter(type=ClassificationChoice.COMPONENT.value)

    # Traigo el instrumento activo
    active_instrument = consultActiveInstrument()
    # Traigo el id de los items asociadas al instrumento activo y que esten activos
    categoriesId = Instrument_structure_history.objects.filter(instrument_header=active_instrument).filter(
        is_active=True).values('new_item__category__id').distinct()
    queryset = ItemClassification.objects.filter(id__in=categoriesId)

    # Traigo la lista de items asociadas al instrumento activo
    #itemsByInstrumentSet = Instrument_header.objects.filter(itemsByInstrument__new_item_item_order=1).values('itemsByInstrument__new_item')
    #items_by_instrument= Instrument_structure_history.objects.filter(instrument_header=active_instrument).filter(is_active=True).filter(new_item__item_order=2)
    #itemsToShow=Item.objects.filter(id__in=items_by_instrument__new_item)

    #queryset = ItemClassification.objects.filter()

    #Filtro la lista de objectos a pintar de la clasificacion
    #queryset = ItemClassification.objects.filter(itemsByCategory__in=itemsByInstrumentSet).filter(type=ClassificationChoice.CATEGORY.value)

    #queryset = ItemClassification.objects.filter(type=ClassificationChoice.CATEGORY.value)

    # Traigo el id de los items asociadas al instrumento activo
    #itemsByInstrument = Instrument_structure_history.objects.filter(instrument_header=active_instrument).values(
        #'new_item')
    #items = Item.objects.filter(id__in=idItemsByInstrument)
    #queryset = ItemClassification.objects.filter(type=ClassificationChoice.DIMENSION.value).filter(itemsByCategory__in=itemsByInstrument)
    #queryset = ItemClassification.objects.filter(type=ClassificationChoice.DIMENSION.value).distinct()
    """