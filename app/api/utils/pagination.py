"""
Pagination Utilities

Provides reusable pagination functionality for database queries.
"""

from flask import request
from sqlalchemy.orm import Query


def get_pagination_params():
    """
    Extract pagination parameters from request args.
    
    Returns:
        tuple: (page, per_page) with validation
    """
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 50, type=int), 100)  # Max 100 items per page
    
    # Ensure positive values
    page = max(1, page)
    per_page = max(1, per_page)
    
    return page, per_page


def paginate_query(query: Query, page: int = None, per_page: int = None, serialize_func=None):
    """
    Paginate a SQLAlchemy query and return formatted results.
    
    Args:
        query: SQLAlchemy query object
        page: Page number (if None, gets from request)
        per_page: Items per page (if None, gets from request)
        serialize_func: Function to serialize each item (defaults to .to_dict())
        
    Returns:
        dict: Paginated data with items and pagination metadata
    """
    if page is None or per_page is None:
        page, per_page = get_pagination_params()
    
    if serialize_func is None:
        serialize_func = lambda item: item.to_dict()
    
    paginated = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    return {
        'items': [serialize_func(item) for item in paginated.items],
        'pagination': create_pagination_response(paginated)
    }


def create_pagination_response(paginated):
    """
    Create standardized pagination metadata.
    
    Args:
        paginated: Flask-SQLAlchemy Pagination object
        
    Returns:
        dict: Pagination metadata
    """
    return {
        'page': paginated.page,
        'per_page': paginated.per_page,
        'total': paginated.total,
        'pages': paginated.pages,
        'has_prev': paginated.has_prev,
        'has_next': paginated.has_next,
        'prev_num': paginated.prev_num,
        'next_num': paginated.next_num
    }