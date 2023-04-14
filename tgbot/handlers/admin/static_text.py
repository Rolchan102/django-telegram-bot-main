command_start = '/stats'
only_for_admins = 'Извините, эта функция доступна только для администраторов. Установите галочку "admin" в панели администратора django.'

secret_admin_commands = f"⚠️ Секретные команды администратора\n" \
                        f"{command_start} - статистика бота"

users_amount_stat = "<b>Пользователи</b>: {user_count}\n" \
                    "<b>24ч активность</b>: {active_24}"
