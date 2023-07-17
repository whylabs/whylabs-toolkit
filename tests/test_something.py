import os
import logging

logger = logging.getLogger(__name__)

ORG_ID = os.environ["ORG_ID"]

def test_dummy() -> None:
    logger.info(ORG_ID)
    assert ORG_ID == "org-fjx9Rz"