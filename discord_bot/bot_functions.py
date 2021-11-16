
from discord import Webhook, RequestsWebhookAdapter
from lumacode.discord_bot import constants


def send_message(message):

    print("sending message: %s" % message)
    web_hook = Webhook.from_url(constants.web_hook_url, adapter=RequestsWebhookAdapter())
    web_hook.send(message)


if __name__ == "__main__":
    send_message('rawr')
