from werkzeug.exceptions import HTTPException


class MediaFileNotFound(HTTPException):
    pass


class MediaThumbnailNotFound(HTTPException):
    pass


class InternalServerError(HTTPException):
    pass


class AuthenticationError(HTTPException):
    pass


class SearchLengthError(HTTPException):
    pass


class VideoSubtitleNotFound(HTTPException):
    pass


errors = {
    'MediaFileNotFound': {
        'message': "Media not found!",
        'status': 404,
    },
    'MediaThumbnailNotFound': {
        'message': "Media Thumbail not found or not exists",
        'status': 404,
    },
    'VideoSubtitleNotFound': {
        'message': "The video subtitle was not found",
        'status': 404,
    },
    'InternalServerError': {
        'message': 'Internal Server Error',
        'status': 500
    },
    'AuthenticationError': {
        'message': 'Authentication Token require!',
        'status': 403
    },
    'SearchLengthError': {
        'message': 'Search string input too short!',
        'status': 403
    }
}
