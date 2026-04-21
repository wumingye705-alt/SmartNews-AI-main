from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from utils.exception_response import (http_exception_handler,
                                      integrity_error_handler,
                                      sqlalchemy_error_handler,
                                      general_exception_handler)


def register_exception_handlers(app):
    """注册全局异常处理器"""
    app.add_exception_handler(HTTPException, http_exception_handler)  # 使用正确的HTTPException类
    app.add_exception_handler(IntegrityError, integrity_error_handler)  # 处理数据库完整性错误
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_error_handler)  # 处理SQLAlchemy异常
    app.add_exception_handler(Exception, general_exception_handler)  # 处理其他异常