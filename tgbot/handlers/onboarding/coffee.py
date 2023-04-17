import datetime
import pytz
from typing import List


def send_weekly_messages():
    # Get the current date and time in Moscow time
    tz_moscow = pytz.timezone('Europe/Moscow')
    now = datetime.datetime.now(tz_moscow)
    day_of_week = now.weekday()  # Monday is 0 and Sunday is 6
    time_of_day = now.time()

    if day_of_week == 0 and time_of_day == datetime.time(9, 0):
        # It's Monday at 9:00 AM Moscow time
        # Query the database to get all users with activity "in the game" and status "active"
        users = get_users_with_activity_and_status("in the game", "active")

        for user in users:
            # Send a message to the user asking if they are ready for a new week of random coffee
            send_message(user, "Hello, start a new week of random coffee, do you feel it? yes - no")
            response = wait_for_response(user, timeout=300)  # Wait for 5 minutes for a response

            if response == "no":
                # If the user responds "no", set their activity to "paused"
                set_user_activity(user, "paused")
            elif response == "yes":
                # If the user responds "yes", continue to the next step
                pass

        # Randomly form pairs from the list of users with activity "in the game" and status "active"
        pairs = random_pairs(users)

        # Assign the system administrator to any employee who is left without a pair
        assign_admin_to_unpaired_employee(pairs)

        # Send each participant a message with the name and email of their pair
        for pair in pairs:
            send_message(pair[0],
                         f"Hello, your couple for this week is {pair[1].full_name} ({pair[1].email}). Contact them in any convenient way and arrange a meeting.")


    elif day_of_week == 4 and time_of_day == datetime.time(17, 0):

        # It's Friday at 5:00 PM Moscow time

        # Send each participant a message with a survey asking if their meeting took place, how they liked it, and if they will attend next week

        participants = get_users_with_activity("in the game")

        for participant in participants:

            send_message(participant, "Did your meeting take place? (yes or no)")

            meeting_status = wait_for_response(participant, timeout=300)  # Wait for 5 minutes for a response

            send_message(participant, "How did you like your meeting? (good or bad)")

            meeting_feedback = wait_for_response(participant, timeout=300)  # Wait for 5 minutes for a response

            send_message(participant, "Will you attend next week? (yes or no)")

            next_week_status = wait_for_response(participant, timeout=300)  # Wait for 5 minutes for a response

            if next_week_status == "no":
                # If the user responds "no", change their activity to "paused"

                set_user_activity(participant, "paused")
