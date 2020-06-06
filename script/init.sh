# Пути до прокта и его папок

SERVICE_NAME="tree-viewer"

curr_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
PROJ_DIR=`realpath $curr_dir/..`
CONFIG_DIR="$PROJ_DIR/config"

echo
echo "### SERVICE_NAME=$SERVICE_NAME ###"
echo
echo "Directories:"
echo
echo "PROJ_DIR=$PROJ_DIR"
echo "CONFIG_DIR=$CONFIG_DIR"
echo
echo "#######"
echo
