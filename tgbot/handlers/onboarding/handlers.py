from enum import IntFlag, auto

from django.db.models import Q
from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from tgbot.handlers.onboarding import static_text, registration
from users.models import User, UserMeeting


class RegistrationStates(IntFlag):
    CHECK_EMAIL = auto()
    CHECK_CODE = auto()


class EndGameStates(IntFlag):
    IS_LIKED = auto()
    IS_JOIN_NEXT = auto()


def command_start(update: Update, context: CallbackContext):
    text = static_text.registration_message.format(
        first_name=update.message.from_user.first_name
    )
    update.message.reply_text(text=text)
    return RegistrationStates.CHECK_EMAIL


def check_email_handler(update: Update, context: CallbackContext):
    """
    Validate email and send code
    """
    try:
        registration.check_email(update, context)
    except registration.HandledError:
        return ConversationHandler.END

    return RegistrationStates.CHECK_CODE


def check_code_handler(update: Update, context: CallbackContext):
    """
    Validate code and create User
    """
    try:
        registration.check_code(update, context)
    except registration.HandledError:
        return RegistrationStates.CHECK_CODE

    return ConversationHandler.END


def is_player_in_game_handler(update: Update, context: CallbackContext):
    """
    Handler for answer about join in game
    """
    if update.message.text.lower() == 'да':
        User.objects.filter(update.message.from_user.id).update(activity='game')
    update.message.reply_text(
        static_text.answer_is_ok
    )


def is_met_handler(update: Update, context: CallbackContext):
    """
    Handler for answer after game
    """
    meeting = UserMeeting.objects.filter(
        Q(user_1_id=update.message.from_user.id) | Q(user_2_id=update.message.from_user.id)
    ).last()
    meeting.is_met = update.message.text.lower() == 'да'
    meeting.save()
    update.message.reply_text(
        static_text.end_game_message2
    )
    return EndGameStates.IS_LIKED


def is_liked_handler(update: Update, context: CallbackContext):
    """
    Handler for answer after game
    """
    meeting = UserMeeting.objects.filter(
        Q(user_1_id=update.message.from_user.id) | Q(user_2_id=update.message.from_user.id)
    ).last()
    meeting.is_met = update.message.text.lower() == 'хорошо'
    meeting.save()
    update.message.reply_text(
        static_text.end_game_message3
    )
    return EndGameStates.IS_JOIN_NEXT


def is_join_next(update: Update, context: CallbackContext):
    """
    Handler for answer after game
    """
    if update.message.text.lower() == 'да':
        User.objects.filter(update.message.from_user.id).update(activity='game')
    update.message.reply_text(
        static_text.answer_is_ok
    )
    return ConversationHandler.END
