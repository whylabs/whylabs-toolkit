import logging

from whylabs_toolkit.helpers.models import update_model_metadata

logger = logging.getLogger(__name__)

logging.basicConfig()
logger.setLevel(logging.DEBUG)


def test_update_model_time_period():
    # TODO make test pass
    update_model_metadata(dataset_id="model-7", org_id="org-fjx9Rz", time_period="P1M")


def test_update_model_type():
    # TODO make test pass
    pass
