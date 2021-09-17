import json
import datetime
from typing import Optional

from bot._types import JSON_DATA
from bot.utils.custom_exceptions import (
    ToManyPlaylists,
    NoGuildPlaylists,
    PlaylistNotFound,
)
from bot.utils.file_utils import PlayListsFile, update_json


@update_json(PlayListsFile)
def save_new_playlist(
    guild_id: int, playlist: list, json_data: JSON_DATA, name: Optional[str] = None
) -> str:
    # playlist_1 = copy.deepcopy(playlist)
    # [item.pop("requester", 0) for item in playlist_1]
    new_playlist = [{"id": track["id"]} for track in playlist]

    guild_id = str(guild_id)
    guild_playlists = json_data[guild_id] if guild_id in json_data else {}

    length = len(guild_playlists)
    if length >= 10:
        raise ToManyPlaylists
    if name is None:
        name = f"Playlist {length + 1}"
    else:
        name = name.strip()

    date = datetime.date.today()
    guild_playlists[name] = {"tracks": new_playlist, "date": date.toordinal()}
    json_data[guild_id] = guild_playlists

    return name


def get_single_guild_playlist(guild_id):
    playlists = PlayListsFile.get()
    return playlists.get(str(guild_id))


@update_json(PlayListsFile)
def rename_playlist(guild_id: int, old_name: str, new_name: str, json_data: JSON_DATA):
    guild_playlists = get_single_guild_playlist(guild_id)
    if guild_playlists is None:
        raise NoGuildPlaylists
    if old_name not in guild_playlists:
        raise PlaylistNotFound
    guild_playlists[new_name] = guild_playlists.pop(old_name)
    json_data[str(guild_id)] = guild_playlists


@update_json(PlayListsFile)
def delete_playlist(guild_id: int, playlist_name: str, json_data: JSON_DATA):
    guild_playlists = get_single_guild_playlist(guild_id)
    if guild_playlists is None:
        raise NoGuildPlaylists
    if playlist_name not in guild_playlists:
        raise PlaylistNotFound
    if len(guild_playlists) == 1:
        del json_data[str(guild_id)]
    else:
        del guild_playlists[playlist_name]
        json_data[str(guild_id)] = guild_playlists
