mkdir /home/richou/.var/app/com.nyaker.RyzenTuningUtility
cp -f -r * /home/richou/.var/app/com.nyaker.RyzenTuningUtility
cp -f RyzenTuningController.desktop /home/richou/.local/share/applications
echo installing libs
pip install PyGObject

echo installing icon
sudo cp -f com.nyaker.RyzenTuningUtility.svg /usr/share/icons/hicolor/scalable/apps
