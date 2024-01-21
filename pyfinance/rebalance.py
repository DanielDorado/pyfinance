from dataclasses import dataclass, field
from typing import Dict, List
import logging as log

# A data class to represent a Asset
@dataclass
class Asset:
    """ Class to represent a Asset."""
    name: str
    goal_percentage: int
    value: float
    rebalanced_value: float = 0.0
    sending_to: Dict['Asset', float] = field(default_factory=dict)
    reciving_from: Dict['Asset', float] = field(default_factory=dict)  # Double accounting

    def current_percentage(self, total_value) -> float:
        """ Return the current percentage of the asset."""
        return round(self.value * 100 / total_value, 2)
    
    def how_much_send(self) -> float:
        return self.value - self.rebalanced_value - sum(self.sending_to.values())
    
    def how_much_recive(self) -> float:
        return self.rebalanced_value - self.value - sum(self.reciving_from.values())
    
    def send_to(self, asset: 'Asset', value: float) -> None:
        """ Send value to asset."""
        if self.how_much_send() < value:
            raise ValueError(f"You can't send {value} to {asset.name}. You can send {self.how_much_send()}")
        self.sending_to[asset] = value
        asset.recive_from(self, value)

    def recive_from(self, asset: 'Asset', value: float) -> None:
        """ Recive value from asset."""
        if self.how_much_recive() < value:
            raise ValueError(f"You can't recive {value} from {asset.name}. You can recive {self.how_much_recive()}")
        self.reciving_from[asset] = value

    def __eq__(self, other):
        """ Check if two assets are equal."""
        return self.name == other.name
    
    def __hash__(self):
        """ Return the hash of the asset."""
        return hash(self.name)
    
    def __str__(self):
        return f"Asset {self.name}: Current Value {self.value}"


class RebalanceAssets(object):
    """ Class to rebalance assets."""
    
    def __init__(self, assets: List[Asset], threeshold: int) -> None:
        """ Initialize the class with a list of assets and a threeshold.
        
        Args:
            assets (List[Asset]): A list of assets.
            threeshold (int): The threeshold to rebalance the assets. If any asset is below the threeshold, all the assets will be rebalanced.
        """
        # Definitions:
        self.assets = assets
        self.threeshold = threeshold
        self.has_to_be_rebalanced = False

        self._percentages = []  # To store the current percentages of the assets
        # Invariants:
        # check if the sum of the assets is equal to 100
        percentage_sum = sum([asset.goal_percentage for asset in self.assets])
        if percentage_sum != 100:
            raise ValueError(f"The sum of the assets' percentage is {percentage_sum}, not equal to 100")
        # check if the threeshold is between 0 and 100
        if not 0 <= self.threeshold <= 100:
            raise ValueError(f"The threeshold is {self.threeshold}, not between 0 and 100")
        # check if the assets are unique
        if len(set([asset.name for asset in self.assets])) != len(self.assets):
            raise ValueError("The assets are not unique")
        
        # Calculations:
        self._update_has_to_be_rebalanced()
        if self.has_to_be_rebalanced:
            self._rebalance()
            self._calculate_sends_and_recives()
        else:
            log.info("The assets do not have to be rebalanced")

    def information(self) -> str:
        """ Return a string with the information of the rebalance."""
        if self.has_to_be_rebalanced:
            return self._information_rebalance()
        else:
            return f"The assets do not have to be rebalanced. The percentages are {self._percentages}"
        
    def _information_rebalance(self) -> str:
        """ Return a string with the information of the rebalance."""
        information = ""
        for asset in self.assets:
            information += f"**{asset.name}** ({asset.goal_percentage}%): {asset.value} --> {asset.rebalanced_value}\n"
            for asset_to_send, value in asset.sending_to.items():
                information += f"    - {value} ---> {asset_to_send.name}\n"
        return information

    def _rebalance(self):
        """ Rebalance the assets. And put in new_assets a copy of the asset rebalanced."""
        total_value = sum([asset.value for asset in self.assets])
        for asset in self.assets:
            asset.rebalanced_value = round(total_value * asset.goal_percentage / 100, 2)
    
    def _update_has_to_be_rebalanced(self):
        """ Check if the assets has to be rebalanced.
        
        All the assets has to be rebalanaced if in one or more assets the absolut difference between the goal percentage and the current percentage is greater than the threeshold.
        """
        total = sum([asset.value for asset in self.assets])
        for asset in self.assets:
            current_percentage = asset.current_percentage(total_value=total)
            self._percentages.append(current_percentage)
            if abs(asset.goal_percentage - current_percentage) > self.threeshold:
                self.has_to_be_rebalanced = True


    def _calculate_sends_and_recives(self):
        """ Calculate the sends and recives for each asset."""
        for asset in self.assets:
            if asset.how_much_send() > 0:
                for asset_to_send in self.assets:
                    if asset_to_send.how_much_recive() > 0 and asset_to_send != asset:
                        asset.send_to(asset_to_send, min(asset.how_much_send(), asset_to_send.how_much_recive()))
    
    def __str__(self):
        return f"RebalanceAssets with {len(self.assets)} assets and a threshold of {self.threeshold}"

def csv_to_assets(csv_file: str) -> List[Asset]:
    """ Return a list of assets from a csv file.
    
    Args:
        csv_file (str): The path of the csv file.
    
    Returns:
        List[Asset]: A list of assets.
    """
    assets = []
    with open(csv_file, "r") as f:
        for line in f:
            name, goal_percentage, value = line.strip().split(",")
            assets.append(Asset(name=name, goal_percentage=int(goal_percentage), value=float(value)))
    return assets    

if __name__ == "__main__":
    # Rebalance from a csv file passing the path of the csv file as an argument
    import sys
    threeshold = sys.argv[1]
    csv_file = sys.argv[2]
    assets = csv_to_assets(csv_file)
    rebalance_assets = RebalanceAssets(assets, threeshold=int(threeshold))
    print(rebalance_assets.information())
