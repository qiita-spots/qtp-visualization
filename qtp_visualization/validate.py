# -----------------------------------------------------------------------------
# Copyright (c) 2014--, The Qiita Development Team.
#
# Distributed under the terms of the BSD 3-clause License.
#
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------

from json import loads
from os.path import join, basename

from qiime2 import Visualization
from qiita_client import ArtifactInfo

Q2_INDEX = """<!DOCTYPE html>
<html>
  <body>
    <iframe src="./support_files/%s" width="100%%" height="850" frameborder=0>
    </iframe>
  </body>
</html>"""


def _validate_q2_visualization(files, out_dir):
    # Magic number 0 -> there is only 1 qzv file
    qzv_fp = files['qzv'][0]
    # If the loader files this is not a correct Qiime 2 visualization. There
    # is no common exception raised, so we catch all of them
    try:
        q2vis = Visualization.load(qzv_fp)
    except Exception as e:
        return False, None, "Error loading Qiime 2 visualization: %s" % e

    # The visualization in Qiime 2 can contain multiple files and directories.
    # Adding all of them to Qiita can generate a very polluted GUI. In order
    # to improve that, we create a directory where all the files are added
    # (including the original index file) and we create a new index file with
    # an iframe that points to the old index file. This way, we are only adding
    # one HTML file and one directory to the Qiita filepaths.
    html_dir = join(out_dir, 'support_files')
    html_fp = join(out_dir, 'index.html')

    # Extract all the visualization files in the support_files.
    q2vis.export_data(html_dir)

    # Find the index paths. Only HTML based visualizations are currently
    # supported, since everything that we are doing is web based. Not sure
    # if there is any other type of visualizaion in Qiime 2 at this point, but
    # checking here will show a useful error in case that this occurs.
    index_paths = q2vis.get_index_paths()
    if 'html' not in index_paths:
        return (False, None,
                "Only Qiime 2 visualization with an html index are supported")

    index_name = basename(index_paths['html'])
    with open(html_fp, 'w') as f:
        f.write(Q2_INDEX % index_name)

    # We add the original qzv file so users can download it and play with it
    filepaths = [(qzv_fp, 'qzv'), (html_fp, 'html_summary'),
                 (html_dir, 'html_summary_dir')]

    return True, [ArtifactInfo(None, 'q2_visualization', filepaths)], ""


def validate(qclient, job_id, parameters, out_dir):
    """Validates a new artifact

    Parameters
    ----------
    qclient : qiita_client.QiitaClient
        The Qiita server client
    job_id : str
        The job id
    parameters : dict
        The parameter values to validate and create the artifact
    out_dir : str
        The path to the job's output directory

    Returns
    -------
    bool, list of qiita_client.ArtifactInfo , str
        Whether the job is successful
        The artifact information, if successful
        The error message, if not successful
    """
    files = loads(parameters['files'])
    a_type = parameters['artifact_type']

    validators = {'q2_visualization': _validate_q2_visualization}

    # Check if the validate is of a type that we support
    if a_type not in validators:
        return (False, None, "Unknown artifact type %s. Supported types: %s"
                             % (a_type, ", ".join(sorted(validators))))

    # Validate the specific type
    success, ainfo, error_msg = validators[a_type](files, out_dir)

    return success, ainfo, error_msg
