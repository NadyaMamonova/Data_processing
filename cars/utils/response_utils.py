from rest_framework.response import Response
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def create_json_response(data=None, status=200, message="Success", metadata=None):
    """
    Формирует стандартизированный JSON-ответ

    Args:
        data: Основные данные ответа
        status: HTTP статус код
        message: Сообщение для пользователя
        metadata: Дополнительные метаданные

    Returns:
        Response: Стандартизированный DRF Response
    """
    try:
        response_data = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "status": status,
                "message": message,
                "service": "Car Statistics API",
                "version": "1.0",
                **(metadata or {})
            },
            "data": data
        }

        # Логирование успешного формирования ответа
        logger.info(f"Response created with status {status}")

        return Response(response_data, status=status)

    except Exception as e:
        logger.error(f"Error creating response: {str(e)}")
        return Response({
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "status": 500,
                "message": "Internal server error",
                "error": str(e)
            },
            "data": None
        }, status=500)