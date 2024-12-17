from datetime import datetime
from repository.interaction_dao import InteractionDao
from repository.user_dao import ProfileDao

dao = InteractionDao()
profile_dao = ProfileDao()

async def add_interaction(user_id: int, film_id: int):
    profile = await profile_dao.find_by_auth_id(user_id)
    interaction = await dao.get_interaction_by_user_and_film(profile.id, film_id)
    if interaction is None:
        await dao.add(profile_id=profile.id,
                        film_id=film_id,
                        last_interaction=datetime.now(),
                        count_interaction=1,
                    )
    else:
        await dao.update(interaction)

async def add_time_into_interaction(user_id: int, film_id: int, time: int):
    profile = await profile_dao.find_by_auth_id(user_id)
    interaction = await dao.get_interaction_by_user_and_film(profile.id, film_id)
    interaction.watchtime = time
    await dao.update_time(interaction)