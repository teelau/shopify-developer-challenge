#!/bin/sh
#wait until MySQL is available
maxcounter=45

counter=1
until echo '\q' | mysql -h"$MYSQL_HOST" -P"$MYSQL_PORT" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" $MYSQL_DATABASE; do
    >&2 echo "MySQL is unavailable - sleeping"
    counter=`expr $counter + 1`
    if [ $counter -gt $maxcounter ]; then
        >&2 echo "We have been waiting for MySQL too long already; failing."
        exit 1
    fi;
    sleep 1
done

echo 'MySQL is Available'