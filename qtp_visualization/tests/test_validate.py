# -----------------------------------------------------------------------------
# Copyright (c) 2014--, The Qiita Development Team.
#
# Distributed under the terms of the BSD 3-clause License.
#
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------

from unittest import main
from tempfile import mkdtemp
from os.path import exists, isdir, join, dirname
from os import remove
from shutil import rmtree
from functools import partial
from json import dumps
from time import sleep

from qiita_client.testing import PluginTestCase
from qiita_client import ArtifactInfo

from qtp_visualization.validate import _validate_q2_visualization, validate


class ValidateTests(PluginTestCase):
    def setUp(self):
        self.out_dir = mkdtemp()
        self._clean_up_files = [self.out_dir]

        path_builder = partial(join, dirname(__file__), 'test_data')
        self.valid_qzv = path_builder('good_vis.qzv')
        self.invalid_qzv = path_builder('bad_vis.qzv')

        # Debugging
        sleep(5)

    def tearDown(self):
        for fp in self._clean_up_files:
            if exists(fp):
                if isdir(fp):
                    rmtree(fp)
                else:
                    remove(fp)

    def test_validate_q2_visualization(self):
        # Valid qzv
        obs_succes, obs_ainfo, obs_error = _validate_q2_visualization(
            {'qzv': [self.valid_qzv]}, self.out_dir)
        self.assertEqual(obs_error, "")
        self.assertTrue(obs_succes)
        exp_files = [(self.valid_qzv, 'qzv'),
                     (join(self.out_dir, 'index.html'), 'html_summary'),
                     (join(self.out_dir, 'support_files'), 'html_summary_dir')]
        exp_ainfo = [ArtifactInfo(None, 'q2_visualization', exp_files)]
        self.assertEqual(obs_ainfo, exp_ainfo)

        # Invalid qzv
        obs_succes, obs_ainfo, obs_error = _validate_q2_visualization(
            {'qzv': [self.invalid_qzv]}, self.out_dir)
        self.assertIn("Error loading Qiime 2 visualization:", obs_error)
        self.assertFalse(obs_succes)
        self.assertIsNone(obs_ainfo)

    def _create_job(self, atype, files):
        parameters = {'template': None,
                      'files': dumps(files),
                      'artifact_type': atype,
                      'analysis': 1}
        data = {'command': dumps(['Visualization types', '0.1.0', 'Validate']),
                'parameters': dumps(parameters), 'status': 'running'}
        job_id = self.qclient.post(
            '/apitest/processing_job/', data=data)['job']
        return job_id, parameters

    def test_validate(self):
        # Type not supported
        job_id, params = self._create_job('NotAType',
                                          {'qzv': [self.valid_qzv]})
        obs_succes, obs_ainfo, obs_error = validate(
            self.qclient, job_id, params, self.out_dir)
        self.assertEqual(obs_error, "Unknown artifact type NotAType. "
                                    "Supported types: q2_visualization")
        self.assertFalse(obs_succes)
        self.assertIsNone(obs_ainfo)

        # q2_visualization success
        job_id, params = self._create_job('q2_visualization',
                                          {'qzv': [self.valid_qzv]})
        obs_succes, obs_ainfo, obs_error = validate(
            self.qclient, job_id, params, self.out_dir)
        self.assertEqual(obs_error, "")
        self.assertTrue(obs_succes)
        exp_files = [(self.valid_qzv, 'qzv'),
                     (join(self.out_dir, 'index.html'), 'html_summary'),
                     (join(self.out_dir, 'support_files'), 'html_summary_dir')]
        exp_ainfo = [ArtifactInfo(None, 'q2_visualization', exp_files)]
        self.assertEqual(obs_ainfo, exp_ainfo)


if __name__ == '__main__':
    main()
