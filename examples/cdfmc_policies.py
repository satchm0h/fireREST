#!/bin/env python3

import os
import time
import json
import logging
import argparse
import coloredlogs
from fireREST import cdFMC

CDO_TOKEN_FILE = '~/.cdo_token'
CDO_TOKEN_EV = 'CDO_TOKEN'
CDO_DEFAULT_REGION = 'us'

def _format(json_obj):
    return json.dumps(json_obj, sort_keys=True, indent=2, separators=(',', ': '))


def init():
    '''
        init()
        Handle command line args, setup log, etc..
    '''

    global DEFAULTS

    # Configure logging
    coloredlogs.install(level='DEBUG',
                        fmt='%(asctime)s %(levelname)s %(message)s')

    # Supress requests log
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)

    # Handle command line args
    parser = argparse.ArgumentParser(description='Install/Update FMC Dynamic Objects')
    parser.add_argument('-D, --debug', dest='debug',
                        help='Full debug output',
                        action='store_true')
    parser.add_argument('-t --token', dest='token',
                        help=f'CDO API token (Please use {CDO_TOKEN_FILE} file or {CDO_TOKEN_EV} env var instead)',
                        default=None)
    parser.add_argument('-r --region', dest='region',
                        help=f'CDO Region. Must be one of: "us", "eu", or "apj Default: {CDO_DEFAULT_REGION}',
                        default=CDO_DEFAULT_REGION)
    parser.add_argument('-b, --bulk', dest='bulk', action='store_true',
                        help='Process all the Access Policies on the FMC at once',
                        default=None)
    options = parser.parse_args()

    # Enable debug
    if not options.debug:
        coloredlogs.decrease_verbosity()

    # Load from env if not provided on the command line
    if options.token is None:
        if 'CDO_TOKEN' in os.environ:
            logging.debug('Loading token from environment')
            options.token = os.environ.get(CDO_TOKEN_EV)
        elif os.path.isfile(os.path.expanduser(CDO_TOKEN_FILE)):
            logging.debug('Loading token from file')
            with open(os.path.expanduser(CDO_TOKEN_FILE), 'r') as fh:
                options.token = fh.read().strip()
        else:
            logging.fatal("Unable to find CDO token file")
            exit(5)
        
    return options


def main(options):
    ''' Let's make do stuff
    '''

    # Connect to the FMC RestAPI
    start = time.time()
    logging.info(f'Connecting to cdFMC')
    fmc = cdFMC(options.token, options.region)
    logging.debug(f"Connected.")
    elapsed = time.time() - start
    logging.info('Time elapsed for session establishment: %1.1f secs', elapsed)

    policies = fmc.policy.accesspolicy.accessrule.get(container_name='Ted API Test')

    logging.info(json.dumps(policies, indent=2))


if __name__ == '__main__':
    main(init())
