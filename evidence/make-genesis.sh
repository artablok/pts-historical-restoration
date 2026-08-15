#!/bin/sh

if [ $# != 2 ]; then
    echo "Usage: $0 <init-delegates.json> <snapshot.json.gz>"
    exit 1
fi

exec >"`dirname $0`/../../../libraries/blockchain/genesis.json"

echo "{"
ts="`zcat "$2" | cut -d, -f 2 | cut -d: -f 2`"
echo '"timestamp" : "'`date -d @$ts +%Y%m%dT%H%M%S`'",'
echo '"market_assets": [ ],'
echo '"names": ['
cat `dirname $0`/names.json $1 | \
  grep '"name"' | \
  sed 's=",=",\
	=g;s={= {\
	=g;s=}=\
 }=g;s=:=: =g'
echo '],'
zcat "$2" | sed 's=^.*"balances="balances=;s=,"moneysupply".*==' | \
  sed 's=",=",\
	=g;s=\[= [\
	=g;s=],=\
 ],\
=g'
echo '}'

