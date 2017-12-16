from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import viewsets
from .models import Institution, InstitutionType
from .permissions import IsAllowedOrSuperuser
from .serializers_admin import InstitutionAdminSerializer, InstitutionTypeAdminSerializer


class InstitutionAdminViewSet(viewsets.ModelViewSet):

    queryset = Institution.objects.all()
    serializer_class = InstitutionAdminSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (SearchFilter,)
    search_fields = ('title',)


class InstitutionTypeAdminViewSet(viewsets.ModelViewSet):

    queryset = InstitutionType.objects.all()
    serializer_class = InstitutionTypeAdminSerializer
    permission_classes = (IsAuthenticated,)