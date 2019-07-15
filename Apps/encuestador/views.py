from django.db.models import Avg,Count
from django.db.models import F
from django.conf import settings
from rest_framework import viewsets
from rest_framework.views import APIView
import jwt
from Apps.encuestador.models import ClassificationChoice
from Apps.encuestador.models import Company, Client,Config_surveys_by_clients
from Apps.encuestador.models import Customized_instrument
from Apps.encuestador.models import Instrument_header
from Apps.encuestador.models import Instrument_structure_history
from Apps.encuestador.models import Item
from Apps.encuestador.models import ItemClassification
from Apps.encuestador.models import Items_respon_by_participants
from Apps.encuestador.models import LanguageChoice
from Apps.encuestador.models import Participant_response_header
from Apps.encuestador.models import Response_format
from Apps.encuestador.models import Surveys_by_client
from Apps.encuestador.models import User
from Apps.encuestador.models import Trans_instrument_header
from Apps.encuestador.models import Trans_item
from Apps.encuestador.models import Trans_parametric_table,Parametric_master
from Apps.encuestador.serializers import AverageResponsesSerializer
from Apps.encuestador.serializers import ClientSerializer
from Apps.encuestador.serializers import CompanySerializer,ConfigSurveysByClientsSerializer
from Apps.encuestador.serializers import CustomizedInstrumentSerializer
from Apps.encuestador.serializers import ItemSerializer
from Apps.encuestador.serializers import ParticipantResponseHeaderSerializer
from Apps.encuestador.serializers import ResponseFormatSerializer
from Apps.encuestador.serializers import SimpleItemClassificationSerializer
from Apps.encuestador.serializers import SurveysByClientSerializer
from Apps.encuestador.serializers import TranslatedItemSerializer
from Apps.encuestador.serializers import TranslatedInstrumentSerializer
from Apps.encuestador.serializers import LoginByCodeSerializer
from Apps.encuestador.serializers import LoginByPwdSerializer
from Apps.encuestador.serializers import UserSerializer

"""
"""

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import AllowAny
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
           "id", "i18n_code").annotate(text=F('option_label'), value=F('id')).order_by('numeric_value')
        return areas

    except Parametric_master.DoesNotExist:
        return False

class CustomizedInstrumentViewSet (viewsets.ModelViewSet):
    # list, create, retrieve, update, partial update and destroy
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

    @action(detail=False, methods=['post'])
    def by_company(self, request):
        idCompany = request.data.get("idCompany", None)

        isAdmin = request.data.get('isAdmin', False)
        configuredSurveys = []

        if (idCompany == None and isAdmin):
            # Se retornan todos las configuraciones que se encuentren
            configuredSurveys = Config_surveys_by_clients.objects.all()
        elif (idCompany != None):
            # Consultar todos los ids de clientes asociados a una compañia
            configuredSurveys = Config_surveys_by_clients.objects.filter(client__company__id=idCompany)
        # Como serializar los datos para poderlos retornar en el request
        serializer = ConfigSurveysByClientsSerializer(configuredSurveys, many=True)
        print("VIEW ConfigSurveysByClientsViewSet byCompany: isAdmin, idCompany " , serializer.data , isAdmin, idCompany)
        return Response(serializer.data)


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


class UsersViewSet (viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    """ Personalizado con la info que estaba disponible en https://www.django-rest-framework.org/api-guide/viewsets/#marking-extra-actions-for-routing"""

    @action(detail=False, methods=['post'])
    def users_by_company(self,request):
        idCompany = request.data.get("idCompany", None)

        isAdmin = request.data.get('isAdmin', False)
        users = []
        print("view  users_by_company idCompany  isAdmin", idCompany, isAdmin)

        if (idCompany == None and isAdmin):
            # Se retornan todos los usuarios
            users = User.objects.all()
        elif (idCompany != None):
            # Consultar todos los ids de clientes asociados a una compañia
            users = User.objects.filter(company__id=idCompany)
        # Como serializar los datos para poderlos retornar en el request
        serializer = UserSerializer(users, many=True)
        print(serializer.data)
        return Response(serializer.data)


    def update(self, request,  pk=None):
        # Este metodo se debe sobrescribir para que se acepten actualizaciones parciales
        serializer_data = self.request.data

        # Here is that serialize, validate, save pattern we talked about
        # before.
        print("UsersViewSet update:", serializer_data)
        # Esto podría lanzar una exception pero no la manejo pq si pasa necesito que falle en la vista
        user = User.objects.get(id=pk)
        # Se tiene que pasar el instance para que el metodo save sepa que es un update y no un create
        serializer = UserSerializer(instance=user, data=serializer_data)
        serializer.is_valid(raise_exception=True)
        # Tengo que pasar los datos de la instancia recibidos al serializador para que haga update y no create
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


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
    def get_active_items(self):

        # Traigo el instrumento activo
        active_instrument = consultActiveInstrument()
        # Traigo el id de los items asociadas al instrumento activo y que esten activos
        activeItemsId = Instrument_structure_history.objects.filter(instrument_header=active_instrument).filter(
            is_active=True).values('new_item__id')
        queryset = Trans_item.objects.filter(item__in=activeItemsId).values().filter(i18n_code=LanguageChoice.ES.name)


    @api_view(['POST'])
    # @renderer_classes((JSONRenderer,))
    def averageFilters(request, format=None):
        """
        A view that returns the count of active users in JSON.
        """
        idClient = request.data['idClient']

        # FIXME
        responseHeadersByCompany = Participant_response_header.objects.filter(
            customized_instrument__config_survey__client__id=idClient).values('id')

        # Dimensions
        dimensions_average = Items_respon_by_participants.objects.filter(
            participant_response_header__id__in=responseHeadersByCompany).values("item__dimension_id").annotate(
            name=F('item__dimension__name'), category=F('item__category__name'), idElement=F('item__dimension_id'),
            average=Avg('answer_numeric'), n=Count('participant_response_header', distinct=True)).order_by('item__category__name','-average')

        # Components
        # Respuestas de la compañía donde el componente no sea null
        components_average = Items_respon_by_participants.objects.filter(participant_response_header__id__in=responseHeadersByCompany).exclude(item__component= None).values(
                                                                                 "item__component_id").annotate(name=F('item__component__name'), idElement=F('item__component_id'),average=Avg('answer_numeric'),n=Count('participant_response_header',distinct=True)).order_by('-average')

        # Categories
        """ Trae los campos sin renombrarlos
        categories_average = Items_respon_by_participants.objects.filter(
            participant_response_header__id__in=responseHeadersByCompany).values("item__category__name","item__category_id").annotate(average=Avg('answer_numeric'),n=Count('participant_response_header',distinct=True)).order_by('-average')
            """

        ###### Areas por categorias
        list_areas_by_categories_average_todos = []
        ## En vue data.js de la vista están definidas las 5 áreas quemadas sobre las que se trabaja, por ello el ciclo tiene un rage de 1 a 6
        list_average_by_area =[]
        areas = consultAreas()

        for area in areas:
            #El id de aqu es el id de la tabla parametrica
            areas_by_categories_average = Items_respon_by_participants.objects.filter(
                participant_response_header__id__in=responseHeadersByCompany).filter(
                participant_response_header__area=area['id']).values("item__category_id").annotate(
                area=F('participant_response_header__area__option_label'), category_name=F('item__category__name'),
                average=Avg('answer_numeric'),
                n=Count('participant_response_header', distinct=True)).order_by('item__category__name')

            # Se construye un objecto que tendra para cada area los promedios ponderados
            row = {}
            if areas_by_categories_average.exists():
                row['area'] = area['text'] +' (' + str(areas_by_categories_average.first()['n'])+ ')'
                for result in areas_by_categories_average:
                    row[result['category_name']] = round(result['average'],2)
            else:
                row['area'] = area['text'] + ' ( 0 )'
            list_areas_by_categories_average_todos.append(row)

            # Promedio por area
            area_average_data = Items_respon_by_participants.objects.filter(
                participant_response_header__id__in=responseHeadersByCompany).filter(participant_response_header__area = area['id']).values(
                "participant_response_header__area").annotate(average=Avg('answer_numeric'),
                n=Count('participant_response_header', distinct=True)).order_by('-average')

            if area_average_data.exists():
                list_average_by_area.append({'average':area_average_data.first()['average'],'n':area_average_data.first()['n'], 'name':area['text']+' (' + str(area_average_data.first()['n'])+ ')'})
            else:
                # list_average_by_area[i]= {'average': 0, 'n':0, 'name':areas[i]}
                list_average_by_area.append({'average': 0, 'n':0, 'name':area['text']+' (0) '})

        # Usa el atributo f para renombrar el valor de un campo. Esto lo hago para que en la tabla de la vista todos se llamen igual( catogiras, dimensions,components) y puedan dibujar mas facil. Tiene que tener al menos un campo value para que funcione
        categories_average = Items_respon_by_participants.objects.filter(
            participant_response_header__id__in=responseHeadersByCompany).values("item__category_id").annotate(name=F('item__category__name'), idElement=F('item__category_id'),average=Avg('answer_numeric'),n=Count('participant_response_header',distinct=True)).order_by('name')

        categories_average_by_directives= Items_respon_by_participants.objects.filter(
            participant_response_header__id__in=responseHeadersByCompany).filter(participant_response_header__is_directive=1).values("item__category_id").annotate(name=F('item__category__name'), idElement=F('item__category_id'),average=Avg('answer_numeric'),n=Count('participant_response_header',distinct=True)).order_by('item__category__name')

        categories_labels = ItemClassification.objects.filter(type=ClassificationChoice.CATEGORY.value).values('name').annotate(key=F('name')).order_by('name')
        print("Category labeles")
        print(categories_labels)
        """ category_names_list=[]
        for category_name in categories_labels:
            category_names_list.append(category_name['name'])"""

        # Los comento pq no los use al cambiar por contar con un distinc en el query
        # count_directives = Participant_response_header.objects.filter(id__in=responseHeadersByCompany).filter(is_directive=1).aggregate(Count('is_directive'))
        # count_NO_directives = Participant_response_header.objects.filter(id__in=responseHeadersByCompany).filter(is_directive=0).aggregate(Count('is_directive'))
        # numDirectives= count_directives['is_directive__count']
        # numNoDirectives = count_NO_directives['is_directive__count']

        categories_average_by_no_directives = Items_respon_by_participants.objects.filter(
                participant_response_header__id__in=responseHeadersByCompany).filter(
                participant_response_header__is_directive=0).values("item__category_id").annotate(name=F('item__category__name'), idElement=F('item__category_id'),
                average=Avg('answer_numeric'), n=Count('participant_response_header',distinct=True)).order_by('item__category__name')
        # Overall average
        overall_average_count = Items_respon_by_participants.objects.filter(
            participant_response_header__id__in=responseHeadersByCompany).aggregate(average=Avg('answer_numeric'), n= Count('participant_response_header',distinct=True))

        # Construccion de los promedios por categorias, dimensiones y componentes anidados
        level_one_list = []
        print ("VIEW ResponsesView method: averageFilters  .. construyendo nested table")
        print("VIEW ResponsesView method: averageFilters categories average ..")
        print (categories_average)
        for average_category in categories_average:
            level_one = {'id':average_category['idElement'], 'name': average_category['name'], 'average': average_category['average'], 'n':average_category['n'],  'level': 1}
            print("VIEW ResponsesView Category " + str(level_one))
            dimensions_by_category_average = Items_respon_by_participants.objects.filter(
                participant_response_header__id__in=responseHeadersByCompany)\
                .filter(item__category__id = average_category['idElement'])\
                .values("item__dimension_id").annotate(
                name=F('item__dimension__name'), category=F('item__category__name'), idElement=F('item__dimension_id'),
                average=Avg('answer_numeric'), n=Count('participant_response_header', distinct=True)).order_by(
                'item__category__name', '-average')
            # print("VIEW ResponsesView dimensions by category" + str(dimensions_by_category_average))

            # Se crean objetos del nivel 2 de anidamiento que corresponden a las dimensiones para luego buscar los componentes
            # relacionados con estas dimensiones
            level_two_list =[]
            for average_dimension in dimensions_by_category_average:
                level_two = {'id': average_dimension['idElement'], 'name': average_dimension['name'], 'level': 2,
                         'average': average_dimension['average'], 'n': average_dimension['n']}
                print("VIEW ResponsesView dimension " + str(average_dimension))
                components_by_dimension_average = Items_respon_by_participants.objects.\
                    filter(participant_response_header__id__in=responseHeadersByCompany)\
                    .filter(item__dimension__id=average_dimension['idElement']) \
                    .exclude(item__component=None) \
                    .values("item__component_id")\
                    .annotate(name=F('item__component__name'), idElement=F('item__component_id'),average=Avg('answer_numeric'),n=Count('participant_response_header',distinct=True))\
                    .order_by('-average')
                print("VIEW componets by dimensions")
                # Lista de componentes que conforman la dimension
                level_two['items'] = components_by_dimension_average

                #Se adiciona el elemento de nivel 2 a la lista completa de nivel 2
                level_two_list.append(level_two)
                print("VIEW ResponsesView components by dimension" + str(components_by_dimension_average))

            # Se completa el objeto de nivel uno con la lista que resulta del nivel 2
            level_one['items'] = level_two_list

            #Se agrega el objeto de nivel uno a la lista de nivel 1
            level_one_list.append(level_one)

        print("VIEW ResponsesView lista anidada")
        print(level_one_list)

        # print (request)
        content = {'overall_average': overall_average_count['average'], 'n': overall_average_count['n'],
                   "average_by_dimensions": dimensions_average, "average_by_components": components_average,
                   "average_by_categories": categories_average,
                   "categories_average_by_directives": categories_average_by_directives,
                   "categories_average_by_no_directives": categories_average_by_no_directives,
                   "categories_average_by_area": list_areas_by_categories_average_todos,
                   "average_by_area": list_average_by_area,
                   "category_names":categories_labels,
                   'nested_average': level_one_list }
        # return Response(content)
        return Response(content)

    @api_view(['POST'])
    def getClientAndConfiguration(request, format=None):
        """ Trae informacion del cliente y las configuraciones relacionadas con el cliente"""

        #idCompany = request.data['idCompany']
        idCompany = request.data.get("idCompany", None)

        isAdmin = request.data.get('isAdmin', False)
        isCompany = request.data.get('isCompany', False)
        ids_clients = []

        print("view  getClientAndConfiguration idCompany  isAdmin  is Company;", idCompany, isAdmin, isCompany)
        if isAdmin or isCompany:
            if idCompany == None:
                # Se consultan todos los clientes sin filtro pq esto solo lo puede hacer el usuario admin
                print("VIEW getClientAndConfiguration consulto clientes para todas las compañias ")
                ids_clients = Client.objects.values("id")
            else:
                # Consultar todos los ids de clientes asociados a una compañia
                print ("VIEW getClientAndConfiguration consulto clientes para una compañia con id ", idCompany)
                ids_clients = Client.objects.filter(company__id=idCompany).values("id")

        print (" VIEW getClientAndConfiguration ids_clients", str(ids_clients))
        # max_survey=Config_surveys_by_clients.objects.filter(client=OuterRef('pk'))),
        # Los ultimos dos campos los agregue para que se puedan mostrar facilmente en una lista desplegable, pues esas listas esperan el id con el campo value y el texto con el campo text
        clients_with_configuration= Config_surveys_by_clients.objects.all().filter(client__id__in=ids_clients).values('client__id', 'client__client_company_name', 'client__identification', 'client__company_id','client__company__name','client__constitution_year', 'client__number_employees',
                  'client__is_corporate_group', 'client__is_family_company',"max_surveys","used_surveys").annotate(config_id=F('id'),text=F('client__client_company_name'), value=F('client__id'))
        #clients_without_configuration= Client.objects.all().annotate(max_surveys=Value('0'),used_surveys=Value('0'))

        # Se consultan los id de los que si tienen configuracion para excluirlos de la consulta directa de la tabla de clientes y así hacer que la union no tenga repetidos
        clients_with_configuration_ids = Config_surveys_by_clients.objects.all().values('client__id')

        # Se hace la resta en los campos que se anotan solo como truco para que los valores sean zero pues no encontre como inicializarlos realmente en cero
        clients_without_configuration= Client.objects.exclude(id__in=clients_with_configuration_ids).filter(id__in=ids_clients).values('id', 'client_company_name', 'identification', 'company_id','company__name','constitution_year', 'number_employees',
                  'is_corporate_group', 'is_family_company').annotate(max_surveys=Count('id')-Count('id'),used_surveys=Count('id')-Count('id'),config_id=Count('id')-Count('id'), text=F('client_company_name'),value=F('id')).order_by('-updated_at')

        #FIXME - Tratar de agregar los campos que faltan manualmente antes de retornar los datos
        all_clients= clients_without_configuration.union(clients_with_configuration)
        print("Clients and config survey ", all_clients)
        return Response(all_clients)
        # return Response ()

    @api_view(['POST'])
    def getCustomizedInstrument(request):
        """
        Busca cual es para configuracion activa para ese cliente y luego retorna un objeto de Intrumento personalizado
        que tiene prediligenciados los mismos campos que estan por defecto definidos en el instrumento que este activo.
        Con esa información el cliente puede personalizar la información y luego guardar la información en la base de datos.
        :param idClient:
        :return:
        """
        try:
            idClient = request.data['idClient']
            # Encuentra el cliente asociado a esa configuracion
            config_surveys_by_client = Config_surveys_by_clients.objects.get(client_id=idClient)
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
                     'custom_thanks': customized_instrument_to_client.thanks, 'prefix':'C'+str(idClient),
                     'error': 'no_customized_instrument'}
                    print(response)
                    return Response(response,status = status.HTTP_200_OK)
                   # return Response( CustomizedInstrumentSerializer(customized_instrument_to_client,context={'request': request}).data,status = status.HTTP_200_OK)
                except Trans_instrument_header.DoesNotExist:
                    print("Error no se encontro una traduccion para el instrumento que se consulta")
        except Config_surveys_by_clients.DoesNotExist:
            error= "INFO: No se encontró configuración para el cliente enviado"
            print(error)
            response = {'error': 'config_survey'}
            return Response(response,status=status.HTTP_200_OK)

    @api_view(['POST'])
    def getParticipantResponsesToDownload(request):

        # Si no llega ese parametro pone None en su campo
        idClient = request.data.get("idClient", None)
        idCompany = request.data.get("idCompany", None)
        isClient = request.data.get("isClient", None)

        ids_clients = []
        print ("getParticipantResponsesToDownload  idClient and idCompany", str(idClient), str(idCompany), str(request.data))

        if idClient == None and idCompany != None and isClient!= True:
            # Esta fncionalidad por ahroa estara sin uso.
            # Si no se recibe cliente pero si compañia se consultan todos los clientes asociados a la compañia
            ids_clients= Client.objects.filter(company__id=idCompany).values("id")
        elif idClient != None:
            # La lista de id de clientes solo tendria el id del cliente que se recibe
            ids_clients = [idClient]

        print("getParticipantResponsesToDownload ... ids_clients", ids_clients)
        # Consultar las respuestas
        all_responses_by_participants = Items_respon_by_participants.objects.filter(
                participant_response_header__customized_instrument__config_survey__client__id__in=ids_clients).values(
                    "answer_numeric").annotate(participant_id=F('participant_response_header__id'), is_directive=F('participant_response_header__is_directive'),
                                                                       area= F('participant_response_header__area__option_label'),
                                                                       participant_email= F('participant_response_header__email'),
                                                                       client_id=F('participant_response_header__customized_instrument__config_survey__client__id'),
                                                                       client_name=F('participant_response_header__customized_instrument__config_survey__client__client_company_name'),
                                                                       pregunta_id=F('item__id')).order_by('item__id','participant_response_header__id')

        print ("VIEW getParticipantResponsesToDownload  responses" + str(all_responses_by_participants))
        return Response(all_responses_by_participants)

    @api_view(['POST'])
    def isAllowedSaveResponses(request):
        idCustomizedInstrument = request.data['idCustomizedInstrument']
        config_survey = Customized_instrument.objects.get(
            id=idCustomizedInstrument).config_survey
        if config_survey.used_surveys < config_survey.max_surveys:
            response = {'save': True}
        else:
            response = {'save': False}
        return Response(response,status=status.HTTP_200_OK)

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

""" *************************REGISTRO & LOGIN & AUTENTICACION***************************************"""

class LoginAPIView(APIView):
    permission_classes = (AllowAny,)
    #renderer_classes = (UserJSONRenderer,)

    """
        Esta vista controla las peticiones de autenticacion cuando se hace por código de acceso y prefijo
    """

    @api_view(['POST'])
    def by_code(request):
        """ Este codigo se ejecuta solo cuando se reciben peticiones POST"""

        requestData = {}
        serializer_context = {
            'request': request,
        }
        requestData['access_code'] = request.data['access_code']
        requestData['prefix'] = request.data['prefix']
        # Notice here that we do not call `serializer.save()` like we did for
        # the registration endpoint. This is because we don't  have
        # anything to save. Instead, the `validate` method on our serializer
        # handles everything we need.

        serializer = LoginByCodeSerializer(data=requestData,context=serializer_context)
        serializer.is_valid(raise_exception=True) # Retorna error de tipo 400
        # Responde con los datos que ya incluye el token de autenticación que fue agregado x el serializador
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

    @api_view(['POST'])
    def by_pwd(request):
        requestData = {}
        serializer_context = {
            'request': request,
        }
        requestData['email'] = request.data['email']
        requestData['password'] = request.data['password']

        serializer = LoginByPwdSerializer(data=requestData)
        serializer.is_valid(raise_exception=True)

        # El usuario que se retorna se serializa para poderlo retornar
        serializer = UserSerializer(serializer.validated_data, many=False)
        print("LOGINVIEW: Authenticated user to return " + str(serializer.data))
        return Response(serializer.data, status=status.HTTP_200_OK)


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