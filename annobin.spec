Name:    annobin
Summary: Binary annotation plugin for GCC
Version: 2.3
Release: 1%{?dist}

License: GPLv3, MIT/X11 (config/libcutl.m4, install-sh)
Group:   Development/Tools
URL:     https://fedoraproject.org/wiki/Toolchain/Watermark

# Use "--without tests" to disable the testsuite.  The default is to run them.
%bcond_without tests

#---------------------------------------------------------------------------------
Source:  https://nickc.fedorapeople.org/annobin-%{version}.tar.lz

# This is a gcc plugin, hence gcc is required.
Requires: gcc

BuildRequires: gcc-plugin-devel pkgconfig

%description
A plugin for GCC that records extra information in the files that it compiles.
This information can be used to analyze the files, and provide the loader
with extra information about the requirements of the loaded file.

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

%build
%configure --quiet
make %{?_smp_mflags}

%if %{with tests}
make check
%endif

%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT

%files
%{ANNOBIN_PLUGIN_DIR}
%{_bindir}/built-by.sh
%{_bindir}/check-abi.sh
%{_bindir}/hardened.sh
%license COPYING3 LICENSE
%exclude %{_datadir}/doc/annobin-plugin/COPYING3
%exclude %{_datadir}/doc/annobin-plugin/LICENSE
%doc %{_datadir}/doc/annobin-plugin/annotation.proposal.txt

#---------------------------------------------------------------------------------

%changelog
* Thu Sep 21 2017 Nick Clifton <nickc@redhat.com> - annobin-2.3-1
- Add annobin-tests subpackage containing some preliminary tests.
- Remove link-time test for unsuported targets.

* Wed Aug 02 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Mon Jul 31 2017 Florian Weimer <fweimer@redhat.com> - 2.0-2
- Rebuild with binutils fix for ppc64le (#1475636)

* Wed Jun 28 2017 Nick Clifton <nickc@redhat.com> - annobin-2.0-1.fc25
- Fixes for problems reported by the package submission review:
   * Add %%license entry to %%file section.
   * Update License and BuildRequires tags.
   * Add Requires tag.
   * Remove %%clean.
   * Add %%check.
   * Clean up the %%changelog.
- Update to use version 2 of the specification and sources.

* Thu May 11 2017 Nick Clifton <nickc@redhat.com> - annobin-1.0-1
- Initial submission.
