import willie
import requests

sv_last_block = None
sv_glob_bot = None

@willie.module.commands('vpool')
def vpool(bot, trigger):
    try:
        results = requests.get('http://simplevert.com/api/pool_stats').json()
    except Exception:
        print "GET /api/pool_stats failed for .vpool"
        return
    
    hashrate = results['hashrate']
    workers = results['workers']
    bot.say("Workers: {0} | Hashrate: {1}".format(workers, "%0.1f Mh/s" % (hashrate/1000.0)))

@willie.module.commands('vround', 'vluck')
def vround(bot, trigger):
    try:
        results = requests.get('http://simplevert.com/api/pool_stats').json()
    except Exception:
        print "GET /api/pool_stats failed for .vround"
        return
    
    completed_shares = results['completed_shares']
    shares_to_solve = results['shares_to_solve']
    luck = (shares_to_solve / completed_shares) * 100.0
    bot.say("Luck: {0}".format("%0.1f%%" % luck))

@willie.module.commands('sv')
def sv(bot, trigger):
    # Can only be done in privmsg by an admin
    if not trigger.admin:
        return
    
    global sv_glob_bot
    sv_glob_bot = bot

    bot.scheduler.clear_jobs
    func = check_new_block
    func.thread = False
    checker = bot.Job(60, func)
    bot.scheduler.add_job(checker)

def check_new_block(bot):
    global sv_last_block, sv_glob_bot
    # jobs automatically get provided the bot context when run
    try:
        results = requests.get('http://simplevert.com/api/pool_stats').json()
    except Exception:
        print "GET /api/pool_stats failed on check_new_block"
        return

    new_block = results['last_block_found']
    print('SimpleVert Block: {0}'.format(new_block))
    # sv_glob_bot.msg("#simpledoge", 'SimpleVert Block: {0}'.format(new_block))
    # don't announce anything on boot, just set the last block
    if sv_last_block is not None and new_block > sv_last_block:
        print('New block found on SimpleVert!')
        sv_glob_bot.msg("#simpledoge", "New block found on SimpleVert!")
    sv_last_block = new_block