#!/bin/bash
set -e
set -o pipefail

waiting_services() {
  if [ -n "${SQL_HOST}" ]
  then
      echo "Waiting for SQL..."

      while ! nc -z $SQL_HOST $SQL_PORT; do
        sleep 0.1
      done

      echo "PostgreSQL started"
  fi
}

initial_setup() {
  echo "Loading fixtures"
  python manage.py loaddata */fixtures/*.json

  echo "Creating default users"
  python manage.py createdefaultusers
}

migrate_database() {
  COUNT=$(python manage.py showmigrations -p | grep [X] || true | wc -l)
  if [[ -z ${COUNT} || ${COUNT} -eq 0 ]]; then
    echo "Setting up RestAPI for firstrun. Please be patient, this could take a while..."
    python manage.py migrate
    initial_setup
  fi
  echo "Running migrating scripts"
  python manage.py migrate
}

case ${1} in
  app:init|app:start|app:sanitize)
    waiting_services

    sleep 5

    case ${1} in
      app:start)
        migrate_database
        ;;
      app:init)
        migrate_database
        initial_setup
        ;;
    esac
    ;;
  app:help)
    echo "Available options:"
    echo " app:start        - Starts the django server (default)"
    echo " app:init         - Initialize the django (e.g. create databases, compile assets), but don't start it."
    echo " app:flush        - Flush everything."
    echo " app:help         - Displays the help"
    echo " [command]        - Execute the specified command, eg. bash."
    ;;
  *)
    exec "$@"
    ;;
esac