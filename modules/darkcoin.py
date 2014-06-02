import willie
import requests

@willie.module.commands('drkdiff', 'drkdifficulty')
def vdiff(bot, trigger):
    try:
        results = requests.get('http://simpledrk.com/api/network_stats').json()
    except Exception:
        print "getdifficulty failed"
        return
    
    bot.say('Difficulty: {difficulty:,.3f}'.format(**results))