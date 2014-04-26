import willie
import requests
from datetime import timedelta

sd_last_block = None
sd_glob_bot = None

@willie.module.commands('pool')
def pool(bot, trigger):
    try:
        results = requests.get('http://simpledoge.com/api/pool_stats').json()
    except Exception:
        print "GET /api/pool_stats failed for .pool"
        return

    hashrate = results['hashrate']
    workers = results['workers']
    bot.say("Workers: {0} | Hashrate: {1}".format(workers, "%0.1f Mh/s" % (hashrate/1000.0)))

@willie.module.commands('round', 'luck')
def round(bot, trigger):
    try:
        results = requests.get('http://simpledoge.com/api/pool_stats').json()
    except Exception:
        print "GET /api/pool_stats failed for .round"
        return

    # Luck
    completed_shares = results['completed_shares']
    shares_to_solve = results['shares_to_solve']
    luck = (shares_to_solve / completed_shares) * 100.0

    # Round Duration
    round_duration = results['round_duration']
    round_duration_formatted = timedelta(seconds=int(round_duration))

    # Estimated Time Left
    est_sec_remaining = results['est_sec_remaining']
    est_sec_remaining_formatted = None
    if est_sec_remaining > 0:
        est_sec_remaining_formatted = timedelta(seconds=int(est_sec_remaining))
    else:
        est_sec_remaining_formatted = '-' + str(timedelta() - timedelta(seconds=int(est_sec_remaining)))

    bot.say("Luck: {0} | Round Duration: {1} | Est. Time Remaining: {2}".format(("%0.1f%%" % luck), round_duration_formatted, est_sec_remaining_formatted))

@willie.module.commands('stats')
def stats(bot, trigger):
    address = trigger.group(2)

    try:
        results = requests.get('http://simpledoge.com/api/'+address).json()
    except Exception:
        print "GET /api/<address> failed for .stats"
        return

    workers = results['workers']
    message = ""
    for w in workers:
        status = 'online' if w['online'] else 'offline'
        message += '[{0}] {1} | '.format(status, w['name'])
    message = message[:-2]

    bot.say(message)

@willie.module.commands('sd')
def sd(bot, trigger):
    # Can only be done in privmsg by an admin
    if not trigger.admin:
        return

    global sd_glob_bot
    sd_glob_bot = bot

    bot.scheduler.clear_jobs
    func = check_new_block
    func.thread = False
    checker = bot.Job(60, func)
    bot.scheduler.add_job(checker)

def check_new_block(bot):
    global sd_last_block, sd_glob_bot
    # jobs automatically get provided the bot context when run
    try:
        results = requests.get('http://simpledoge.com/api/last_block').json()
    except Exception:
        print "GET /api/last_block failed on check_new_block"
        return

    new_block = results['height']
    print('SimpleDoge Block: {0}'.format(new_block))
    # sd_glob_bot.msg("#simpledoge", 'SimpleDoge Block: {0}'.format(new_block))
    # don't announce anything on boot, just set the last block
    if sd_last_block is not None and new_block > sd_last_block:
        block_msg = 'New block #{0} found by {1} on SimpleDoge! [Duration: {2} | Diff: {3}]'.format(new_block, results['found_by'], results['duration'], ('%0.3f' % results['difficulty']))
        print(block_msg)
        sd_glob_bot.msg("#simpledoge", block_msg)
    sd_last_block = new_block
