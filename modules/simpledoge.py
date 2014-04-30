import willie
import requests
from datetime import timedelta

sd_last_block = None
sd_glob_bot = None


def setup(bot):
    # Can only be done in privmsg by an admin
    global sd_glob_bot
    sd_glob_bot = bot
    bot.memory['api'] = bot.config.simplecoin.api_url
    if not bot.memory['api']:
        raise willie.config.ConfigurationError("Must provide api_url as config")
    bot.memory['name'] = bot.config.simplecoin.name or "SimpleCoin"
    bot.memory['cmd_prefix'] = bot.config.simplecoin.cmd_prefix or ""

    print bot.memory

    bot.scheduler.clear_jobs()
    func = check_new_block
    func.thread = False
    checker = bot.Job(60, func)
    bot.scheduler.add_job(checker)
    print "Adding new job checker function check_new_block"

    pool.commands = [bot.memory['cmd_prefix'] + 'pool']
    round.commands = [bot.memory['cmd_prefix'] + 'round', bot.memory['cmd_prefix'] + 'luck']
    stats.commands = [bot.memory['cmd_prefix'] + 'stats']


def pool(bot, trigger):
    try:
        results = requests.get(bot.memory['api'] + "/pool_stats").json()
    except Exception:
        print "GET /api/pool_stats failed for .pool"
        return

    hashrate = results['hashrate']
    workers = results['workers']
    bot.say("Workers: {0:,} | Hashrate: {1:1,} MH/s"
            .format(workers, hashrate / 1000.0))


def round(bot, trigger):
    try:
        results = requests.get(bot.memory['api'] + "/pool_stats").json()
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

    bot.say("Luck: {0:1,}% | Round Duration: {1} | Est. Time Remaining: {2}"
            .format(luck, round_duration_formatted, est_sec_remaining_formatted))


def stats(bot, trigger):
    address = trigger.group(2)

    try:
        results = requests.get(bot.memory['api'] + '/' + address).json()
    except Exception:
        print "GET /api/<address> failed for .stats"
        return

    workers = results['workers']
    message = ' | '.join(['[{0}] {1}'
                          .format('online' if w['online'] else 'offline',
                                  w['name']) for w in workers])
    bot.say(message)


def check_new_block(bot):
    global sd_last_block, sd_glob_bot
    # jobs automatically get provided the bot context when run
    try:
        results = requests.get(bot.memory['api'] + "/last_block").json()
    except Exception:
        print "GET /api/last_block failed on check_new_block"
        return

    new_block = results['height']
    print(bot.memory['name'] + ' Block: {0}'.format(new_block))
    # don't announce anything on boot, just set the last block
    if sd_last_block is not None and new_block > sd_last_block:
        block_msg = ('New block #{0:,} found by {1} on {2}! '
                     '[Duration: {3} | Diff: {4:3,} | Luck: {5:1,}]'
                     .format(new_block, results['found_by'], bot.memory['name'],
                             results['duration'], results['difficulty'],
                             results['luck']))
        sd_glob_bot.say(block_msg)
    sd_last_block = new_block
