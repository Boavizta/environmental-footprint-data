#!/bin/bash

if [ $(uname -s) == "Darwin" ]
then
    chrome_cmd='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
else
    chrome_cmd="google-chrome"
fi

echo "Workstations"
for line in $("$chrome_cmd" --headless --dump-dom --virtual-time-budget=10000 --timeout=10000 --run-all-compositor-stages-before-draw --disable-gpu --user-agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36" 'https://www.dell.com/fr-fr/dt/corporate/social-impact/advancing-sustainability/sustainable-products-and-services/product-carbon-footprints.htm#tab0=0' | grep -E '<a data-iframe' | sed -E 's/\<a data\-iframe\=\"(http\:)*(.*\.pdf)\s*\" href.*/https\:\2/g');
do 
    if ( grep -q $(echo $line | sed -E 's/.*\/([^\/]*\.pdf)/\1/g') ../../boavizta-data-us.csv ) || ( grep -q $(echo $line | sed -E 's/.*\/([^\/]*\.pdf)/\1/g') url_blacklist )
    then
        :
    else
        PYTHONPATH=../../ python3 ../parsers/dell_standalone.py -s $line  
    fi
done

echo "Laptops"
for line in $("$chrome_cmd" --headless --dump-dom --virtual-time-budget=10000 --timeout=10000 --run-all-compositor-stages-before-draw --disable-gpu --user-agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36" 'https://www.dell.com/fr-fr/dt/corporate/social-impact/advancing-sustainability/sustainable-products-and-services/product-carbon-footprints.htm#tab0=1' | grep -E '<a data-iframe' | sed -E 's/\<a data\-iframe\=\"(http\:)*(.*\.pdf)\s*\" href.*/https\:\2/g');
do 
    if ( grep -q $(echo $line | sed -E 's/.*\/([^\/]*\.pdf)/\1/g') ../../boavizta-data-us.csv ) || ( grep -q $(echo $line | sed -E 's/.*\/([^\/]*\.pdf)/\1/g') url_blacklist )
    then
        :
    else
        PYTHONPATH=../../ python3 ../parsers/dell_standalone.py -s $line  
    fi
done

echo "Monitors"
for line in $("$chrome_cmd" --headless --dump-dom --virtual-time-budget=10000 --timeout=10000 --run-all-compositor-stages-before-draw --disable-gpu --user-agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36" 'https://www.dell.com/fr-fr/dt/corporate/social-impact/advancing-sustainability/sustainable-products-and-services/product-carbon-footprints.htm#tab0=2' | grep -E '<a data-iframe' | sed -E 's/\<a data\-iframe\=\"(http\:)*(.*\.pdf)\s*\" href.*/https\:\2/g');
do 
    if ( grep -q $(echo $line | sed -E 's/.*\/([^\/]*\.pdf)/\1/g') ../../boavizta-data-us.csv ) || ( grep -q $(echo $line | sed -E 's/.*\/([^\/]*\.pdf)/\1/g') url_blacklist )
    then
        :
    else
        PYTHONPATH=../../ python3 ../parsers/dell_standalone.py -s $line  
    fi
done

echo "Servers"
for line in $("$chrome_cmd" --headless --dump-dom --virtual-time-budget=10000 --timeout=10000 --run-all-compositor-stages-before-draw --disable-gpu --user-agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36" 'https://www.dell.com/fr-fr/dt/corporate/social-impact/advancing-sustainability/sustainable-products-and-services/product-carbon-footprints.htm#tab0=3' | grep -E '<a data-iframe' | sed -E 's/\<a data\-iframe\=\"(http\:)*(.*\.pdf)\s*\" href.*/https\:\2/g');
do 
    if ( grep -q $(echo $line | sed -E 's/.*\/([^\/]*\.pdf)/\1/g') ../../boavizta-data-us.csv ) || ( grep -q $(echo $line | sed -E 's/.*\/([^\/]*\.pdf)/\1/g') url_blacklist )
    then
        :
    else
        PYTHONPATH=../../ python3 ../parsers/dell_standalone.py -s $line  
    fi
done

echo "Thin clients"
for line in $("$chrome_cmd" --headless --dump-dom --virtual-time-budget=10000 --timeout=10000 --run-all-compositor-stages-before-draw --disable-gpu --user-agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36" 'https://www.dell.com/fr-fr/dt/corporate/social-impact/advancing-sustainability/sustainable-products-and-services/product-carbon-footprints.htm#tab0=5' | grep -E '<a data-iframe' | sed -E 's/\<a data\-iframe\=\"(http\:)*(.*\.pdf)\s*\" href.*/https\:\2/g');
do 
    if ( grep -q $(echo $line | sed -E 's/.*\/([^\/]*\.pdf)/\1/g') ../../boavizta-data-us.csv ) || ( grep -q $(echo $line | sed -E 's/.*\/([^\/]*\.pdf)/\1/g') url_blacklist )
    then
        :
    else
        PYTHONPATH=../../ python3 ../parsers/dell_standalone.py -s $line  
    fi
done

