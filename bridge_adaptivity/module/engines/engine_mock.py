import logging
import random

from django.db.models import Count

from module.engines.interface import EngineInterface

log = logging.getLogger(__name__)


class EngineMock(EngineInterface):
    """Mock adaptive engine which is used by default if no other engines were added."""

    @staticmethod
    def _get_s_activities_list(sequence):
        """
        Create list with the activities ids which should be excluded from the selection.

        :param sequence: sequence
        :return: list of ids
        """
        s_activities_ids = []
        s_activities_list = list(
            sequence.items.values('activity_id', 'activity__repetition').
            order_by('activity_id').
            annotate(repeated=Count('activity_id')).
            values('activity_id', 'repeated', 'activity__repetition')
        )
        s_activities_ids.extend(
            item['activity_id']
            for item in s_activities_list
            if item['activity__repetition'] <= item['repeated']
        )

        return s_activities_ids

    def select_activity(self, sequence):
        """
        Mock engine provides random choice for the activity from the collection on the Bridge.

        :param sequence: sequence
        :return: selected activity source_launch_url
        """
        s_activities_list = self._get_s_activities_list(sequence)

        available_activities = sequence.collection_order.collection.activities.exclude(id__in=s_activities_list)
        pre_assesment = available_activities.filter(atype='A')
        generic = available_activities.filter(atype='G')
        post_assessment = available_activities.filter(atype='Z')
        chosen_activity_url = None
        if pre_assesment:
            chosen_activity_url = pre_assesment.first().source_launch_url
        elif generic:
            chosen_activity_url = random.choice(generic).source_launch_url
        elif post_assessment:
            chosen_activity_url = post_assessment.first().source_launch_url
        log.debug(f"Chosen activity is: {chosen_activity_url}")
        return {'source_launch_url': chosen_activity_url} if chosen_activity_url else {'complete': True}

    def sync_collection_activities(self, collection):
        """Mock engine works with data stored on the Bridge and do not need to implement method."""
        log.debug(
            f"The Collection {collection.name} was successfully synchronized with the Mock Engine."
        )

        return True

    def submit_activity_answer(self, sequence_item):
        """Mock engine works with data stored on the Bridge and do not need to implement method."""
        log.debug(
            f"Student has submitted answer for the activity {sequence_item.activity.name} and got {sequence_item.score} scores."
        )

        return True
