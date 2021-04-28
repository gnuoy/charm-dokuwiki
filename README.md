# dokuwiki

## Build

To build:

    git clone https://github.com/gnuoy/charm-dokuwiki.git
    cd charm-dokuwiki/
    charmcraft build

## Usage

Run it like so:

    juju deploy ./dokuwiki.charm --resource dokuwiki-image=gnuoy/dokuwiki-test

The name of the wiki can be changed via the wiki-name charm config option:

    juju config dokuwiki wiki-name="SuperSecretWiki"
