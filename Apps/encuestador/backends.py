import jwt

from django.conf import settings

from rest_framework import authentication, exceptions

from .models import User, Customized_instrument, Config_surveys_by_clients


class JWTAuthentication(authentication.BaseAuthentication):
    """
    Modificada de https://thinkster.io/tutorials/django-json-api/authentication
    Se configura en el settings de python
    """
    authentication_header_prefix = 'Bearer'

    def authenticate(self, request):
        """
        The `authenticate` method is called on every request regardless of
        whether the endpoint requires authentication.

        `authenticate` has two possible return values:

        1) `None` - We return `None` if we do not wish to authenticate. Usually
                    this means we know authentication will fail. An example of
                    this is when the request does not include a token in the
                    headers.

        2) `(user, token)` - We return a user/token combination when
                             authentication is successful.

                            If neither case is met, that means there's an error
                            and we do not return anything.
                            We simple raise the `AuthenticationFailed`
                            exception and let Django REST Framework
                            handle the rest.
        """
        request.user = None

        # `auth_header` should be an array with two elements: 1) the name of
        # the authentication header (in this case, "Token") and 2) the JWT
        # that we should authenticate against.
        auth_header = authentication.get_authorization_header(request).split()
        auth_header_prefix = self.authentication_header_prefix.lower()

        if not auth_header:
            return None

        if len(auth_header) == 1:
            # Invalid token header. No credentials provided. Do not attempt to
            # authenticate.
            return None

        elif len(auth_header) > 2:
            # Invalid token header. The Token string should not contain spaces. Do
            # not attempt to authenticate.
            return None

        # The JWT library we're using can't handle the `byte` type, which is
        # commonly used by standard libraries in Python 3. To get around this,
        # we simply have to decode `prefix` and `token`. This does not make for
        # clean code, but it is a good decision because we would get an error
        # if we didn't decode these values.
        prefix = auth_header[0].decode('utf-8')
        token = auth_header[1].decode('utf-8')

        if prefix.lower() != auth_header_prefix:
            # The auth header prefix is not what we expected. Do not attempt to
            # authenticate.
            return None

        # By now, we are sure there is a *chance* that authentication will
        # succeed. We delegate the actual credentials authentication to the
        # method below.
        return self._authenticate_credentials(request, token)

    def _authenticate_credentials(self, request, token):
        """
        Try to authenticate the given credentials. If authentication is
        successful, return the user and token. If not, throw an error.
        """
        #try:
        print("token")
        print(token)
        # Logica para controlar si el token expiró
        try:
            payload = jwt.decode(token, settings.SECRET_KEY)
            print("payload")
            print(payload)
        except Exception as e:
            msg = 'Autenticacion incorrecta. La sesión expiró. Autentíquese nuevamente'
            raise exceptions.AuthenticationFailed(msg)


        #Esto se conecta con la parte de la serializacion  en las clases LoginByCodeSerializer y LoginSerializer

        #Se saca toda la informacion que podria llegar en el payload
        customized_instrument_id = payload.get('customized_instrument_id', None)
        config_survey_id = payload.get('config_survey_id', None)

        #Solo para autenticacion via usuario y contraseña
        user_id = payload.get('user_id', None)
        profile_id = payload.get('profile_id', None)

        #Para ambos casos
        mode = payload.get('mode', None)
        exp = payload.get('exp', None)

        #Segun lo que venga en mode se busca la información
        if mode == "byAccessCode":
            try:
                customized_instrument_to_client = Customized_instrument.objects.get(id=customized_instrument_id)
                config_survey = Config_surveys_by_clients.objects.get(id=config_survey_id)
                # Se crea un usuario dummy para usar las funciones de autenticación de django una vez que se esta seguro de
                # que la infomacion que se esperaba se recupero correctamente
                fake_user = User(email="test@test.com")
                request.user = fake_user
                return (fake_user, token)
            except Customized_instrument.DoesNotExist:
                msg = 'Token inválido: Ninguna encuesta personalizado existe con el identificador enviado'
                raise exceptions.AuthenticationFailed(msg)
            except Config_surveys_by_clients.DoesNotExist:
                msg = 'Token inválido: No se encuentra ninguna encuesta personalizada para la empresa'
                raise exceptions.AuthenticationFailed(msg)
        elif mode == "normal":
            """Auteticacion con pasword y contraseña"""
            try:
                user = User.objects.get(pk=payload['id'])
            except User.DoesNotExist:
                msg = 'Token inválido: No se encuentra ningún usuario con ese token'
                raise exceptions.AuthenticationFailed(msg)
            if not user.is_active:
                msg = 'Este usuario fue desactivado.'
                raise exceptions.AuthenticationFailed(msg)
            return (user, token)