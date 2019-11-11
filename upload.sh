echo "======== Uploading repo to Github ======== "
git push
echo "======== Refreshing the website ======== "
cd bin && python3 vallenato_fr.py --website
echo "======== Uploading the website ======== "
cd ../website/prod && rsync -av --delete -e 'ssh -p 21324' ./* e2jk@pascal.klein.st:/var/www/html/vallenato.fr
