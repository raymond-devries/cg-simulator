from typing import Optional

from dask import bag as dask_bag
from dask.distributed import Client
from rich.progress import track

from accordion_simulator.core import SimulatorCore, console


def run_simulation(
    print_game: bool = False,
    interactive: bool = False,
    cost_per_deck: float = 0,
    earned_per_card: float = 0,
    save_csv: Optional[str] = None,
    deck_csv: Optional[str] = None,
) -> dict:
    print_game = print_game or interactive
    total_cards = SimulatorCore().simulate(print_game, interactive, save_csv, deck_csv)

    results = {"total_cards": total_cards}
    gross = total_cards * earned_per_card
    net = gross - cost_per_deck

    if print_game:
        console.print(f"Cards in your first pile: {total_cards}")

    if cost_per_deck or earned_per_card:
        results["gross"] = gross
        results["net"] = net
        if print_game:
            net_color = "red" if net < 0 else "green"
            console.print(
                f"You earned ${gross: ,.2f} [blue]({total_cards} cards x "
                f"${earned_per_card: ,})[/blue] from the game"
            )
            console.print(f"A deck of cards cost: ${cost_per_deck: ,.2f}")
            console.print(
                f"Making your net total: [{net_color}]${net: ,.2f}[/{net_color}]"
            )

    return results


def run_multiple_simulations(
    simulations: int = 10,
    print_results: bool = False,
    cost_per_deck: float = 0,
    earned_per_card: float = 0,
    print_games: bool = False,
    use_dask: bool = False,
    dask_address: Optional[str] = None,
    dask_bag_partition_size: int = 10000,
    custom_dask_client: Optional[Client] = None,
) -> dict:
    if use_dask:
        if custom_dask_client is not None:
            client = custom_dask_client
            if dask_address:
                console.print(
                    f"[red]Since a custom dask client was provided, the dask address "
                    f"of[/red] {dask_address} [red]is being ignored[/red]"
                )
        else:
            client = Client(dask_address)
        console.print(client)

        if print_games:
            console.print("[red]Printing games is disabled when using dask.[/red]")
            console.print("[blue]Final results will still be printed[/blue]")

        def simulate(*_):
            return SimulatorCore().simulate()

        bag = dask_bag.from_sequence(
            range(simulations), partition_size=dask_bag_partition_size
        )
        results = bag.map(simulate).compute()

    else:
        simulator = SimulatorCore()
        results = [
            simulator.simulate(print_games)
            for _ in track(
                range(simulations), "Running Simulations", disable=print_games
            )
        ]

    total_cards = sum(results)
    average_cards = total_cards / simulations
    print_results = print_results or print_games
    final_results = {
        "results": results,
        "total_cards": total_cards,
        "average_cards": average_cards,
    }

    if print_results:
        console.rule("[b]RESULTS[/b]")
        console.print(f"You played {simulations: ,} games")
        console.print(f"Average cards in first stack: {average_cards}")

    if cost_per_deck or earned_per_card:
        gross_total = total_cards * earned_per_card
        net_total = gross_total - cost_per_deck * simulations

        gross_average = gross_total / simulations
        net_average = net_total / simulations

        final_results["gross_total"] = gross_total
        final_results["net_total"] = net_total
        final_results["gross_average"] = gross_average
        final_results["net_average"] = net_average

        if print_results:
            net_color = "red" if net_total < 0 else "green"
            console.print(f"Total gross earnings: [green]${gross_total: ,.2f}[/green]")
            console.print(
                f"Total net earnings: [{net_color}]${net_total: ,.2f}[/{net_color}]"
            )
            console.print(
                f"Average gross earnings: [green]${gross_average: ,.2f}[/green]"
            )
            console.print(
                f"Average net earnings: "
                f"[{net_color}]${net_average: ,.2f}[/{net_color}]"
            )

    return final_results
