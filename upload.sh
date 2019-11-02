echo "======== Uploading repo to Github ======== "
git push
echo "======== Uploading /aprender ======== "
cd aprender && rsync -av --delete -e 'ssh -p 21324' --exclude=temp/ ./* e2jk@pascal.klein.st:/var/www/html/vallenato.fr/aprender
echo "======== Uploading www ======== "
cd ../website/prod && rsync -av --delete -e 'ssh -p 21324' ./* e2jk@pascal.klein.st:/var/www/html/vallenato.fr
