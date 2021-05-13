#!/bin/bash

. /usr/share/beakerlib/beakerlib.sh || exit 1

set -x

default_cflags=`rpm -E %{build_cflags}`
default_cxxflags=`rpm -E %{build_cxxflags}`
default_ldflags=`rpm -E %{build_ldflags}`

cflags=`rpm -D '%toolchain gcc' -E %{build_cflags}`
cxxflags=`rpm -D '%toolchain gcc' -E %{build_cxxflags}`
ldflags=`rpm -D '%toolchain gcc' -E %{build_ldflags}`

set +x

rlJournalStart
rlPhaseStartTest
    rlRun "rpm -qa | fgrep -e redhat-rpm-config -e gcc -e annobin -e binutils | sort"

    rlRun "test \"$default_cflags\" = \"$cflags\""
    rlRun "test \"$default_cxxflags\" = \"$cxxflags\""
    rlRun "test \"$default_ldflags\" = \"$ldflags\""

    rlRun "gcc $cflags -o hello.o -c hello.c"
    rlRun "annocheck hello.o"
    rlRun "gcc $cflags -o main.o -c main.c"
    rlRun "gcc $ldflags -o hello main.o hello.o"
    rlRun "annocheck hello"
    rlRun "./hello | grep \"Hello World\""

    rlRun "g++ $cxxflags -o hello-cpp.o -c hello.cpp"
    rlRun "annocheck hello-cpp.o"
    rlRun "g++ $cxxflags -o main-cpp.o -c main.cpp"
    rlRun "g++ $ldflags -o hello-cpp main-cpp.o hello-cpp.o"
    rlRun "annocheck hello-cpp"
    rlRun "./hello-cpp | grep \"Hello World\""
rlPhaseEnd
rlJournalPrintText
rlJournalEnd
