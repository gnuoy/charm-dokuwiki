#!/usr/bin/env python3
# Copyright 2021 Ubuntu
# See LICENSE file for licensing details.
#
# Learn more at: https://juju.is/docs/sdk

"""Charm the service.

Refer to the following post for a quick-start guide that will help you
develop a new k8s charm using the Operator Framework:

    https://discourse.charmhub.io/t/4208
"""

from jinja2 import Environment, BaseLoader, meta
import logging
import yaml

import ops
from ops.charm import CharmBase
from ops.main import main
from ops.framework import StoredState
from ops.model import ActiveStatus

logger = logging.getLogger(__name__)


class DokuwikiCharm(CharmBase):
    """Charm the service."""

    _stored = StoredState()

    def __init__(self, *args):
        super().__init__(*args)
        self.framework.observe(self.on.install, self._on_install)
        self.framework.observe(self.on.upgrade_charm, self._on_config_changed)
        self.framework.observe(self.on.config_changed, self._on_config_changed)
        self.framework.observe(self.on.fortune_action, self._on_fortune_action)
        self.framework.observe(self.on.dokuwiki_pebble_ready, self._on_dokuwiki_pebble_ready)
        self._stored.set_default(things=[])

    def _on_install(self, _):
        """Perform any install steps and report status."""
        # Learn more about statuses in the SDK docs:
        # https://juju.is/docs/sdk/constructs#heading--statuses
        self.unit.status = ActiveStatus()

    def _on_config_changed(self, event: ops.framework.EventBase) -> None:
        """Just an example to show how to deal with changed configuration.

        TEMPLATE-TODO: change this example to suit your needs.
        If you don't need to handle config, you can remove this method,
        the hook created in __init__.py for it, the corresponding test,
        and the config.py file.

        Learn more about config at https://juju.is/docs/sdk/config
        """
        self._update_files(event)

    def _on_fortune_action(self, event):
        """Just an example to show how to receive actions.

        TEMPLATE-TODO: change this example to suit your needs.
        If you don't need to handle actions, you can remove this method,
        the hook created in __init__.py for it, the corresponding test,
        and the actions.py file.

        Learn more about actions at https://juju.is/docs/sdk/actions
        """
        fail = event.params["fail"]
        if fail:
            event.fail(fail)
        else:
            event.set_results({"fortune": "A bug in the code is worth two in the documentation."})

    def _update_files(self, event):
        container = self.unit.get_container("dokuwiki")
        wikiname = self.config["wiki-name"]
        local_php_template = """<?php
/**
 * Dokuwiki's Main Configuration File - Local Settings
 * Auto-generated by install script
 * Date: Wed, 28 Apr 2021 19:01:59 +0000
 */
$conf['title'] = '{wikiname}';
$conf['lang'] = 'en';
$conf['license'] = 'cc-by-sa';
$conf['useacl'] = 1;
$conf['superuser'] = '@admin';
$conf['disableactions'] = 'register';
"""
        ctxt = {
            'wikiname': self.config["wiki-name"]}
        logger.info("Pushing new local.php")
        container.push("/var/www/dokuwiki/conf/local.php", local_php_template.format(**ctxt))

    def _on_dokuwiki_pebble_ready(self, event: ops.framework.EventBase) -> None:
        """Handle the workload ready event."""
        #self._stored.gunicorn_pebble_ready = True

        #pebble_config = self._get_pebble_config(event)
        #if not pebble_config:
        #    # Charm will be in blocked status.
        #    return
        pebble_config = {
            "summary": "dokuwiki layer",
            "description": "dokuwiki layer",
            "services": {
                "gunicorn": {
                    "override": "replace",
                    "summary": "dokuwiki service",
                    "command": "/usr/sbin/apachectl -D FOREGROUND",
                    "startup": "enabled",
                }
            },
        }

        container = event.workload
        logger.debug("About to add_layer with pebble_config:\n{}".format(yaml.dump(pebble_config)))
        # `container.add_layer` accepts str (YAML) or dict or pebble.Layer
        # object directly.
        container.add_layer("dokuwiki", pebble_config)
        # Start the container and set status.
        container.autostart()
        self.unit.status = ActiveStatus()

    def _render_template(self, tmpl: str, ctx: dict) -> str:
        """Render a Jinja2 template

        :returns: A rendered Jinja2 template
        """
        j2env = Environment(loader=BaseLoader())
        j2template = j2env.from_string(tmpl)

        return j2template.render(**ctx)


if __name__ == "__main__":
    main(DokuwikiCharm)
