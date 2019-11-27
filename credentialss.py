import io
import json

import six

from google.auth import _helpers
from google.auth import credentials
from google.auth import exceptions
from google.oauth2 import _client


# The Google OAuth 2.0 token endpoint. Used for authorized user credentials.
_GOOGLE_OAUTH2_TOKEN_ENDPOINT = 'https://oauth2.googleapis.com/token'


class Credentials(credentials.ReadOnlyScoped, credentials.Credentials):
    """Credentials using OAuth 2.0 access and refresh tokens."""

    def __init__(self, token, refresh_token=None, id_token=None,
                 token_uri=None, client_id=None, client_secret=None,
                 scopes=None):
        """
        Args:
            token (Optional(str)): The OAuth 2.0 access token. Can be None
                if refresh information is provided.
            refresh_token (str): The OAuth 2.0 refresh token. If specified,
                credentials can be refreshed.
            id_token (str): The Open ID Connect ID Token.
            token_uri (str): The OAuth 2.0 authorization server's token
                endpoint URI. Must be specified for refresh, can be left as
                None if the token can not be refreshed.
            client_id (str): The OAuth 2.0 client ID. Must be specified for
                refresh, can be left as None if the token can not be refreshed.
            client_secret(str): The OAuth 2.0 client secret. Must be specified
                for refresh, can be left as None if the token can not be
                refreshed.
            scopes (Sequence[str]): The scopes that were originally used
                to obtain authorization. This is a purely informative parameter
                that can be used by :meth:`has_scopes`. OAuth 2.0 credentials
                can not request additional scopes after authorization.
        """
        super(Credentials, self).__init__()
        self.token = token
        self._refresh_token = refresh_token
        self._id_token = id_token
        self._scopes = scopes
        self._token_uri = token_uri
        self._client_id = client_id
        self._client_secret = client_secret

    @property
    def refresh_token(self):
        """Optional[str]: The OAuth 2.0 refresh token."""
        return self._refresh_token

    @property
    def token_uri(self):
        """Optional[str]: The OAuth 2.0 authorization server's token endpoint
        URI."""
        return self._token_uri

    @property
    def id_token(self):
        """Optional[str]: The Open ID Connect ID Token.
        Depending on the authorization server and the scopes requested, this
        may be populated when credentials are obtained and updated when
        :meth:`refresh` is called. This token is a JWT. It can be verified
        and decoded using :func:`google.oauth2.id_token.verify_oauth2_token`.
        """
        return self._id_token

    @property
    def client_id(self):
        """Optional[str]: The OAuth 2.0 client ID."""
        return self._client_id

    @property
    def client_secret(self):
        """Optional[str]: The OAuth 2.0 client secret."""
        return self._client_secret

    @property
    def requires_scopes(self):
        """False: OAuth 2.0 credentials have their scopes set when
        the initial token is requested and can not be changed."""
        return False

    @_helpers.copy_docstring(credentials.Credentials)
    def refresh(self, request):
        if (self._refresh_token is None or
                self._token_uri is None or
                self._client_id is None or
                self._client_secret is None):
            raise exceptions.RefreshError(
                'The credentials do not contain the necessary fields need to '
                'refresh the access token. You must specify refresh_token, '
                'token_uri, client_id, and client_secret.')

        access_token, refresh_token, expiry, grant_response = (
            _client.refresh_grant(
                request, self._token_uri, self._refresh_token, self._client_id,
                self._client_secret))

        self.token = access_token
        self.expiry = expiry
        self._refresh_token = refresh_token
        self._id_token = grant_response.get('id_token')

    @classmethod
    def from_authorized_user_info(cls, info, scopes=None):
        """Creates a Credentials instance from parsed authorized user info.
        Args:
            info (Mapping[str, str]): The authorized user info in Google
                format.
            scopes (Sequence[str]): Optional list of scopes to include in the
                credentials.
        Returns:
            google.oauth2.credentials.Credentials: The constructed
                credentials.
        Raises:
            ValueError: If the info is not in the expected format.
        """
        keys_needed = set(('refresh_token', 'client_id', 'client_secret'))
        missing = keys_needed.difference(six.iterkeys(info))

        if missing:
            raise ValueError(
                'Authorized user info was not in the expected format, missing '
                'fields {}.'.format(', '.join(missing)))

        return Credentials(
            None,  # No access token, must be refreshed.
            refresh_token=info['refresh_token'],
            token_uri=_GOOGLE_OAUTH2_TOKEN_ENDPOINT,
            scopes=scopes,
            client_id=info['client_id'],
            client_secret=info['client_secret'])

    @classmethod
    def from_authorized_user_file(cls, filename, scopes=None):
        """Creates a Credentials instance from an authorized user json file.
        Args:
            filename (str): The path to the authorized user json file.
            scopes (Sequence[str]): Optional list of scopes to include in the
                credentials.
        Returns:
            google.oauth2.credentials.Credentials: The constructed
                credentials.
        Raises:
            ValueError: If the file is not in the expected format.
        """
        with io.open(filename, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
            return cls.from_authorized_user_info(data, scopes)
