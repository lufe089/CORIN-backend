from django.shortcuts import render

from Apps.encuestador.models import Item
from Apps.encuestador.models import ClassificationChoice
from Apps.encuestador.models import ItemClassification
from Apps.encuestador.models import Item
from Apps.encuestador.models import Instrument_header
from Apps.encuestador.models import Instrument_structure_history
from Apps.encuestador.models import Items_respon_by_participants
from Apps.encuestador.models import Customized_instrument
from Apps.encuestador.models import Trans_instrument_header
from Apps.encuestador.models import LanguageChoice
from Apps.encuestador.models import Trans_item
from Apps.encuestador.models import Participant_response_header
from Apps.encuestador.models import Company, Client,Config_surveys_by_clients
from Apps.encuestador.models import Response_format
from Apps.encuestador.models import Surveys_by_client
from Apps.encuestador.models import Trans_parametric_table,Parametric_master
from rest_framework import viewsets
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView
from django.db.models import F,Value
from rest_framework.response import Response
import logging


from Apps.encuestador.serializers import CompanySerializer,ConfigSurveysByClientsSerializer
from Apps.encuestador.serializers import ResponseFormatSerializer
from Apps.encuestador.serializers import ClientSerializer
from Apps.encuestador.serializers import TranslatedInstrumentSerializer
from Apps.encuestador.serializers import TranslatedItemSerializer
from Apps.encuestador.serializers import ItemSerializer
from Apps.encuestador.serializers import SimpleItemClassificationSerializer
from Apps.encuestador.serializers import CustomizedInstrumentSerializer
from Apps.encuestador.serializers import ParticipantResponseHeaderSerializer
from Apps.encuestador.serializers import SurveysByClientSerializer
from Apps.encuestador.serializers import AverageResponsesSerializer
from django.db.models import Avg,Count
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

def consultAreas():
    # Nombre dado a la tabla que tiene las áreas
    parameteric_master = Parametric_master.objects.get(name="areas", end_date=None)
    try:
        areas = Trans_parametric_table.objects.filter(parametric_master=parameteric_master, i18n_code="ES").values(
            "i18n_code").annotate(text=F('option_label'), value=F('numeric_value')).order_by('numeric_value')
        return areas

    except Parametric_master.DoesNotExist:
        return False

class CustomizedInstrumentViewSet (viewsets.ModelViewSet):
    serializer_class = CustomizedInstrumentSerializer
    queryset = Customized_instrument.objects.all()


class CompanyViewSet (viewsets.ModelViewSet):
    serializer_class = CompanySerializer
    queryset = Company.objects.all()

class ClientViewSet (viewsets.ModelViewSet):
    serializer_class = ClientSerializer
    queryset = Client.objects.all().order_by('-created_at')
    # queryset = Client.objects.all().order_by('-created_at')

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
    # print ("Imprimo lo que tiene el instrumento")
    # print (active_instrument)
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

class AverageByClassifiers (viewsets.ModelViewSet):
    serializer_class = AverageResponsesSerializer
    #queryset= Items_respon_by_participants.objects.values('item__dimension__name, item__dimension').annotate(average=Avg('answer_numeric')).order_by('-average')

    # Traigo las respuestas del cliente -- OJO EL CLIENTE ahorita esta quemado
    # FIXME
    responseHeadersByCompany = Participant_response_header.objects.filter(customized_instrument__config_survey__client__id=1).values('id')

    #Dimensions
    queryset= Items_respon_by_participants.objects.filter(participant_response_header__id__in =responseHeadersByCompany).values("participant_response_header","item__dimension__name", "item__dimension_id").annotate(average=Avg('answer_numeric')).order_by('-average')


class ResponsesView(APIView):
    @api_view(['GET'])
    def get_areas(request):

        result=consultAreas()
        if(result == False):
            print("INFO: No se encontró configuración para la tabla paramétrica de areas")
            return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(result)

    @api_view(['GET'])
    # @renderer_classes((JSONRenderer,))
    def averageFilters(request, format=None):
        """
        A view that returns the count of active users in JSON.
        """
        # FIXME
        responseHeadersByCompany = Participant_response_header.objects.filter(
            customized_instrument__config_survey__client__id=1).values('id')

        # Dimensions
        dimensions_average = Items_respon_by_participants.objects.filter(
            participant_response_header__id__in=responseHeadersByCompany).values("item__dimension_id").annotate(name=F('item__dimension__name'), idElement=F('item__dimension_id'),average=Avg('answer_numeric'),n=Count('participant_response_header',distinct=True)).order_by('-average')

        # Components
        # Respuestas de la compañía donde el componente no sea null
        components_average = Items_respon_by_participants.objects.filter(participant_response_header__id__in=responseHeadersByCompany).exclude(item__component= None).values(
                                                                                 "item__component_id").annotate(name=F('item__component__name'), idElement=F('item__component_id'),average=Avg('answer_numeric'),n=Count('participant_response_header',distinct=True)).order_by('-average')

        # Categories
        """ Trae los campos sin renombrarlos
        categories_average = Items_respon_by_participants.objects.filter(
            participant_response_header__id__in=responseHeadersByCompany).values("item__category__name","item__category_id").annotate(average=Avg('answer_numeric'),n=Count('participant_response_header',distinct=True)).order_by('-average')
            """
        # Areas por categorias
        list_areas_by_categories_average_todos = []
        ## En vue data.js de la vista están definidas las 5 áreas quemadas sobre las que se trabaja, por ello el ciclo tiene un rage de 1 a 6
        list_average_by_area =[]
        areas = consultAreas()

        # FIXME estos datos son iguales a los que estan en en el front-end pero estan quedamos tal vez toque volverlos una tabla paramétrica
        """
        areas[1]= 'Área de Producción/operaciones'
        areas[2]= 'Área comercial'
        areas[3]= 'Área de tecnología'
        areas[4]= 'Área de gestión humana'
        areas[5]= 'Área de investigación y desarrollo'
        """

        for area in areas:
            print(area)

            print(area['value'])
            areas_by_categories_average = Items_respon_by_participants.objects.filter(
                participant_response_header__id__in=responseHeadersByCompany).filter(
                participant_response_header__area=area['value']).values("item__category_id").annotate(
                area_id=F('participant_response_header__area'), category_name=F('item__category__name'),
                idElement=F('item__category_id'), average=Avg('answer_numeric'),
                n=Count('participant_response_header', distinct=True)).order_by('-average')

            list_areas_by_categories_average_todos.append(
                {'idArea': area['value'], 'name': area['text'], 'averageByCategories': areas_by_categories_average})

            # Promedio por area
            area_average_data = Items_respon_by_participants.objects.filter(
                participant_response_header__id__in=responseHeadersByCompany).filter(participant_response_header__area = area['value']).values(
                "participant_response_header__area").annotate(average=Avg('answer_numeric'),
                n=Count('participant_response_header', distinct=True)).order_by('-average')

            if area_average_data.exists():
                list_average_by_area.append({'average':area_average_data.first()['average'],'n':area_average_data.first()['n'], 'name':area['text']+' (' + str(area_average_data.first()['n'])+ ')'})
            else:
                # list_average_by_area[i]= {'average': 0, 'n':0, 'name':areas[i]}
                list_average_by_area.append({'average': 0, 'n':0, 'name':area['text']+' (0) '})


        print("Lista de listas para las áreas")
        print(list_areas_by_categories_average_todos)



        # Usa el atributo f para renombrar el valor de un campo. Esto lo hago para que en la tabla de la vista todos se llamen igual( catogiras, dimensions,components) y puedan dibujar mas facil. Tiene que tener al menos un campo value para que funcione
        categories_average = Items_respon_by_participants.objects.filter(
            participant_response_header__id__in=responseHeadersByCompany).values("item__category_id").annotate(name=F('item__category__name'), idElement=F('item__category_id'),average=Avg('answer_numeric'),n=Count('participant_response_header',distinct=True)).order_by('-average')
        print ("Categories average")
        print(categories_average)

        categories_average_by_directives= Items_respon_by_participants.objects.filter(
            participant_response_header__id__in=responseHeadersByCompany).filter(participant_response_header__is_directive=1).values("item__category_id").annotate(name=F('item__category__name'), idElement=F('item__category_id'),average=Avg('answer_numeric'),n=Count('participant_response_header',distinct=True) ).order_by('-average')


        # Los comento pq no los use al cambiar por contar con un distinc en el query
        # count_directives = Participant_response_header.objects.filter(id__in=responseHeadersByCompany).filter(is_directive=1).aggregate(Count('is_directive'))
        # count_NO_directives = Participant_response_header.objects.filter(id__in=responseHeadersByCompany).filter(is_directive=0).aggregate(Count('is_directive'))
        # numDirectives= count_directives['is_directive__count']
        # numNoDirectives = count_NO_directives['is_directive__count']

        categories_average_by_no_directives = Items_respon_by_participants.objects.filter(
                participant_response_header__id__in=responseHeadersByCompany).filter(
                participant_response_header__is_directive=0).values("item__category_id").annotate(name=F('item__category__name'), idElement=F('item__category_id'),
                average=Avg('answer_numeric'), n=Count('participant_response_header',distinct=True)).order_by('-average')

        # Overall average
        overall_average_count = Items_respon_by_participants.objects.filter(
            participant_response_header__id__in=responseHeadersByCompany).aggregate(average=Avg('answer_numeric'), n= Count('participant_response_header',distinct=True))

        print (request)
        content = {'overall_average': overall_average_count['average'], 'n': overall_average_count['n'],
                   "average_by_dimensions": dimensions_average, "average_by_components": components_average,
                   "average_by_categories": categories_average,
                   "categories_average_by_directives": categories_average_by_directives,
                   "categories_average_by_no_directives": categories_average_by_no_directives,
                   "categories_average_by_area": list_areas_by_categories_average_todos,
                   "average_by_area": list_average_by_area}
        # return Response(content)
        return Response(content)

    @api_view(['GET'])
    def getClientAndConfiguration(request, format=None):
        """ Trae informacion del cliente y las configuraciones relacionadas con el cliente"""

        # max_survey=Config_surveys_by_clients.objects.filter(client=OuterRef('pk'))),
        clients_with_configuration= Config_surveys_by_clients.objects.all().values('client__id', 'client__client_company_name', 'client__company_id','client__constitution_year', 'client__number_employees',
                  'client__is_corporate_group', 'client__is_family_company',"max_surveys","used_surveys").annotate(config_id=F('id'))
        #clients_without_configuration= Client.objects.all().annotate(max_surveys=Value('0'),used_surveys=Value('0'))

        # Se consultan los id de los que si tienen configuracion para excluirlos de la consulta directa de la tabla de clientes y así hacer que la union no tenga repetidos
        clients_with_configuration_ids = Config_surveys_by_clients.objects.all().values('client__id')

        # Se hace la resta en los campos que se anotan solo como truco para que los valores sean zero pues no encontre como inicializarlos realmente en cero
        clients_without_configuration= Client.objects.exclude(id__in=clients_with_configuration_ids).values('id', 'client_company_name', 'company_id','constitution_year', 'number_employees',
                  'is_corporate_group', 'is_family_company').annotate(max_surveys=Count('id')-Count('id'),used_surveys=Count('id')-Count('id'),config_id=Count('id')-Count('id')).order_by('-updated_at')

        #FIXME - Tratar de agregar los campos que faltan manualmente antes de retornar los datos
        all_clients= clients_without_configuration.union(clients_with_configuration)
        return Response(all_clients)
        # return Response ()

    @api_view(['GET'])
    def getCustomizedInstrument(request):
        """
        Busca cual es para configuracion activa para ese cliente y luego retorna un objeto de Intrumento personalizado
        que tiene prediligenciados los mismos campos que estan por defecto definidos en el instrumento que este activo.
        Con esa información el cliente puede personalizar la información y luego guardar la información en la base de datos.
        :param idClient:
        :return:
        """
        try:
            idClient = request.GET['idClient']
            # Encuentra el cliente asociado a esa configuracion
            config_surveys_by_client = Config_surveys_by_clients.objects.get(client_id=idClient)
            print(config_surveys_by_client)
            customized_instrument_to_client =  Customized_instrument()
            # Busca si hay una personalización para el cliente
            try:
                customized_instrument_to_client= Customized_instrument.objects.get(config_survey=config_surveys_by_client)
                # Si existe se retorna directamente
                serializer= CustomizedInstrumentSerializer(customized_instrument_to_client,context={'request': request})
                return Response(serializer.data)
            except Customized_instrument.DoesNotExist:
                # Se consultan los textos asociados al instrument header
                try:
                    # Fixme por ahora se hace que el idioma que se consulte sea directamente español
                    trans_instrument_header=Trans_instrument_header.objects.get(instrument_header=config_surveys_by_client.instrument_header, i18n_code="ES")
                    # Se le asocia a este objeto la configuracion del survey
                    customized_instrument_to_client.config_survey=config_surveys_by_client
                    customized_instrument_to_client.user_instructions= trans_instrument_header.user_instructions
                    customized_instrument_to_client.contact_info  = trans_instrument_header.contact_info
                    customized_instrument_to_client.thanks = trans_instrument_header.thanks
                    response={'config_survey_id': customized_instrument_to_client.config_survey.id,
                     'custom_user_instructions': customized_instrument_to_client.user_instructions,
                     'custom_contact_info': customized_instrument_to_client.contact_info,
                     'custom_thanks': customized_instrument_to_client.thanks, 'prefix':'C'+idClient}
                    print(response)
                    return Response(response,status = status.HTTP_200_OK)
                   # return Response( CustomizedInstrumentSerializer(customized_instrument_to_client,context={'request': request}).data,status = status.HTTP_200_OK)
                except Trans_instrument_header.DoesNotExist:
                    print("Error no se encontro una traduccion para el instrumento que se consulta")
        except Config_surveys_by_clients.DoesNotExist:
            print("INFO: No se encontró configuración para el cliente enviado")
            return Response(status=status.HTTP_404_NOT_FOUND)

    @api_view(['POST'])
    def getParticipantResponsesToDownload(request):
        print(request)
        idCompany= request.POST['idCompany']

        # Todos los ids de los clientes asociados a la compania
        ids_clients= Client.objects.filter(company__id=idCompany).values("id")

        print(ids_clients)
        # Consultar las respuestas
        all_responses_by_participants = Items_respon_by_participants.objects.filter(
                participant_response_header__customized_instrument__config_survey__client__id__in=ids_clients).values(
                "answer_numeric").annotate(participante_id=F('participant_response_header__id'), is_directive=F('participant_response_header__is_directive'),
                                                                       area=F('participant_response_header__area'),
                                                                       client_id=F('participant_response_header__customized_instrument__config_survey__client__id'),
                                                                       pregunta_id=F('item__id')).order_by('item__id','participant_response_header__id')
        return Response(all_responses_by_participants)


    """ Lo comento pq al fin no sirve0
    @api_view(['GET'])
    # @renderer_classes((JSONRenderer,))
    def getItemsByCategorySpanish(request, format=None):
        # Traigo el instrumento activo
        active_instrument = consultActiveInstrument()
        # Traigo el id de los items asociadas al instrumento activo y que esten activos
        activeItemsId = Instrument_structure_history.objects.filter(instrument_header=active_instrument).filter(
            is_active=True).values('new_item__id')
        queryset = Trans_item.objects.filter(item__in=activeItemsId).filter(i18n_code=LanguageChoice.ES.name)

        # Traigo el instrumento activo
        active_instrument = consultActiveInstrument()
        # Traigo el id de los items asociadas al instrumento activo y que esten activos
        categoriesId = Instrument_structure_history.objects.filter(instrument_header=active_instrument).filter(
            is_active=True).values('new_item__category__id').distinct()
        queryset = ItemClassification.objects.filter(id__in=categoriesId).order_by('-name')

    """



class SimpleActiveCategoriesViewSet(viewsets.ModelViewSet):
    serializer_class = SimpleItemClassificationSerializer
    # Traigo el instrumento activo
    active_instrument = consultActiveInstrument()
    # Traigo el id de los items asociadas al instrumento activo y que esten activos
    categoriesId = Instrument_structure_history.objects.filter(instrument_header=active_instrument).filter(
        is_active=True).values('new_item__category__id').distinct()
    queryset = ItemClassification.objects.filter(id__in=categoriesId).order_by('-name')


class SimpleActiveDimensionsViewSet(viewsets.ModelViewSet):
    serializer_class = SimpleItemClassificationSerializer
    # Traigo el instrumento activo
    active_instrument = consultActiveInstrument()
    # Traigo el id de los items asociadas al instrumento activo y que esten activos
    dimensionsId = Instrument_structure_history.objects.filter(instrument_header=active_instrument).filter(
        is_active=True).values('new_item__dimension__id').distinct()
    queryset = ItemClassification.objects.filter(id__in=dimensionsId).order_by('-name')

class SimpleActiveComponentsViewSet(viewsets.ModelViewSet):
    serializer_class = SimpleItemClassificationSerializer
    # Traigo el instrumento activo
    active_instrument = consultActiveInstrument()
    # Traigo el id de los items asociadas al instrumento activo y que esten activos
    dimensionsId = Instrument_structure_history.objects.filter(instrument_header=active_instrument).filter(
        is_active=True).values('new_item__component__id').distinct()
    # El menos en el order by significa que es descendiente
    queryset = ItemClassification.objects.filter(id__in=dimensionsId).order_by('-name')

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