from django.contrib.auth.models import User

from .models import Profile


class EmailAuthBackend:
    """
    Authenticate a user based on email address as the username
    """

    def authenticate(self, request, username=None, password=None):
        """
        Authenticate a user based on email address as the user name
        :param request:
        :param username:
        :param password:
        :return:
        """
        try:
            user = User.objects.get(email=username)
            if user.check_password(password):
                return user
            return None
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            return None

    def get_user(self, user_id):
        """
        Get a User object from the user_id
        :param user_id:
        :return:
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


def create_profile(backend, user, *args, **kwargs):
    """
    Create user profile
    :param backend:
    :param user:
    :param args:
    :param kwargs:
    :return:
    """
    if backend.name == 'google-oauth2':
        Profile.objects.get_or_create(user=user)
