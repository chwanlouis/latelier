# ==============================================================================
# 🚨 CRITICAL INFRASTRUCTURE WARNING: DO NOT REMOVE OR ALTER THESE IMPORTS! 🚨
# ==============================================================================
# These explicit model imports are MANDATORY to prevent runtime race conditions
# and circular dependency failures within SQLAlchemy's global mapper registry.
#
# Why this is required:
# When endpoints or repositories dynamically interact with the 'UserSQLModel',
# SQLAlchemy's relationship configuration eagerly parses foreign keys and
# many-to-many bridges (e.g., 'OrganisationSQLModel', 'PermissionSQLModel').
#
# If these model are not pre-loaded into python memory during application startup,
# SQLAlchemy will fail to resolve relation string tokens, triggering critical
# 500 Internal Server Errors (e.g., "KeyError: 'OrganisationSQLModel'").
#
# Keep this block at the absolute entry-point of the application (main.py).
# ==============================================================================
from module.core.model.sql.user import UserSQLModel
# ==============================================================================
