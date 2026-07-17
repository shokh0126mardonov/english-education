import os
import logging
from celery import shared_task
from django.utils import timezone
from django.db import transaction

from app.lessons.models import Lesson
from app.common.services.youtube import YouTubeService
from app.common.services.youtube_processing import YoutubeProcessingService

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def upload_lesson_video_to_youtube_task(self, lesson_id: int, schema_name: str) -> None:
    """
    Celery task to upload a lesson video to YouTube.
    Runs video conversion pipeline and handles retries with exponential backoff.
    """
    logger.info(f"Video received. Starting background upload for Lesson ID: {lesson_id} in schema {schema_name}")

    from django_tenants.utils import schema_context

    with schema_context(schema_name):
        try:
            with transaction.atomic():
                try:
                    lesson = Lesson.objects.select_for_update().get(id=lesson_id)
                except Lesson.DoesNotExist:
                    logger.error(f"Lesson ID {lesson_id} not found in schema {schema_name}. Aborting.")
                    return
                
                if not lesson.local_file_path or not os.path.exists(lesson.local_file_path):
                    logger.error(f"Local video file not found at '{lesson.local_file_path}'. Aborting upload.")
                    lesson.upload_status = 'FAILED'
                    lesson.failure_reason = "Local video file missing before upload"
                    lesson.save()
                    return

                lesson.upload_status = 'uploading'
                lesson.save()

            # Perform processing & upload
            processing_service = YoutubeProcessingService()
            processing_service.process_and_upload(lesson, lesson.local_file_path)

            # Triggers background processing check
            if lesson.youtube_video_id:
                check_youtube_processing.delay(lesson.youtube_video_id, schema_name)

        except Exception as e:
            # Retry with exponential backoff: 60s, 120s, 240s
            countdown = 60 * (2 ** self.request.retries)
            logger.warning(
                f"Upload failed for Lesson {lesson_id}: {str(e)}. "
                f"Retrying task in {countdown}s (Attempt {self.request.retries + 1}/3)..."
            )
            try:
                self.retry(exc=e, countdown=countdown)
            except self.MaxRetriesExceededError:
                logger.error(f"YouTube upload failed after maximum retries for Lesson {lesson_id}.")
                with transaction.atomic():
                    try:
                        lesson = Lesson.objects.select_for_update().get(id=lesson_id)
                        lesson.upload_status = 'FAILED'
                        lesson.failure_reason = f"Upload failed: {str(e)}"
                        lesson.save()
                    except Lesson.DoesNotExist:
                        pass


@shared_task
def check_youtube_processing(video_id: str, schema_name: str) -> None:
    """
    Task to periodically check the processing status of a video on YouTube.
    Fires every 30 seconds until status is succeeded or failed.
    """
    logger.info(f"Checking processing status on YouTube for Video ID: {video_id} in schema {schema_name}")

    from django_tenants.utils import schema_context

    with schema_context(schema_name):
        try:
            lesson = Lesson.objects.get(youtube_video_id=video_id)
        except Lesson.DoesNotExist:
            logger.error(f"No lesson found with YouTube Video ID: {video_id}. Aborting checker.")
            return

        # Check status via YouTube Service
        try:
            yt_service = YouTubeService()
            result = yt_service.check_processing_status(video_id)
        except Exception as e:
            logger.error(f"Failed to query YouTube API for video {video_id}: {str(e)}. Retrying status check in 30s...")
            check_youtube_processing.apply_async(args=[video_id, schema_name], countdown=30)
            return

        status = result.get('status')
        
        if status == 'succeeded':
            logger.info(f"Processing completed on YouTube for Video ID: {video_id}. Marking lesson as READY.")
            
            local_path = lesson.local_file_path
            
            with transaction.atomic():
                lesson.upload_status = 'READY'
                lesson.local_file_path = None
                lesson.save()

            # Delete local file only after upload_status == READY
            if local_path and os.path.exists(local_path):
                try:
                    os.remove(local_path)
                    logger.info(f"Local file deleted: {local_path}")
                except Exception as del_err:
                    logger.error(f"Failed to delete local video file {local_path}: {str(del_err)}")

        elif status == 'failed':
            logger.error(f"Processing failed on YouTube for Video ID: {video_id}. Reason: {result.get('failure_reason')}")
            
            with transaction.atomic():
                lesson.upload_status = 'FAILED'
                lesson.failure_reason = result.get('failure_reason')
                lesson.save()

        else:
            # Still processing or transient not found, wait and try again in 30 seconds
            logger.info(f"Waiting for processing: YouTube Video ID {video_id} is still in processing state. Re-scheduling...")
            check_youtube_processing.apply_async(args=[video_id, schema_name], countdown=30)
