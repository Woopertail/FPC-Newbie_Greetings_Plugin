"""
Данный плагин высылает сообщение пользователю, если он написал впервые за историю работы FunPay Cardinal.
Данные об уже написавших вам пользователях хранятся в storage/cache/newbie_detect_plugin_cache.json.
ВНИМАНИЕ! Новые пользователи - это те, кого нет в storage/cache/newbie_detect_plugin_cache.json.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cardinal import Cardinal

import os
import json
import logging
from FunPayAPI.runner import MessageEvent


# -------------------- НАСТРОЙКА ПЛАГИНА ---------------------

# Приветственное сообщение.
# Доступные переменные:
# $username - написавший пользователь.
GREETINGS_MESSAGE = """Привет, $username!
Я вижу тебя впервые!
К сожалению, мой хозяин не настроил текст приветствия,
потому, давай подождем его вместе."""

# -- НЕ РЕДАКТИРУЙТЕ КОД НИЖЕ ДЛЯ ПРАВИЛЬНОЙ РАБОТЫ ПЛАГИНА --


logger = logging.getLogger(f"Cardinal.{__name__}")


def load_newbies_from_cache() -> list[str]:
    """
    Загружает из кэша список пользователей, которые уже писали на аккаунт.

    :return: список никнеймов пользователей.
    """
    if not os.path.exists("storage/cache/newbie_detect_plugin.json"):
        return []
    with open("storage/cache/newbie_detect_plugin_cache.json", "r", encoding="utf-8") as f:
        users = f.read()

    try:
        users = json.loads(users)
        return users
    except json.decoder.JSONDecodeError:
        return []


def save_newbies_to_cache(newbies: list[str]) -> None:
    """
    Сохраняет в кэш список пользователей, которые уже писали на аккаунт.

    :param newbies: список никнеймов пользователей.
    """
    users = json.dumps(newbies, indent=4, ensure_ascii=False)
    if not os.path.exists("storage/cache/"):
        os.makedirs("storage/cache")
    with open("storage/cache/newbie_detect_plugin_cache.json", "w", encoding="utf-8") as f:
        f.write(users)


OLD_USERS = load_newbies_from_cache()
logger.info("Загрузил пользователей, которые уже писали мне.")


def send_newbie_message_handler(msg: MessageEvent, cardinal: Cardinal, *args) -> None:
    """
    Отправляет приветственное сообщение пользователю, если он написал впервые.

    :param msg: не используется.
    :param cardinal: экземпляр кардинала.
    """
    if msg.sender_username is None or not GREETINGS_MESSAGE:
        return

    if msg.sender_username in OLD_USERS:
        return
        
    text = GREETINGS_MESSAGE.replace("$username", msg.sender_username)

    logger.info(f"Пользователь {msg.sender_username} пишет впервые. Отправляю приветственное сообщение.")
    OLD_USERS.append(msg.sender_username)
    save_newbies_to_cache(OLD_USERS)

    new_msg_object = MessageEvent(msg.node_id, text, msg.sender_username, None)
    cardinal.send_message(new_msg_object)


REGISTER_TO_NEW_MESSAGE_EVENT = [send_newbie_message_handler]
