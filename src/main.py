import datetime
import time
import traceback
from exchange import Exchange
from slack_bot import SlackBot


if __name__ == '__main__':
    exchange = Exchange()
    alerter = SlackBot('alerter')
    base_time = [datetime.time(hour=8, minute=59),
        datetime.time(hour=9), datetime.time(hour=9, minute=1)]
    operation = False
    posted_message = False
    # set target
    exchange.update_target()
    alerter.post_message(exchange)
    # repeat for every seconds
    while True:
        try:
            now = datetime.datetime.now()
            # at AM 08:59
            if operation and (base_time[0] < now.time() < base_time[1]):
                exchange.clear_position()
                operation = False
            # at AM 09:00
            if not operation and (base_time[1] < now.time() < base_time[2]):
                exchange.update_target()
                operation = True
            # try entering position every second
            if operation and exchange.position_type is None:
                if exchange.enter_position():
                    alerter.post_message(exchange)
            # post current info every hour
            if not posted_message and now.minute == 0:
                alerter.post_message(exchange)
                posted_message = True
            elif now.minute != 0:
                posted_message = False
        # exception handling
        except Exception as e:
            traceback.print_exc()
            alerter.post_message('# error\n' + str(e))
        # sleep 1 second
        print('*', now.strftime('%Y-%m-%d %H:%M:%S'))
        sleep_time = (1000000 - now.microsecond) / 1000000
        time.sleep(sleep_time)
