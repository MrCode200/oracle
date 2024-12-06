from logging import getLogger
from typing import Type

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from backend.src.database import PluginModel, PluginDTO, engine

logger = getLogger("oracle.app")

Session = sessionmaker(bind=engine)


def convert_to_dto(plugin: PluginModel) -> PluginDTO | None:
    """
    Helper function to convert an IndicatorModel to an IndicatorDTO.
    """
    if not plugin:
        return None
    return PluginDTO(
        id=plugin.id,
        profile_id=plugin.profile_id,
        name=plugin.name,
        settings=plugin.plugin_settings,
    )


def create_plugin(
        profile_id: int, name: str, settings: dict
) -> PluginDTO | None:
    """
    Creates a new plugin for the profile in the database.

    :param profile_id: The ID of the profile.
    :param name: The name of the plugin.
    :param settings: The settings of the plugin.

    :return: The newly created Plugin object.
    """
    session = Session()

    try:
        new_plugin = PluginModel(
            profile_id=profile_id,
            name=name,
            plugin_settings=settings,
        )
        session.add(new_plugin)
        session.commit()

        logger.info(
            f"Plugin {name} created successfully for profile {profile_id}."
        )
        return convert_to_dto(new_plugin)

    except IntegrityError as e:
        logger.error(f"Error creating plugin {name}: {e}", exc_info=True)
        session.rollback()
        return None

    finally:
        session.close()


def get_plugin(
        id: int | None = None,
        profile_id: int | None = None,
        name: str | None = None,
) -> PluginDTO | list[PluginDTO] | None:
    """
    Retrieves a plugin from the database by ID, profile ID, or name.

    :param id: The ID of the plugin.
    :param profile_id: The ID of the profile.
    :param name: The name of the plugin.

    :return: The Plugin object or None if not found.
    """
    session = Session()

    try:
        if id is not None:
            return convert_to_dto(session.get(PluginModel, id))
        elif profile_id is not None:
            return [convert_to_dto(plugin) for plugin in
                    session.query(PluginModel).filter_by(profile_id=profile_id).all()]
        elif name is not None:
            return convert_to_dto(session.query(PluginModel).filter_by(name=name).first())
        else:
            return [convert_to_dto(plugin) for plugin in session.query(PluginModel).all()]

    except Exception as e:
        logger.error(f"Error retrieving plugin: {e}", exc_info=True)
        return None

    finally:
        session.close()


def update_plugin(
        id: int, name: str | None = None, plugin_settings: dict | None = None
) -> bool:
    """
    Updates a plugin in the database.

    :param id: The ID of the plugin to update.
    :param name: The new plugin name (optional).
    :param plugin_settings: The new plugin settings (optional).

    :return: True if the plugin was updated successfully, False otherwise.
    """
    session = Session()

    try:
        plugin = session.get(PluginModel, id)
        if not plugin:
            logger.warning(f"Plugin with ID {id} not found.")
            return False

        if name:
            plugin.name = name
        if plugin_settings:
            plugin.plugin_settings = plugin_settings

        session.commit()
        logger.info(f"Plugin {id} updated successfully.")
        return True

    except Exception as e:
        logger.error(f"Error updating plugin with ID {id}: {e}", exc_info=True)
        session.rollback()
        return False

    finally:
        session.close()


def delete_plugin(id: int) -> bool:
    """
    Deletes a plugin from the database.

    :param id: The ID of the plugin to delete.

    :return: True if the plugin was deleted successfully, False if not found.
    """
    session = Session()

    try:
        plugin = session.get(PluginModel, id)
        if plugin:
            session.delete(plugin)
            session.commit()
            logger.info(f"Plugin {id} deleted successfully.")
            return True
        else:
            logger.warning(f"Plugin with ID {id} not found.")
            return False

    except Exception as e:
        logger.error(f"Error deleting plugin with ID {id}: {e}", exc_info=True)
        session.rollback()
        return False

    finally:
        session.close()
