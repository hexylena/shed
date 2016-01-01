import os
from .models import Installable, Version
from .handlers import unpack_tarball, ToolHandler, ToolContext
from django.test import TestCase
from django.contrib.auth import models
from django.utils import timezone


def testData(name):
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'test-data', name)

class HandlerTestCase(TestCase):

    def setUp(self):
        user = models.User(username='3shed5me')
        user.save()
        self.installable = Installable(
            name='cairo',
            synopsis='syn',
            description='desc',
            remote_repository_url='asdf',
            homepage_url='asdffdasfsd',
            repository_type=0,
            owner=user,
        )
        self.installable.save()
        prev = Version(
            version='0.1.0',
            commit_message='Some message',
            uploaded=timezone.now(),
            installable=self.installable,
            tar_gz_sha256='deadbeef',
            tar_gz_sig_available=False,
            replacement_version=None,
        )
        prev.save()
        self.th = ToolHandler(self.installable)

    def test_unpacking_tarballs(self):
        tmpdir = unpack_tarball(testData('test.tgz'))
        assert os.listdir(tmpdir) == ['fixtures.json']
        # Cleanup
        os.unlink(os.path.join(tmpdir, 'fixtures.json'))
        os.removedirs(tmpdir)

    def test_invalid_tarball(self):
        with self.assertRaises(AssertionError):
            self.th.validate_archive(
                testData('test.tgz')
            )

    def test_valid_tarball(self):
        tool = self.th.validate_archive(
            testData('seqtk_cutn.tgz')
        )

        self.assertTrue(
            'seqtk_cutN.xml' in tool[0]
        )

    def test_duplicate_version(self):
        tool = self.th.validate_archive(
            testData('seqtk_cutn.tgz')
        )
        with ToolContext(tool[0]) as tool_root:
            assert len(self.installable.version_set.all()) == 1
            v1 = self.th.generate_version_from_tool(tool_root)
            # Should have two versions listed now
            assert len(self.installable.version_set.all()) == 2

            with self.assertRaises(Exception):
                v2 = self.th.generate_version_from_tool(tool_root)

            assert len(self.installable.version_set.all()) == 2
