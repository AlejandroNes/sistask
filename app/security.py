"""Autenticación local de Flask-AppBuilder mediante correo electrónico."""

import secrets

from flask_appbuilder.security.sqla.manager import SecurityManager


class EmailSecurityManager(SecurityManager):
    def auth_user_db(self, email, password):
        # FAB también acepta nombres de usuario; aquí se exige un correo existente.
        user = self.find_user(email=email.strip()) if email and '@' in email else None
        if not user or user.email.casefold() != email.strip().casefold():
            # Ejecutar la verificación de FAB incluso para usuarios inexistentes.
            return super().auth_user_db('no-existe-' + secrets.token_hex(24), password)
        return super().auth_user_db(user.username, password)
