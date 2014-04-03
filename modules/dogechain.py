import willie
import requests

@willie.module.commands('diff', 'difficulty')
def diff(bot, trigger):
    try:
        diff = requests.get('http://dogechain.info/chain/Dogecoin/q/getdifficulty').text.strip()
    except Exception:
        print "getdifficulty failed"
        return
    
    bot.say('Difficulty: {0}'.format(diff))