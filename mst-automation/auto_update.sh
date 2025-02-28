# 0 */4 * * * /home/prabesh/proj/icpmap/mst-automation/auto_update.sh

SCRIPT_DIR="$(dirname "$(realpath "${BASH_SOURCE[0]}")")"

source "$SCRIPT_DIR/../.venv/bin/activate"
python "$SCRIPT_DIR/files_download.py"

cd "$SCRIPT_DIR/mst"
git add .; git commit -m "y2 auto update"; git push;
