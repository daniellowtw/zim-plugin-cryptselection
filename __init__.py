# Copyright 2015 Daniel Low <github.com/daniellowtw>
# License:  same as zim (gpl)
#
# Changes: 
# * Mainly to make it work on Windows
# * Toggle between decrypted and encrypted text
# * Preference asks for path and public key to encrypt under


# -*- coding: utf-8 -*-
# cryptselection plugin for zim
#
# Copyright 2015 Klaus Holler <kho@gmx.at>
# License:  same as zim (gpl)
#
# Installation/Usage:
# * Put the cryptselection/ directory to your ~/.local/share/zim/plugins subdirectory
#   i.e. cd ~/.local/share/zim/plugins &&
#        git clone https://github.com/k3ho/zim-plugin-cryptselection.git cryptselection
# * Then (re)start zim, and setup once the 'Crypt Selection' plugin:
#   * enable it in Edit>Preferences>Plugins and
#   * set the encryption/decryption commands via 'Configure' button
# * For in-place decryption gpg-agent should be started before starting zim and be
#   configured properly to display a pinentry popup to ask for the PGP key passphrase.

from __future__ import with_statement

import gtk
import re
from subprocess import Popen, PIPE

from zim.plugins import PluginClass, extends, WindowExtension
from zim.actions import action
from zim.gui.widgets import ui_environment, MessageDialog

import logging

logger = logging.getLogger('zim.plugins.cryptselection')


class CryptSelectionPlugin(PluginClass):

    plugin_info = {
        'name': _('Crypt Selection'), # T: plugin name
        'description': _('''\
This plugin encrypts or decrypts the current selection 
with a specified encryption command (e.g. gpg).
If -----BEGIN PGP MESSAGE----- is found at selection
start and -----END PGP MESSAGE----- found at selection
end then decrypt, otherwise encrypt.
'''), # T: plugin description
        'author': 'Klaus Holler, Daniel Low',
        'help': 'Plugins:Crypt Selection',
    }

    plugin_preferences = [
        # key, type, label, default
        ('GPG_path', 'string',_('GPG path'),'"C:\\Program Files (x86)\\GNU\\GnuPG\\pub\\gpg.exe"'), # T: plugin preference
        ('RECIPIENT', 'string', _("The public key to use"), 'Your email address')
    ]


@extends('MainWindow')
class MainWindowExtension(WindowExtension):

    uimanager_xml = '''
    <ui>
        <menubar name='menubar'>
            <menu action='edit_menu'>
                <placeholder name='plugin_items'>
                    <menuitem action='crypt_selection'/>
                </placeholder>
            </menu>
        </menubar>
    </ui>
    '''

    def __init__(self, plugin, window):
        WindowExtension.__init__(self, plugin, window)
        self.preferences = plugin.preferences

    @action(_('Crypt selection')) # T: menu item
    # TODO: add stock parameter to set icon
    def crypt_selection(self):
        buffer = self.window.pageview.view.get_buffer()
        try:
            sel_start, sel_end = buffer.get_selection_bounds()
        except ValueError:
            MessageDialog(self.window.ui,
                _('Please select the text to be encrypted, first.')).run()
                # T: Error message in "crypt selection" dialog, %s will be replaced
                # by application name
            return

        first_lineno = sel_start.get_line()
        last_lineno = sel_end.get_line()

        with buffer.user_action:
            assert buffer.get_has_selection(), 'No Selection present'
            sel_text = self.window.pageview.get_selection(format='wiki')
            self_bounds = (sel_start.get_offset(), sel_end.get_offset())
            if ((re.match(r'[\n\s]*\-{5}BEGIN PGP MESSAGE\-{5}', sel_text) is None) or
                re.search(r'\s*\-{5}END PGP MESSAGE\-{5}[\n\s]*$', sel_text) is None):
                # default is encryption:
                encrypt = True
                cryptcmd = self.preferences['GPG_path'] + " --always-trust -ear " + self.preferences['RECIPIENT']
            else:
                # on-the-fly decryption if selection is a full PGP encrypted block
                encrypt = False
                cryptcmd = self.preferences['GPG_path'] + " -d"
            newtext = None
            p = Popen("".join(cryptcmd), stdin=PIPE, stdout=PIPE)
            newtext, err = p.communicate(input=sel_text)
            if p.returncode == 0:
                # replace selection only if crypt command was successful
                # (incidated by returncode 0)
                bounds = map(buffer.get_iter_at_offset, self_bounds)
                buffer.delete(*bounds)
                buffer.insert_at_cursor("\n%s\n" % newtext)
            else:
                logger.warn("crypt command '%s' returned code %d." % (cryptcmd,
                            p.returncode))
