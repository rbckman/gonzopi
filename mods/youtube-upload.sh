#!/bin/sh
# YOUTUBE-UPLOAD MOD
# $1 filmtitle
# $2 filename
PATH=`pwd`

printf "\033c"

/bin/cat <<'EOF'     

                             _                          _                 _ 
                   _        | |                        | |               | |
 _   _  ___  _   _| |_ _   _| | _   ____    _   _ ____ | | ___   ____  _ | |
| | | |/ _ \| | | |  _) | | | || \ / _  )  | | | |  _ \| |/ _ \ / _  |/ || |
| |_| | |_| | |_| | |_| |_| | |_) | (/ /   | |_| | | | | | |_| ( ( | ( (_| |
 \__  |\___/ \____|\___)____|____/ \____)   \____| ||_/|_|\___/ \_||_|\____|
(____/                                           |_|                        
    

EOF
read -p "Youtube film title: " title
read -p "Film description: " description


while true; do
    read -p 'Do you want your video public (y)es (n)o?:' yn
    case $yn in
        [Yy]* ) privacy='public' ; break ;;
        [Nn]* ) privacy='private'; break;;
        * ) echo "Please answer yes or no.";;
    esac
done

while true; do
    echo "Do you want to upload video $title with description $description to a $privacy Youtube video?"
    read -p 'Is this correct (y)es (n)o?:' yn
    case $yn in
        [Yy]* ) echo "OK!" ; break ;;
        [Nn]* ) echo "NOPE!" ; exit;;
        * ) echo "Please answer yes or no.";;
    esac
done

/usr/bin/python3 $PATH/mods/youtube-upload/youtube_upload/__main__.py --title="$title" --description="$description" --privacy="$privacy" $2
