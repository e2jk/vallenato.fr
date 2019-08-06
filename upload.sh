git push && cd aprender && rsync -av --delete -e 'ssh -p 21324' --exclude=temp/ ./* e2jk@pascal.klein.st:/var/www/html/vallenato.fr/aprender
