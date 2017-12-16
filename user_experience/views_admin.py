from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import viewsets
from .models import UserProfileExperience, UserProfileExperienceType
from .permissions import IsAllowedOrSuperuser
from .serializers_admin import UserProfileExperienceAdminSerializer, UserProfileExperienceTypeAdminSerializer



class UserProfileExperienceAdminViewSet(viewsets.ModelViewSet):

    queryset = UserProfileExperience.objects.all()
    serializer_class = UserProfileExperienceAdminSerializer
    permission_classes = (IsAuthenticated,)


class UserProfileExperienceTypeAdminViewSet(viewsets.ModelViewSet):

    queryset = UserProfileExperienceType.objects.all()
    serializer_class = UserProfileExperienceTypeAdminSerializer
    permission_classes = (IsAuthenticated,)