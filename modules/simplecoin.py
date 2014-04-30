import willie
import requests
from datetime import timedelta


def setup(bot):
    bot.memory['api'] = bot.config.simplecoin.api_url
    if not bot.memory['api']:
        raise willie.config.ConfigurationError("Must provide api_url as config")
    bot.memory['name'] = bot.config.simplecoin.name or "SimpleCoin"
    bot.memory['cmd_prefix'] = bot.config.simplecoin.cmd_prefix or ""
    bot.memory['last_block'] = None

    # output our settings as detected
    print bot.memory

    bot.scheduler.clear_jobs()
    func = check_new_block
    func.thread = False
    checker = bot.Job(60, func)
    bot.scheduler.add_job(checker)
    print "Initiating new block checker"

    pool.commands = [bot.memory['cmd_prefix'] + 'pool']
    round.commands = [bot.memory['cmd_prefix'] + 'round', bot.memory['cmd_prefix'] + 'luck']
    stats.commands = [bot.memory['cmd_prefix'] + 'stats']
    last_block.commands = [bot.memory['cmd_prefix'] + 'last_block']


def pool(bot, trigger):
    try:
        results = requests.get(bot.memory['api'] + "/pool_stats").json()
    except Exception:
        print "GET /api/pool_stats failed for .pool"
        bot.say("Problem connecting to " + bot.memory['name'])
        return

    hashrate = results['hashrate']
    workers = results['workers']
    bot.say("Workers: {:,} | Hashrate: {:,.1f} MH/s"
            .format(workers, hashrate / 1000.0))


def round(bot, trigger):
    try:
        results = requests.get(bot.memory['api'] + "/pool_stats").json()
    except Exception:
        print "GET /api/pool_stats failed for .round"
        bot.say("Problem connecting to " + bot.memory['name'])
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

    bot.say("Luck: {:,.1f}% | Round Duration: {} | Est. Time Remaining: {}"
            .format(luck, round_duration_formatted, est_sec_remaining_formatted))


def stats(bot, trigger):
    address = trigger.group(2)

    try:
        results = requests.get(bot.memory['api'] + '/' + address).json()
    except Exception:
        print "GET /api/<address> failed for .stats"
        bot.say("Problem connecting to " + bot.memory['name'])
        return

    workers = results['workers']
    message = ' | '.join(['[{0}] {1}'
                          .format('online' if w['online'] else 'offline',
                                  w['name']) for w in workers])
    bot.say(message)


def last_block(bot, trigger=None, results=None):
    msg = 'New block '
    if results is None:
        try:
            results = requests.get(bot.memory['api'] + "/last_block").json()
        except Exception:
            print "GET /api/last_block failed on check_new_block"
            bot.say("Problem connecting to " + bot.memory['name'])
            return
        msg = 'Last block '

    block_msg = ('{} #{height:,} found by {found_by} on {} '
                 '[Duration: {duration} | Diff: {difficulty:,.3f} | Luck: {luck:,.0f}%]'
                 .format(msg, bot.memory['name'], **results))
    bot.msg(bot.config.core.channels[0], block_msg)


def check_new_block(bot):
    """ Called every 60 seconds to see if a new block has been found """
    # jobs automatically get provided the bot context when run
    try:
        results = requests.get(bot.memory['api'] + "/last_block").json()
    except Exception:
        print "GET /api/last_block failed on check_new_block"
        return

    lb = bot.memory['last_block']
    # don't announce anything on boot, just set the last block
    if lb is not None and results['height'] > lb:
        last_block(bot, results=results)
    print "Blockheight " + str(results['height'])
    bot.memory['last_block'] = results['height']
