git push && rsync -av -e 'ssh -p 21324' --exclude=temp/ --exclude=upload.sh ./* e2jk@pascal.klein.st:/var/www/html/vallenato.fr/aprender
