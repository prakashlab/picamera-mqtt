import logging
import os

logging.getLogger(__name__).addHandler(logging.NullHandler())

package_path = os.path.dirname(os.path.abspath(__file__))
repo_path = os.path.dirname(package_path)
data_path = os.path.join(repo_path, 'data')
deploy_path = os.path.join(repo_path, 'deploy')
