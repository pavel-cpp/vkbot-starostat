from vkbottle import Bot

import settings

bot = Bot(settings.VK_TOKEN)

bot.labeler.vbml_ignore_case = True
