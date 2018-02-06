# -----------------------------------------------------------------------------
# Copyright (c) 2014--, The Qiita Development Team.
#
# Distributed under the terms of the BSD 3-clause License.
#
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------

from qiita_client import QiitaTypePlugin, QiitaArtifactType

from .validate import validate

# Define the supported artifact types
artifact_types = [
    QiitaArtifactType('q2_visualization', 'Qiime 2 visualization',
                      False, False, False, [('qzv', True)])]


# The visualization is the summary itself, so we don't need a
# generate_html_summary function. However, the plugins requires to
# register a function for it
def generate_html_summary(qclient, job_id, parameters, out_dir):
    return True, None, ""


# Initialize the plugin
plugin = QiitaTypePlugin('Visualization types', '0.1.0',
                         'Visualization artifacts type plugin',
                         validate, generate_html_summary,
                         artifact_types)
