from rest_framework import viewsets, permissions, filters, generics
from .serializer import UserSerializer, GroupSerializer, TagSerializer, InstallableSerializer, RevisionSerializer, SuiteRevisionSerializer, InstallableWithRevisionSerializer
from .models import Tag, Installable, Revision, SuiteRevision
from django.contrib.auth.models import User, Group


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class InstallableList(generics.ListCreateAPIView):
    # class InstallableViewSet(viewsets.ModelViewSet):
    queryset = Installable.objects.all()
    serializer_class = InstallableSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = (filters.DjangoFilterBackend, )
    filter_fields = ('repository_type', )


class InstallableDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Installable.objects.all()
    serializer_class = InstallableWithRevisionSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class RevisionViewSet(viewsets.ModelViewSet):
    queryset = Revision.objects.all()
    serializer_class = RevisionSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class SuiteRevisionViewSet(viewsets.ModelViewSet):
    queryset = SuiteRevision.objects.all()
    serializer_class = SuiteRevisionSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
