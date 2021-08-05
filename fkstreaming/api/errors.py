from werkzeug.exceptions import HTTPException


class MediaFileNotFound(HTTPException):
	pass

class MediaThumbnailNotFound(HTTPException):
	pass

class InternalServerError(HTTPException):
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
    'InternalServerError': {
    	'message': 'Internal Server Error',
    	'status': 500
    }
}