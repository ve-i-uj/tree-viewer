#!/bin/bash
# 
# Обновить конфиг с переменными окружения
#

# "импорт"
curr_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
echo `realpath $curr_dir/init.sh`
source `realpath "$curr_dir/init.sh"`

USAGE="Use 'dev' or 'prod' in the first argument (without quotes). Examples:\n\nbash $0 dev\nbash $0 prod\n"
EXAMPLE_DIR=$curr_dir/examples

# проверка, что есть аргумент
if [ -z "$1" ]
    then
        echo -e $USAGE
        exit
fi

# проверка, что это подходящий аргумент.
# и выставить подходящее окончение заготовок конфигов
if [ $1 == dev ]
	then 
		SETTINGS_ENV=dev
elif [ $1 == prod ]
    then
		SETTINGS_ENV=prod
else
	echo -e $USAGE
	exit 1
fi

cp "$CONFIG_DIR/docker.$1.env" $PROJ_DIR/.env

echo "Done!"
