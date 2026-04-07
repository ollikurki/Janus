from flask import render_template, request
from app import db
import logging


def register_error_handlers(app):
    """Register custom error handlers with the app."""
    
    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 Bad Request errors."""
        app.logger.warning(f'400 Bad Request: {request.url} - {error}')
        return render_template('400.html'), 400
    
    @app.errorhandler(403)
    def forbidden(error):
        """Handle 403 Forbidden errors."""
        app.logger.warning(f'403 Forbidden: {request.url} - {error}')
        return render_template('403.html'), 403
    
    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 Not Found errors."""
        return render_template('404.html'), 404
    
    @app.errorhandler(422)
    def unprocessable_entity(error):
        """Handle 422 Unprocessable Entity errors."""
        app.logger.warning(f'422 Unprocessable: {request.url} - {error}')
        return render_template('422.html'), 422
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 Internal Server errors."""
        app.logger.error(f'500 Internal Error: {request.url} - {error}')
        db.session.rollback()
        return render_template('500.html'), 500
