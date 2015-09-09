from rest_framework import viewsets
from .serializer import TagSerializer, InstallableSerializer, RevisionSerializer, SuiteRevisionSerializer
from .models import Tag, Installable, Revision, SuiteRevision


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class InstallableViewSet(viewsets.ModelViewSet):
    queryset = Installable.objects.all()
    serializer_class = InstallableSerializer


class RevisionViewSet(viewsets.ModelViewSet):
    queryset = Revision.objects.all()
    serializer_class = RevisionSerializer


class SuiteRevisionViewSet(viewsets.ModelViewSet):
    queryset = SuiteRevision.objects.all()
    serializer_class = SuiteRevisionSerializer
