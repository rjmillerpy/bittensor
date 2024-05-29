# The MIT License (MIT)
# Copyright © 2021 Yuma Rao

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the “Software”), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import sys
import argparse
import bittensor
from rich.prompt import Prompt, Confirm
from .utils import check_netuid_set, check_for_cuda_reg_config
from copy import deepcopy

from . import defaults

console = bittensor.__console__

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)


class AppraiseCommand:
    """
    Executes the ``register`` command to register a neuron on the Bittensor network by recycling some TAO (the network's native token).

    This command is used to add a new neuron to a specified subnet within the network, contributing to the decentralization and robustness of Bittensor.

    Usage:
        Before registering, the command checks if the specified subnet exists and whether the user's balance is sufficient to cover the registration cost.

        The registration cost is determined by the current recycle amount for the specified subnet. If the balance is insufficient or the subnet does not exist, the command will exit with an appropriate error message.

        If the preconditions are met, and the user confirms the transaction (if ``no_prompt`` is not set), the command proceeds to register the neuron by recycling the required amount of TAO.

    The command structure includes:

    - Verification of subnet existence.
    - Checking the user's balance against the current recycle amount for the subnet.
    - User confirmation prompt for proceeding with registration.
    - Execution of the registration process.

    Columns Displayed in the confirmation prompt:

    - Balance: The current balance of the user's wallet in TAO.
    - Cost to Register: The required amount of TAO needed to register on the specified subnet.

    Example usage::

        btcli subnets register --netuid 1

    Note:
        This command is critical for users who wish to contribute a new neuron to the network. It requires careful consideration of the subnet selection and an understanding of the registration costs. Users should ensure their wallet is sufficiently funded before attempting to register a neuron.
    """

    @staticmethod
    def run(cli: "bittensor.cli"):
        r"""Register neuron by recycling some TAO."""
        try:
            config = cli.config.copy()
            subtensor: "bittensor.subtensor" = bittensor.subtensor(
                config=config, log_verbose=False
            )
            AppraiseCommand._run(cli, subtensor)
        finally:
            if "subtensor" in locals():
                subtensor.close()
                bittensor.logging.debug("closing subtensor connection")

    @staticmethod
    def _run(cli: "bittensor.cli", subtensor: "bittensor.subtensor"):
        if not cli.config.netuid:
            bittensor.__console__.print(
                f"[red]Please enter netuid[/red]"
            )
            sys.exit(1)

        netuid = cli.config.netuid
        if not subtensor.subnet_exists(netuid=netuid):
            bittensor.__console__.print(
                f"[red]Subnet {netuid} does not exist[/red]"
            )
            sys.exit(1)

        # Check current recycle amount
        current_recycle = subtensor.recycle(netuid=netuid)

        bittensor.__console__.print(
            f"Current recycle for subnet {netuid} is {current_recycle} TAO"
        )
        sys.exit(1)

    @staticmethod
    def add_args(parser: argparse.ArgumentParser):
        appraise_parser = parser.add_parser(
            "appraise", help="""Appraises cost to register to network."""
        )
        appraise_parser.add_argument(
            "--netuid",
            type=int,
            help="netuid for subnet to serve this neuron on",
            default=None,
        )

        bittensor.wallet.add_args(appraise_parser)
        bittensor.subtensor.add_args(appraise_parser)

    @staticmethod
    def check_config(config: "bittensor.config"):
        if (
            not config.is_set("subtensor.network")
            and not config.is_set("subtensor.chain_endpoint")
            and not config.no_prompt
        ):
            config.subtensor.network = Prompt.ask(
                "Enter subtensor network",
                choices=bittensor.__networks__,
                default=defaults.subtensor.network,
            )
            _, endpoint = bittensor.subtensor.determine_chain_endpoint_and_network(
                config.subtensor.network
            )
            config.subtensor.chain_endpoint = endpoint

        check_netuid_set(
            config, subtensor=bittensor.subtensor(config=config, log_verbose=False)
        )

        if not config.is_set("wallet.name") and not config.no_prompt:
            wallet_name = Prompt.ask("Enter wallet name", default=defaults.wallet.name)
            config.wallet.name = str(wallet_name)

        if not config.is_set("wallet.hotkey") and not config.no_prompt:
            hotkey = Prompt.ask("Enter hotkey name", default=defaults.wallet.hotkey)
            config.wallet.hotkey = str(hotkey)
