#!/bin/bash
# vim: dict+=/usr/share/beakerlib/dictionary.vim cpt=.,w,b,u,t,i,k
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#   runtest.sh of /tools/annobin/Sanity/annocheck-silently-ignores-any-file-parameter
#   Description: Test for BZ#1973981 (annocheck silently ignores any file parameter)
#   Author: Martin Cermak <mcermak@redhat.com>
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#   Copyright (c) 2021 Red Hat, Inc.
#
#   This program is free software: you can redistribute it and/or
#   modify it under the terms of the GNU General Public License as
#   published by the Free Software Foundation, either version 2 of
#   the License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be
#   useful, but WITHOUT ANY WARRANTY; without even the implied
#   warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#   PURPOSE.  See the GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program. If not, see http://www.gnu.org/licenses/.
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Include Beaker environment
. /usr/share/beakerlib/beakerlib.sh || exit 1

rlJournalStart
    rlPhaseStartSetup
        rlRun "TMP=$(mktemp -d)"
        rlRun "pushd $TMP"
    rlPhaseEnd

    rlPhaseStartTest
        for i in `seq 0 299`; do touch ${i}.sample; done
        samplecnt=$(ls *.sample | wc -l)
        testcnt=$(ls *.sample | \
                  xargs annocheck |& \
                  grep -F \
                      -e '.sample: unable to read magic number' \
                      -e '.sample: is not an ELF format file' \
                  | wc -l)
        rlRun "test $samplecnt -eq 300"
        rlRun "test $testcnt -eq 300"
    rlPhaseEnd

    rlPhaseStartCleanup
        rlRun "popd"
        rlRun "rm -r $TMP"
    rlPhaseEnd
rlJournalPrintText
rlJournalEnd
