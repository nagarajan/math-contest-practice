cd ~/dev/math-contest-practice
git pull
echo "Pulled latest changes"
mkdir -p /var/www/motleytech/html/apps
rm -rf /var/www/motleytech/html/apps/math
cp -r dist /var/www/motleytech/html/apps/math
echo "Copied dist to /var/www/motleytech/html/apps/math"
echo "Done"
