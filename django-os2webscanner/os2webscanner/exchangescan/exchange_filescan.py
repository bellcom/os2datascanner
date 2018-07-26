"""
Demands:
* starter når den første _done folder er markeret
* hvis filscan indhenter exchange download skal filscan vente indtil en ny folder er markeret med _done.
* Når alt exchange indhold er downloadet skal filscan vide at der ikke er mere indhold at scanne.
"""
import os
import time
import queue
import multiprocessing
import subprocess

from .mailscan_exchange import ExchangeServerScan, read_users
from .settings import NUMBER_OF_EMAIL_THREADS


class ExchangeFilescanner(object):

    def __init__(self, scan_id):
        print('Program started')
        self.scan_id = scan_id
        from scanner.scanner.scanner import Scanner
        self.scanner = Scanner(scan_id)

    def run(self):
        domains = self.scanner.get_domain_objects()
        for domain in domains:
            user_queue = multiprocessing.Queue()
            read_users(user_queue,
                       domain.exchangedomain.get_userlist_file_path())
            done_queue = multiprocessing.Queue()

            scanners = {}
            for i in range(0, NUMBER_OF_EMAIL_THREADS):
                scanners[i] = ExchangeServerScan(user_queue,
                                                 done_queue,
                                                 self.scanner.scan_object.scan_dir,
                                                 domain)
                scanners[i].start()
                print('Started scanner {}'.format(i))
                time.sleep(1)

            print('Scanners started...')

        for key, value in scanners.items():
            self.get_queue_item(done_queue)

            while value.is_alive():
                print('Process with pid {} is still alive'.format(value.pid))
                self.get_queue_item(done_queue)
                time.sleep(1)

    def get_queue_item(self, q):
        item = q.get()
        while item is not None:
            print('Getting item from q: {}'.format(item))
            try:
                item = q.get(True, 1)
                self.start_filescan()

            except queue.Empty:
                print('Queue is empty')
                item = None

    def start_filescan(self):
        # TODO: start file scan on item.
        scanner__dir = self.scanner.scan_object.scan_dir
        log_file = open(self.scanner.scan_object.scan_log_file, "a")
        try:
            process = subprocess.Popen([os.path.join(scanner__dir, 'run.sh'),
                                        str(self.scan_id)], cwd=scanner__dir,
                                       stderr=log_file,
                                       stdout=log_file)
            process.communicate()
        except Exception as e:
            print(e)
            return None


def main():
    exchange_file_scanner = ExchangeFilescanner()
    exchange_file_scanner.run()

# TODO: læg user elementer i en python list og tjek tilsidst eller løbende at alle users er scannet.


main()
