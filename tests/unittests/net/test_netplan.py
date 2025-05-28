import os
from unittest import mock

import pytest
import yaml

from cloudinit import util
from cloudinit.net import netplan, network_state

from cloudinit import lifecycle



@pytest.fixture
def renderer(tmp_path):
    config = {
        "netplan_path": str(tmp_path / "netplan/50-cloud-init.yaml"),
        "postcmds": True,
    }
    yield netplan.Renderer(config)


class TestNetplanRenderer:
    @pytest.mark.parametrize(
        "orig_config", ["", "{'orig_cfg': true}", "{'new_cfg': true}"]
    )
    def test_skip_netplan_generate(self, renderer, orig_config, mocker):
        """Check `netplan generate` called when netplan config has changed."""
        header = "\n"
        new_config = "{'new_cfg': true}"
        renderer_mocks = mocker.patch.multiple(
            renderer,
            _render_content=mocker.Mock(return_value=new_config),
            _netplan_generate=mocker.DEFAULT,
            _net_setup_link=mocker.DEFAULT,
        )
        if orig_config:
            util.ensure_dir(os.path.dirname(renderer.netplan_path))
            with open(renderer.netplan_path, "w") as f:
                f.write(header)
                f.write(orig_config)
        renderer.render_network_state(mocker.Mock())
        config_changed = bool(orig_config != new_config)
        assert renderer_mocks["_netplan_generate"].call_args_list == [
            mock.call(run=True, config_changed=config_changed)
        ]


V2_CONFIG_MTU = """\
network:
  version: 2
  ethernets:
    eth0:
      match:
        macaddress: "00:11:22:33:44:55"
      nameservers:
        addresses:
        - 8.8.8.8
        search:
        - spam.local
        - eggs.local
      mtu: 0
    eth1:
      match:
        macaddress: "66:77:88:99:00:11"
      nameservers:
        addresses:
        - 4.4.4.4
        search:
        - foo.local
        - bar.local
      set-name: "ens92"
      mtu: 1
"""

class TestNetworkStateParseMTU:
    def _parse_network_state_from_config(self, config):
        with mock.patch("cloudinit.net.network_state.get_interfaces_by_mac"):
            config = yaml.safe_load(config)
            return network_state.parse_net_config_data(config["network"])

    @pytest.mark.allow_all_subp
    def test_netplan_mtu(self, renderer, caplog):
        ns = self._parse_network_state_from_config(V2_CONFIG_MTU)
        assert ns != None

        config = {
            "netplan_path": str("/tmp/50-cloud-init.yaml"),
            "postcmds": False,
        }

        if os.path.exists(config["netplan_path"]):
            os.remove(config["netplan_path"])

        renderer = netplan.Renderer(config=config)
        renderer.render_network_state(ns)

        import shutil
        shutil.copyfile(netplan.CLOUDINIT_NETPLAN_FILE, config["netplan_path"])

        assert "Using netplan python module" in caplog.text

        with open(config["netplan_path"], "r") as file:
            content = file.read()
        assert content == V2_CONFIG_MTU 


class TestNetplanAPIWriteYAMLFile:
    def test_no_netplan_python_api(self, caplog):
        """Skip when no netplan available."""
        with mock.patch("builtins.__import__", side_effect=ImportError):
            netplan.netplan_api_write_yaml_file("network: {version: 2}")
        assert (
            "No netplan python module. Fallback to write"
            f" {netplan.CLOUDINIT_NETPLAN_FILE}" in caplog.text
        )
