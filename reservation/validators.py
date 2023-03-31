from django.core.exceptions import ValidationError


def validate_image_size(file):
    """
    Custom validator for property media file size of photos
    :param file:
    :return:
    """
    max_image_size_in_mb = 5
    if file.size > (max_image_size_in_mb * 1024 * 1024):
        raise ValidationError(f'Image size can not be larger than {max_image_size_in_mb} MB')


def validate_video_size(file):
    """
    Custom validator for property media file size of videos
    :param file:
    :return:
    """
    max_video_size_in_mb = 100
    if file.size > (max_video_size_in_mb * 1024 * 1024):
        raise ValidationError(f'Video size can not be larger than {max_video_size_in_mb}')
