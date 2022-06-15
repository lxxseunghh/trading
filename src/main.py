import datetime
import time
import traceback
from exchange import Exchange
from slack_bot import SlackBot


if __name__ == '__main__':
    exchange = Exchange()
    alerter = SlackBot('alerter')
    base_time = [datetime.time(hour=9),
        datetime.time(hour=9, minute=1), datetime.time(hour=9, minute=2)]
    operation = False
    posted_message = False
    # set target
    exchange.update_target()
    alerter.post_message('Start trading')
    alerter.post_message(exchange)
    # write log
    with open('./log/' + exchange.symbol.split('/')[0] + '.txt', 'a') as f:
        f.write(exchange.log() + '\n')
    # repeat for every seconds
    while True:
        try:
            now = datetime.datetime.now()
            # at AM 09:00
            if operation and (base_time[0] <= now.time() < base_time[1]):
                exchange.clear_position()
                operation = False
            # at AM 09:01
            if not operation and (base_time[1] <= now.time() < base_time[2]):
                exchange.update_target()
                alerter.post_message('Updated target price')
                alerter.post_message(exchange)
                operation = True
                # write log
                with open('./log/' + exchange.symbol.split('/')[0] + '.txt', 'a') as f:
                    f.write(exchange.log() + '\n')
            # try entering position every second
            if operation and exchange.position_type is None:
                if exchange.enter_position():
                    alerter.post_message('Entered a new position')
                    alerter.post_message(exchange)
        # exception handling
        except Exception as e:
            traceback.print_exc()
            alerter.post_message('# error\n' + str(e))
        # sleep 1 second
        print(exchange.log())
        sleep_time = (1000000 - now.microsecond) / 1000000
        time.sleep(sleep_time)
