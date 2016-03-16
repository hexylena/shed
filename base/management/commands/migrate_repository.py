from django.core.management.base import BaseCommand, CommandError
from base.models import Installable, Version
import tempfile
import subprocess
import requests

class Command(BaseCommand):
    help = 'Migrates a TS1.0 repository'

    def add_arguments(self, parser):
        parser.add_argument('shed_url')
        parser.add_argument('repo_id')

    def handle(self, *args, **options):
        # Fetch repo metadata
        # data = self.fetchForId(options['shed_url'], options['repo_id'])
        # repo = self.clone_repo(options['shed_url'], data['owner'], data['name'])
        repo = '/tmp/tmp8UZUyN/'
        for (revno, changeset_id) in self.get_changesets(repo):
            print revno, changeset_id


    def fetchForId(self, url, repo_id):
        return requests.get(url + '/api/repositories/' + repo_id).json()

    def get_changesets(self, repo_dir):
        out = subprocess.check_output([
            'hg', 'log', repo_dir
        ])
        out = [x.strip('changeset:').strip().split(':') for x in out.split('\n') if x.startswith('changeset:')]
        return out[::-1]

    def clone_repo(self, shed_url, owner, name):
        # Make a tempdir
        repo_dir = tempfile.mkdtemp()
        subprocess.check_call([
            'hg', 'clone',
            '/'.join((shed_url, 'repos', owner, name)),
            repo_dir
        ])
        return repo_dir
        print repo_dir

    # Clone this repository: hg clone https://toolshed.g2.bx.psu.edu/repos/devteam/bwa
    # https://toolshed.g2.bx.psu.edu/api/repositories/9ff2d127cd7ed6bc
