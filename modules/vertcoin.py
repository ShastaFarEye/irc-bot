import willie
import requests

@willie.module.commands('vdiff', 'vdifficulty')
def vdiff(bot, trigger):
    try:
        diff = requests.get('http://explorer.vertcoin.org/chain/vertcoin/q/getdifficulty').text.encode("utf-8").strip()
    except Exception:
        print "getdifficulty failed"
        return
    
    bot.say('Difficulty: {0}'.format(diff))