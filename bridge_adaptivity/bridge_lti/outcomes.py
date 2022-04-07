import logging

from lti import OutcomeRequest

log = logging.getLogger(__name__)


def update_lms_grades(request=None, sequence=None):
    """Send grade update to LMS (LTI Tool)."""
    outcome_request = OutcomeRequest().from_post_request(request) if request else OutcomeRequest()

    outcome_service = sequence.outcome_service
    if outcome_service is None:
        log.info(f"Sequence: {sequence} doesn't contain an outcome service, grade is not sent.")
        return
    consumer = outcome_service.lms_lti_connection

    outcome_request.consumer_key = consumer.consumer_key
    outcome_request.consumer_secret = consumer.consumer_secret
    outcome_request.lis_outcome_service_url = outcome_service.lis_outcome_service_url
    outcome_request.lis_result_sourcedid = sequence.lis_result_sourcedid

    log.debug(
        f"Update LMS grades. Used sequence = {sequence} is completed = {sequence.completed}, grading_policy = {sequence.collection_order.grading_policy}"
    )


    score = sequence.collection_order.grading_policy.calculate_grade(sequence)
    outcome_request.post_replace_result(score)
    lms_response = outcome_request.outcome_response
    user_id = sequence.lti_user
    if lms_response.is_success():
        log.info(
            f"Successfully sent updated grade to LMS. Student:{user_id}, grade:{score}, comment: success"
        )

    elif lms_response.is_processing():
        log.info(
            f"Grade update is being processed by LMS. Student:{user_id}, grade:{score}, comment: processing"
        )

    elif lms_response.has_warning():
        log.warning(
            f"Grade update response has warnings. Student:{user_id}, grade:{score}, comment: warning"
        )

    else:
        log.error(
            f"Grade update request failed. Student:{user_id}, grade:{score}, comment:{lms_response.code_major}"
        )
