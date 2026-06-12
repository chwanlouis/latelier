from module.core.tools.settings import app_settings
from module.core.tools.log import logger
from module.core.repository.users import user_repository


async def create_initial_admin():
    username = app_settings.INIT_ADMIN_USERNAME
    password = app_settings.INIT_ADMIN_PASSWORD
    email = app_settings.INIT_ADMIN_EMAIL

    print(f"Reading environment variables and initializing admin")

    try:
        admin = await user_repository.create_admin(
            username=username, password=password, email=email
        )

        if not admin:
            print(f"Creation failed: Username '{username}' already exists in the database.")
            return

        print("\n" + "=" * 50)
        print("Admin account successfully initialized via .env!")
        print("=" * 50 + "\n")
        logger.info(f"Initial Super Admin created successfully via seed script from .env.")

    except Exception as e:
        print(f"Database write failed. Error message: {e}")
        logger.exception(e)
