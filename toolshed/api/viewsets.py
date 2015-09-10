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
    """UserViewSet, show all users, do not allow any changes as that's handled in auth.

    TODO: allow user to update a bio? Or similar?
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (ReadOnly,)


class GroupViewSet(viewsets.ModelViewSet):
    """GroupViewSet shows groups. Authenticated users may create groups

    TODO: permissions on editing existing groups.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class TagListViewSet(generics.ListCreateAPIView):
    """TagListViewSet shows tags. Anyone may create or edit existing tags. Yay
    Community.
    """
    queryset = Tag.objects.all()
    serializer_class = TagListSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    pagination_class = LargeResultsSetPagination


class TagDetailViewSet(generics.RetrieveUpdateDestroyAPIView):
    """TagListViewSet shows tags in detail (i.e. including repos)
    """
    queryset = Tag.objects.all()
    serializer_class = TagDetailSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    pagination_class = LargeResultsSetPagination


class InstallableList(generics.ListCreateAPIView):
    """List installables.

    Seperate class as the List view doesn't need full revision/dependency
    details, just a quick overview.
    """
    queryset = Installable.objects.all()
    serializer_class = InstallableSerializer
    # Logged in users can POST to create new installables
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, )
    filter_fields = ('repository_type', )
    search_fields = ('name', 'synopsis', 'description', 'tags__display_name',
                     'tags__description')


class InstallableDetail(generics.RetrieveUpdateDestroyAPIView):
    """Detail Installables.

    Seperate class as the Detail view needs to know the complete dependency
    tree, and revision history.

    Only users attached directly to an installable, or via a linking group may
    edit a particular installable.
    """
    queryset = Installable.objects.all()
    serializer_class = InstallableWithRevisionSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          InstallableAttachedOrReadOnly)


class RevisionViewSet(viewsets.ModelViewSet):
    """Detail/List views of Revisions

    Only users attached directly to the parent installable, or via a linking
    group may create revisions
    """
    queryset = Revision.objects.all()
    serializer_class = RevisionSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          InstallableAttachedOrReadOnly,
                          RevisionPostOnly)


class SuiteRevisionViewSet(viewsets.ModelViewSet):
    """Detail/List views of Revisions
    """
    queryset = SuiteRevision.objects.all()
    serializer_class = SuiteRevisionSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          InstallableAttachedOrReadOnly)
