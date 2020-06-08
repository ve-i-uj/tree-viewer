#!/bin/bash
# wait-for-postgres.sh

# "импорт"
curr_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
echo `realpath $curr_dir/init.sh`
source `realpath "$curr_dir/init.sh"`


set -e
  
host="$1"
shift
cmd="$@"

# переменный окружения
source $PROJ_DIR/.env

until PGPASSWORD=$PG_PWD psql -h "$host" -U $PG_USER -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done
  
>&2 echo "Postgres is up - executing command"
exec $cmd
