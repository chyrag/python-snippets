#!/usr/bin/env python3

import os
from ftplib import FTP, error_perm
from argparse import ArgumentParser


def download(ftp, fpath, dumpdir):
    """ Download a given file from given FTP object into dump directory """
    lpath = os.path.join(dumpdir, os.path.basename(fpath))
    print(fpath)
    ret = ftp.retrbinary("RETR " + fpath, open(lpath, 'wb').write)
    if not ret.startswith('226 '):
        return False
    return True


def recurse(ftp, limit, dumpdir, directory):
    """ Recurse into a directory """
    path = directory
    ftp.cwd(path)
    files = ftp.nlst()
    for dirent in files:
        fpath = os.path.join(path, dirent)
        try:
            size = ftp.size(fpath)
            if size < limit:
                if not download(ftp, fpath, dumpdir):
                    print('Failed to download {}'.format(fpath))
        except error_perm:
            recurse(ftp, limit, dumpdir, fpath)
        except Exception as e:
            print('Caught unexpected exception {}'.format(type(e).__name__))
            raise


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        "-s", "--server", dest="ftpserver", help="FTP server", required=True)
    parser.add_argument("-l", "--limit", dest="limit", help="File size limit")
    parser.add_argument(
        "-d", "--dump", dest="dumpdir", help="Directory to download files")
    args = parser.parse_args()
    if args.limit is None:
        args.limit = "4096"
    if args.dumpdir is None:
        args.dumpdir = '/tmp'
    print('Downloading size < {} into {} from {}'.format(args.limit,
                                                         args.dumpdir,
                                                         args.ftpserver))
    try:
        ftp = FTP(args.ftpserver)
        ftp.set_debuglevel(0)
        ftp.login()
        recurse(ftp, int(args.limit), args.dumpdir, '/')
        ftp.quit()
    except error_perm:
        pass
    except KeyboardInterrupt:
        pass
