from rest_framework import viewsets, permissions, filters, generics
from .serializer import \
    UserSerializer, \
    GroupSerializer, \
    TagDetailSerializer, \
    TagListSerializer, \
    InstallableSerializer, \
    RevisionSerializer, \
    SuiteRevisionSerializer, \
    InstallableWithRevisionSerializer
from .models import Tag, Installable, Revision, SuiteRevision
from django.contrib.auth.models import User, Group
from .permissions import InstallableAttachedOrReadOnly, RevisionPostOnly, ReadOnly
from .pagination import LargeResultsSetPagination


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (ReadOnly,)


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class TagListViewSet(generics.ListCreateAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagListSerializer
    permission_classes = (ReadOnly, )
    pagination_class = LargeResultsSetPagination


class TagDetailViewSet(generics.RetrieveUpdateDestroyAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagDetailSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    pagination_class = LargeResultsSetPagination


class InstallableList(generics.ListCreateAPIView):
    # class InstallableViewSet(viewsets.ModelViewSet):
    queryset = Installable.objects.all()
    serializer_class = InstallableSerializer
    # Logged in users can POST to create new installables
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, )
    filter_fields = ('repository_type', )
    search_fields = ('name', 'synopsis', 'description', 'tags__display_name',
                     'tags__description')


class InstallableDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Installable.objects.all()
    serializer_class = InstallableWithRevisionSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          InstallableAttachedOrReadOnly)


class RevisionViewSet(viewsets.ModelViewSet):
    queryset = Revision.objects.all()
    serializer_class = RevisionSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          InstallableAttachedOrReadOnly,
                          RevisionPostOnly)


class SuiteRevisionViewSet(viewsets.ModelViewSet):
    queryset = SuiteRevision.objects.all()
    serializer_class = SuiteRevisionSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
