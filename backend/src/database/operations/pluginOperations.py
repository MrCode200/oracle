from backend.src.database import engine, Plugin
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from logging import getLogger
from typing import Type

logger = getLogger("oracle.app")

Session = sessionmaker(bind=engine)

def create_plugin(profile_id: int, plugin_name: str, plugin_settings: dict) -> Plugin | None:
    """
    Creates a new plugin for the profile in the database.

    :param profile_id: The ID of the profile.
    :param plugin_name: The name of the plugin.
    :param plugin_settings: The settings of the plugin.

    :return: The newly created Plugin object.
    """
    session = Session()

    try:
        new_plugin = Plugin(
            profile_id=profile_id,
            plugin_name=plugin_name,
            plugin_settings=plugin_settings
        )
        session.add(new_plugin)
        session.commit()

        logger.info(f"Plugin {plugin_name} created successfully for profile {profile_id}.")
        return new_plugin

    except IntegrityError as e:
        logger.error(f"Error creating plugin {plugin_name}: {e}", exc_info=True)
        session.rollback()
        return None

    finally:
        session.close()


def get_plugin(plugin_id: int = None, profile_id: int = None, plugin_name: str = None) -> Plugin | list[Type[Plugin]] | None:
    """
    Retrieves a plugin from the database by ID, profile ID, or name.

    :param plugin_id: The ID of the plugin.
    :param profile_id: The ID of the profile.
    :param plugin_name: The name of the plugin.

    :return: The Plugin object or None if not found.
    """
    session = Session()

    try:
        if plugin_id is not None:
            return session.get(Plugin, plugin_id)
        elif profile_id is not None:
            return session.query(Plugin).filter_by(profile_id=profile_id).all()
        elif plugin_name is not None:
            return session.query(Plugin).filter_by(plugin_name=plugin_name).first()
        else:
            return session.query(Plugin).all()

    except Exception as e:
        logger.error(f"Error retrieving plugin: {e}", exc_info=True)
        return None

    finally:
        session.close()


def update_plugin(plugin_id: int, plugin_name: str = None, plugin_settings: dict = None) -> bool:
    """
    Updates a plugin in the database.

    :param plugin_id: The ID of the plugin to update.
    :param plugin_name: The new plugin name (optional).
    :param plugin_settings: The new plugin settings (optional).

    :return: True if the plugin was updated successfully, False otherwise.
    """
    session = Session()

    try:
        plugin = session.get(Plugin, plugin_id)
        if not plugin:
            logger.warning(f"Plugin with ID {plugin_id} not found.")
            return False

        if plugin_name:
            plugin.plugin_name = plugin_name
        if plugin_settings:
            plugin.plugin_settings = plugin_settings

        session.commit()
        logger.info(f"Plugin {plugin_id} updated successfully.")
        return True

    except Exception as e:
        logger.error(f"Error updating plugin with ID {plugin_id}: {e}", exc_info=True)
        session.rollback()
        return False

    finally:
        session.close()


def delete_plugin(plugin_id: int) -> bool:
    """
    Deletes a plugin from the database.

    :param plugin_id: The ID of the plugin to delete.

    :return: True if the plugin was deleted successfully, False if not found.
    """
    session = Session()

    try:
        plugin = session.get(Plugin, plugin_id)
        if plugin:
            session.delete(plugin)
            session.commit()
            logger.info(f"Plugin {plugin_id} deleted successfully.")
            return True
        else:
            logger.warning(f"Plugin with ID {plugin_id} not found.")
            return False

    except Exception as e:
        logger.error(f"Error deleting plugin with ID {plugin_id}: {e}", exc_info=True)
        session.rollback()
        return False

    finally:
        session.close()
