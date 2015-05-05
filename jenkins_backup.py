#!/usr/bin/env python

import os
from datetime import datetime
import tarfile
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('-P', '--path',
                    action='store',
                    default='/var/lib/jenkins',
                    help='Path to Jenkins home')
parser.add_argument('-p', '--prefix',
                    action='store',
                    default='jenkins_backup',
                    help='Prefix name')
parser.add_argument('-R', '--rotation',
                    action='store',
                    type=int,
                    default=5,
                    help='Rotation period in days')                    
args = vars(parser.parse_args())

# Vars
jenkins_home    =  args.get('path')
jenkins_parent  =  os.path.abspath(os.path.join(jenkins_home, os.pardir))
backup_dir      =  os.path.join(jenkins_home, 'backups')
prefix          =  args.get('prefix')
suffix          =  'tar.gz'
rotation        =  args.get('rotation')

def check_backup_dir():

    """
    This function creates backups dir if it non exists
    """

    if not os.path.isdir(backup_dir):
        os.makedirs(backup_dir)


def clean_obsolete():

    """
    This function leave only 5 newest backups
    """

    files = [ i for i in os.listdir(backup_dir) if i.startswith(prefix) ]
    if len(files) > rotation:
        timestamps = [ k.split('_')[-1].split('.')[0] for k in files ]
        dates = [ datetime.strptime(ts, "%Y-%m-%d") for ts in timestamps ]
        dates.sort()
        last_backups = [ '{0}_{1}.{2}'.format(prefix, x.strftime("%Y-%m-%d"), suffix) for x in dates[-rotation:] ]
        for z in list(set(files) - set(last_backups)):
            os.remove(os.path.join(backup_dir, z))


def apply_timestamp():

    """
    This function generate backup file name
    """

    today = datetime.now().strftime('%Y-%m-%d')
    backup_name = '%s_%s.%s' % (prefix, today, suffix)
    return backup_name


def do_backup():

    """
    This function creates backup tar archive with Jenkins home.
    Add needed dirs which should be excluded to exclude_files list.
    """

    backup_name = apply_timestamp()
    exclude_files = ['jenkins/backups',
                     'jenkins/.cache',
                     'jenkins/workspace']

    def filter_function(tarinfo):
        if tarinfo.name in exclude_files:
            return None
        else:
            return tarinfo

    with tarfile.open(os.path.join(backup_dir, backup_name), mode='w:gz') as jenkins_backup:
        os.chdir('/var/lib')
        jenkins_backup.add('jenkins', filter=filter_function)


if __name__ == "__main__":
    check_backup_dir()
    clean_obsolete()
    do_backup()
