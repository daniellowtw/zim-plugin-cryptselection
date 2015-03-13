zim-plugin-cryptselection
=========================

A plugin for Zim-Wiki_ which encrypts the current selection, replacing plaintext 
in a ZIM page by its encrypted representation. 

If a complete -----BEGIN PGP MESSAGE----- ... -----END PGP MESSAGE----- block is
selected then decrypt the block. For that to work the passphrase of the required
secret key has to be provided via a pinentry popup, i.e. the gpg-agent has to be
started before zim and has to be configured to display a pinentry popup.

# Instructions

Please view the original author's page for other info.

This fork mainly deals with 

* Setting the default to work in Windows
* Toggle between plaintext and ciphertext
* Changed the preferences to ask for default public key to use and path to gpg.

## Requirements

* Have a RSA key established

# Installation

On Windows machine, you will need to use the source code instead of the binary. (I am not sure how to install plugins for the binary version.)

browse to zim/plugins and `git clone https://github.com/daniellowtw/zim-plugin-cryptselection.git cryptselection`

Zim plugin written by Klaus Holler and modified by Daniel Low
