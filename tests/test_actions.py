import pytest
from actions import ActionRequestInfo
from rasa_core.trackers import DialogueStateTracker
from rasa_core.slots import TextSlot
from rasa_core.events import SlotSet


def test_ActionRequestInfo():
    ''' Retrives information from CMS given a keyword which maps to an
    endpoint to retrieve that information.

    Parameters
    ----------
    - keyword: (string) keyword which maps to the appropriate endpoint

    Returns
    ----------
    - json: (json) file containing requested information.
    '''
    assert type(ActionRequestInfo.run()) == dict
