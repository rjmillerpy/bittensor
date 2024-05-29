import subprocess
import re


def remove_ansi_sequences(text):
    ansi_escape = re.compile(r'\x1b\[([0-9]+)(;[0-9]+)*m')
    return ansi_escape.sub('', text)


def get_recycle_amount(netuid=20):
    command = ['btcli', 's', 'appraise', '--netuid', str(netuid), '--subtensor.network', 'finney', '--wallet.name', 'default', '--wallet.hotkey', 'default']
    try:
        # Execute the command and capture the output with a timeout
        result = subprocess.run(command, capture_output=True, text=True, timeout=200)

        # Get the standard output from the result and clean up ANSI sequences
        cli_output = result.stdout
        clean_output = remove_ansi_sequences(cli_output)
        recycle_cost_str = clean_output.split('τ')[-1].split()[0]  # Split on 'τ' and take the first token of the result

        # Convert the extracted string to float
        recycle_cost = float(recycle_cost_str)
        return recycle_cost

    except subprocess.TimeoutExpired:
        print("Command timed out")
    except ValueError as ve:
        print(f"Could not convert string to float: {ve}")
    except Exception as e:
        print(f"An error occurred: {e}")


