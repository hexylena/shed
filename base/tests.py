from django.test import TestCase
from .models import Installable
import os
from .handlers import unpack_tarball, validate_installable_archive
from django.contrib.auth import models


def testData(name):
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'test-data', name)

class HandlerTestCase(TestCase):

    def setUp(self):
        user = models.User(username='3shed5me')
        self.installable = Installable(
            name='cairo',
            synopsis='syn',
            description='desc',
            remote_repository_url='asdf',
            homepage_url='asdffdasfsd',
            repository_type=0,
            owner=user,
        )

    def test_unpacking_tarballs(self):
        tmpdir = unpack_tarball(testData('test.tgz'))
        assert os.listdir(tmpdir) == ['fixtures.json']
        # Cleanup
        os.unlink(os.path.join(tmpdir, 'fixtures.json'))
        os.removedirs(tmpdir)

    def test_invalid_tarball(self):
        with self.assertRaises(AssertionError):
            validate_installable_archive(
                self.installable,
                testData('test.tgz')
            )

    def test_valid_tarball(self):
        tools = validate_installable_archive(
            self.installable,
            testData('seqtk_cutn.tgz')
        )

        self.assertTrue(
            'seqtk_cutN.xml' in tools[0][0]
        )
