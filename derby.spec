Name:                derby
Version:             10.13.1.1
Release:             1
Summary:             Relational database implemented entirely in Java
License:             ASL 2.0
URL:                 http://db.apache.org/derby/
Source0:             http://archive.apache.org/dist/db/derby/db-derby-%{version}/db-derby-%{version}-src.tar.gz
Source1:             derby-script
Source2:             derby.service
Patch1:              derby-javacc.patch
Patch2:              derby-lucene.patch

BuildRequires:       apache-parent javapackages-local glassfish-servlet-api jakarta-oro javacc
BuildRequires:       json_simple lucene4 junit ant systemd
Requires(pre):       shadow-utils
Requires(post):      systemd
Requires(preun):     systemd
Requires(postun):    systemd
BuildArch:           noarch

%description
Apache Derby, an Apache DB sub-project, is a relational database implemented
entirely in Java. Some key advantages include a small footprint, conformance
to Java, JDBC, and SQL standards and embedded JDBC driver.

%package javadoc
Summary:             API documentation for derby.

%description javadoc
%{summary}.

%prep
%setup -q -c
find -name '*.jar' -delete
find -name '*.class' -delete
pushd db-derby-%{version}-src
%patch1 -p0
%patch2 -p0
sed -i -e '/Class-Path/d' build.xml
sed -e 's/initjars,set-doclint,install_packagelists/initjars,set-doclint/' \
    -e '/<link offline/,+1d' \
    -i build.xml
ln -sf $(build-classpath oro) tools/java/jakarta-oro-2.0.8.jar
ln -sf $(build-classpath glassfish-servlet-api) tools/java/geronimo-spec-servlet-2.4-rc4.jar
ln -sf $(build-classpath javacc) tools/java/javacc.jar
ln -sf $(build-classpath json_simple) tools/java/json_simple-1.1.jar
ln -sf $(build-classpath junit) tools/java/junit.jar
ln -sf $(build-classpath lucene4/lucene-core-4) tools/java/lucene-core.jar
ln -sf $(build-classpath lucene4/lucene-analyzers-common-4) tools/java/lucene-analyzers-common.jar
ln -sf $(build-classpath lucene4/lucene-queryparser-4) tools/java/lucene-queryparser.jar
popd

%build
pushd db-derby-%{version}-src
ant buildsource buildjars javadoc
find maven2 -name pom.xml | xargs sed -i -e 's|ALPHA_VERSION|%{version}|'
%mvn_artifact maven2/pom.xml
for p in engine net client tools \
    derbyLocale_cs derbyLocale_de_DE derbyLocale_es derbyLocale_fr derbyLocale_hu \
    derbyLocale_it derbyLocale_ja_JP derbyLocale_ko_KR derbyLocale_pl derbyLocale_pt_BR \
    derbyLocale_ru derbyLocale_zh_CN derbyLocale_zh_TW ; do
  d=derby${p#derby}
  %mvn_artifact maven2/${p}/pom.xml jars/sane/${d%engine}.jar
done
popd

%install
pushd db-derby-%{version}-src
%mvn_install -J javadoc
install -d $RPM_BUILD_ROOT%{_bindir}
install -p -m755 %{SOURCE1} $RPM_BUILD_ROOT%{_bindir}/%{name}-ij
for P in sysinfo NetworkServerControl startNetworkServer stopNetworkServer
do
        ln $RPM_BUILD_ROOT%{_bindir}/%{name}-ij \
                $RPM_BUILD_ROOT%{_bindir}/%{name}-$P
done
mkdir -p $RPM_BUILD_ROOT%{_unitdir}
install -p -m 644 %{SOURCE2} \
        $RPM_BUILD_ROOT%{_unitdir}/%{name}.service
install -dm 755 $RPM_BUILD_ROOT/var/lib/derby
popd

%pre
getent group derby >/dev/null || groupadd -r derby
getent passwd derby >/dev/null || \
    useradd -r -g derby -d /var/lib/derby -s /sbin/nologin \
    -c "Apache Derby service account" derby
exit 0

%post
%systemd_post derby.service

%preun
%systemd_preun derby.service

%postun
%systemd_postun_with_restart derby.service

%files -f  db-derby-%{version}-src/.mfiles
%{_bindir}/*
%doc db-%{name}-%{version}-src/published_api_overview.html
%doc db-%{name}-%{version}-src/RELEASE-NOTES.html
%doc db-%{name}-%{version}-src/README
%{_unitdir}/%{name}.service
%attr(755,derby,derby) %{_sharedstatedir}/%{name}
%license db-derby-%{version}-src/LICENSE
%license db-derby-%{version}-src/NOTICE

%files javadoc -f db-derby-%{version}-src/.mfiles-javadoc
%license db-derby-%{version}-src/LICENSE
%license db-derby-%{version}-src/NOTICE

%changelog
* Thu Jul 30 2020 leiju <leiju4@huawei.com> - 10.13.1.1-1
- Package init
