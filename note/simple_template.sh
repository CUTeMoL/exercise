#!/bin/bash
mkdir /usr/local/pgsql
./configure \
    --prefix='/usr/local/pgsql' \
    --with-systemd \
    --enable-nls \
    --with-perl \
    --with-python \
    --with-tcl \
    --with-llvm \
    --with-lz4 \
    --with-zstd \
    --with-openssl \
    --with-gssapi \
    --with-ldap \
    --with-pam \
    --with-libxml \
    --with-libxslt \
    --with-uuid=e2fs \
   XML2_CONFIG="/usr/bin/xml2-config"
make
make all
make install 
adduser postgres
mkdir -p /usr/local/pgsql/data
chown postgres /usr/local/pgsql/data
su postgres -c "/usr/local/pgsql/bin/initdb -D /usr/local/pgsql/data"
cp postgresql.service /etc/systemd/system/postgresql.service
