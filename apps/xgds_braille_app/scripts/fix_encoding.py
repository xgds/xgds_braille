#!/usr/bin/env python

import os
import sys
import codecs
import shutil
import datetime

def fix_utf(infilename,outfilename,encoding='utf-8'):
    if os.path.exists(outfilename):
        print '%s already exists' % outfilename
        return
    print 'converting %s from UTF to ASCII' % infilename
    print 'reading', infilename
    ifp = codecs.open(infilename,'rb')
    ofp = open(outfilename,'w')
    print 'writing', outfilename
    for line in ifp:
        newline = codecs.decode(line,'utf8','ignore')
        ofp.write(codecs.encode(newline,'ascii','ignore'))
    ifp.close()
    ofp.close()

def fix_crlf(infilename,outfilename):
    if os.path.exists(outfilename):
        print '%s already exists' % outfilename
        return
    print 'converting %s from CRLF to LF' % infilename
    crlf = '\r\n'
    lf = '\n'
    print 'reading', infilename
    ifp = open(infilename, 'rb')
    content = ifp.read()
    ifp.close()
    content = content.replace(crlf,lf)
    print 'writing', outfilename
    ofp = open(outfilename, 'wb')
    ofp.write(content)
    ofp.close()


if __name__=="__main__":
    import optparse
    parser = optparse.OptionParser('usage: %prog [options] <data_root_dir>')
    parser.add_option('-t', '--test',
                      action='store_true', default=False,
                      help='Run in test mode: find files and report them but do not process them')

    opts, args = parser.parse_args()

    if not args:
        print parser.print_help()
        sys.exit(1)

    # the root directory to import is the first positional argument
    # (after any "-" or "--" flags)
    import_root = args[0]

    jobs_tmp_file = '/tmp/fix_encodings.%s' % datetime.datetime.utcnow().isoformat()
    # Two classes of known problem are UTF encoding instead of ASCII,
    # and CRLF line endings rather than POSIX.  This will find those
    # two known encoding problems using command line tools and write
    # them into a temp file.  The first finds UTF that do not have
    # CRLF, otherwise those would be in the list twice.
    os.system('file `find %s -name *.csv` | grep UTF | grep -v CRLF > %s' % \
                  (import_root, jobs_tmp_file))
    os.system('file `find %s -name *.csv` | grep CRLF >> %s' % \
                  (import_root, jobs_tmp_file))

    if opts.test:
        # print the encoding errors to stdout, move the file
        # containing the encoding problems aside for the next run, and
        # exit.
        print 'Found the following problems:'
        os.system('cat %s' % jobs_tmp_file)
        shutil.move(jobs_tmp_file, '%s.test' % jobs_tmp_file)
        sys.exit(0)

    # Go through the list of things to fix
    fp = open('/tmp/encodings_to_fix','r')
    for line in fp:
        # first half is the filename, second half is the problematic encoding
        infile = line.split(':')[0]
        problem = line.split(':')[1].strip()
        if 'UTF' in problem: # (also handles converting CRLF)
            # temp filenames
            tmpname1 = '/tmp/%s.ascii' % os.path.basename(infile)
            tmpname2 = '/tmp/%s.fixed' % os.path.basename(infile)
            # convert UTF to ASCII
            fix_utf(infile,tmpname1)
            # change line endings
            fix_crlf(tmpname1,tmpname2)
            # move final file to the original location
            shutil.move(tmpname2,infile)
        elif 'CRLF' in problem:
            # temp filename
            tmpname = '/tmp/%s.fixed' % os.path.basename(infile)
            # change line endings
            fix_crlf(infile,tmpname)
            # move final file to the original location
            shutil.move(tmpname,infile)
        else:
            # TODO: might need to handle other stuff
            print 'need to handle this case: "%s"' % problem

    # TODO: delete the /tmp/encodings_to_fix file at the end?
