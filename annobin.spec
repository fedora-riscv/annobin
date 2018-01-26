
# Do not build the annobin plugin with annotation enabled.
# This is because if we are bootstrapping a new build environment we can have
# a new version of gcc installed, but without a new of annobin installed.
# (ie we are building the new version of annobin to go with the new version
# of gcc).  If the *old* annobin plugin is used whilst building this new
# version, the old plugin will complain that version of gcc for which it
# was built is different from the version of gcc that is now being used, and
# then it will abort.
%undefine _annotated_build

Name:    annobin
Summary: Binary annotation plugin for GCC
Version: 3.2
Release: 2%{?dist}

License: GPLv3+
URL:     https://fedoraproject.org/wiki/Toolchain/Watermark

# Use "--without tests" to disable the testsuite.  The default is to run them.
%bcond_without tests

#---------------------------------------------------------------------------------
Source:  https://nickc.fedorapeople.org/annobin-%{version}.tar.xz
# For the latest sources use:  git clone git://sourceware.org/git/annobin.git

# This is a gcc plugin, hence gcc is required.
Requires: gcc
Requires(post): /sbin/install-info
Requires(preun): /sbin/install-info

BuildRequires: gcc-plugin-devel pkgconfig coreutils info

%description
A plugin for GCC that records extra information in the files that it compiles,
and a set of scripts that analyze the recorded information.  These scripts can
determine things ABI clashes in compiled binaries, or the absence of required
hardening options.

Note - the plugin is enabled in gcc builds via flags provided by the
redhat-rpm-macros package, and the analysis tools rely upon the readelf program
from the binutils package.

#---------------------------------------------------------------------------------
%if %{with tests}

%package tests
Summary: Test scripts and binaries for checking the behaviour and output of the annobin plugin

%description tests
Provides a means to test the generation of annotated binaries and the parsing
of the resulting files.
# FIXME: Does not actually do this yet...

%endif
#---------------------------------------------------------------------------------

%global ANNOBIN_PLUGIN_DIR %(g++ -print-file-name=plugin)

%prep
%autosetup -p1

# The plugin has to be configured with the same arcane configure
# scripts used by gcc.  Hence we must not allow the Fedora build
# system to regenerate any of the configure files.
touch aclocal.m4 plugin/config.h.in
touch configure */configure Makefile.in */Makefile.in
# Similarly we do not want to rebuild the documentation.
touch doc/annobin.info

%build
%configure --quiet --with-gcc-plugin-dir=%{ANNOBIN_PLUGIN_DIR}
%make_build

%install
%make_install
%{__rm} -f %{buildroot}%{_infodir}/dir

%if %{with tests}
%check
make check
%endif

%post
/sbin/install-info %{_infodir}/annobin.info.gz %{_infodir} >/dev/null 2>&1 || :
exit 0

%preun
if [ $1 = 0 ]; then
   /sbin/install-info --delete %{_infodir}/annobin.info.gz %{_infodir} >/dev/null 2>&1|| :
fi
exit 0

%files
%{ANNOBIN_PLUGIN_DIR}
%{_bindir}/built-by.sh
%{_bindir}/check-abi.sh
%{_bindir}/hardened.sh
%license COPYING3 LICENSE
%exclude %{_datadir}/doc/annobin-plugin/COPYING3
%exclude %{_datadir}/doc/annobin-plugin/LICENSE
%doc %{_datadir}/doc/annobin-plugin/annotation.proposal.txt
%doc %{_infodir}/annobin.info.gz

#---------------------------------------------------------------------------------

%changelog
* Fri Jan 26 2018 Nick Clifton <nickc@redhat.com> - 3.2-2
- Fix the installation of the annobin.info file.

* Fri Jan 26 2018 Nick Clifton <nickc@redhat.com> - 3.2-1
- Rebase on 3.2 release, which now contains documentation!

* Fri Jan 26 2018 Richard W.M. Jones <rjones@redhat.com> - 3.1-3
- Rebuild against GCC 7.3.1.

* Tue Jan 16 2018 Nick Clifton <nickc@redhat.com> - 3.1-2
- Add --with-gcc-plugin-dir option to the configure command line.

* Thu Jan 04 2018 Nick Clifton <nickc@redhat.com> - 3.1-1
- Rebase on version 3.1 sources.

* Mon Dec 11 2017 Nick Clifton <nickc@redhat.com> - 2.5.1-5
- Do not generate notes when there is no output file.  (#1523875)

* Fri Dec 08 2017 Nick Clifton <nickc@redhat.com> - 2.5.1-4
- Invent an input filename when reading from a pipe.  (#1523401)

* Thu Nov 30 2017 Florian Weimer <fweimer@redhat.com> - 2.5.1-3
- Use DECL_ASSEMBLER_NAME for symbol references (#1519165)

* Tue Oct 03 2017 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 2.5.1-2
- Cleanups in spec

* Tue Sep 26 2017 Nick Clifton <nickc@redhat.com> - 2.5.1-1
- Touch the auto-generated files in order to stop them from being regenerated.

* Tue Sep 26 2017 Nick Clifton <nickc@redhat.com> - 2.5-2
- Stop the plugin complaining about compiler datestamp mismatches.

* Thu Sep 21 2017 Nick Clifton <nickc@redhat.com> - 2.4-1
- Tweak tests so that they will run on older machines.

* Thu Sep 21 2017 Nick Clifton <nickc@redhat.com> - 2.3-1
- Add annobin-tests subpackage containing some preliminary tests.
- Remove link-time test for unsuported targets.

* Wed Aug 02 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Mon Jul 31 2017 Florian Weimer <fweimer@redhat.com> - 2.0-2
- Rebuild with binutils fix for ppc64le (#1475636)

* Wed Jun 28 2017 Nick Clifton <nickc@redhat.com> - 2.0-1
- Fixes for problems reported by the package submission review:
   * Add %%license entry to %%file section.
   * Update License and BuildRequires tags.
   * Add Requires tag.
   * Remove %%clean.
   * Add %%check.
   * Clean up the %%changelog.
- Update to use version 2 of the specification and sources.

* Thu May 11 2017 Nick Clifton <nickc@redhat.com> - 1.0-1
- Initial submission.
