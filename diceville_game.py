import random
from enum import Enum
from collections import deque, defaultdict

# Enums
class BuildingType(Enum):
    MAIN_BASE = -1
    RED = 0
    GREEN = 1
    BLUE = 2
    GREY = 3

class BuildingEmblem(Enum):
    NONE = 0
    FOOD = 1
    ENERGY = 2
    RUBY = 3
    SPHERE = 4

class SurfaceType(Enum):
    ANY = -1
    FIELD = 0
    FOREST = 1
    WATER = 2
    MOUNTAIN = 3

class Floor(Enum):
    FIRST_ENTRY_FLOOR = 0
    SCIENCE_FLOOR = 1
    INNOVATIONS_FLOOR = 2
    TRADE_FLOOR = 3
    COMMUNICATION_FLOOR = 4
    EXCITEMENT_FLOOR = 5
    STRATEGIC_FLOOR = 6

class Player(Enum):
    NULL = -1
    HOST = 0
    ENEMY1 = 1
    ENEMY2 = 2
    ENEMY3 = 3

# Tile
class Tile:
    def __init__(self, position, surface_type):
        self.position = position  # tuple (x, y)
        self.surface = surface_type
        self.building = None
        self.owner = Player.NULL

# Building
class Building:
    def __init__(self):
        self.id = 0
        self.name_tag = ""
        self.description_tag = ""
        self.type = BuildingType.RED
        self.min_dice_value = 0
        self.max_dice_value = 0
        self.requirement_tile_surface = SurfaceType.ANY
        self.emblem = BuildingEmblem.NONE
        self.price = 0
        self.owner = None
        self.tile = None

    def get_income_in_case_of_invoke(self, game):
        return 0

    def effect(self, game):
        pass

    def set_owner(self, player):
        self.owner = player

    def set_tile(self, tile):
        self.tile = tile

# EnableableBuilding
class EnableableBuilding(Building):
    def __init__(self):
        super().__init__()
        self.is_building_enabled = False

    def effect(self, game):
        self.is_building_enabled = True
        super().effect(game)

# IInvokableInNextMove
class IInvokableInNextMove:
    def invoke(self, game):
        pass

# IInvokableInDicesRoll
class IInvokableInDicesRoll:
    def invoke(self, game, sum_of_dices):
        pass

# IInvokableInNextBuildingsEffect
class IInvokableInNextBuildingsEffect:
    def init(self, game):
        pass

# MainBase
class MainBase(Building):
    def __init__(self):
        super().__init__()
        self.id = 0
        self.name_tag = "cards/mainBase"
        self.description_tag = "cards/mainBaseDescription"
        self.type = BuildingType.MAIN_BASE
        self.min_dice_value = 0
        self.max_dice_value = 0
        self.requirement_tile_surface = SurfaceType.ANY
        self.emblem = BuildingEmblem.NONE
        self.price = 0
        self.floors = [
            FirstEntryFloor(),
            ScienceFloor(),
            InnovationsFloor(),
            TradeFloor(),
            CommunicationFloor(),
            ExcitementFloor(),
            StrategicFloor()
        ]
        self.queue_of_floors_for_effect = []
        self.activate_floor(0)

    def activate_floor(self, floor_id):
        self.floors[floor_id].initialize()
        if self.get_count_of_activated_floors() == len(self.floors):
            print(f"Player {self.owner} wins!")
            self.game.is_game_over = True

    def floor_activate_effect(self, floor):
        self.queue_of_floors_for_effect.append(floor)

    def get_count_of_floors_in_queue_for_effect(self):
        return len(self.queue_of_floors_for_effect)

    def get_count_of_activated_floors(self):
        return sum(1 for f in self.floors if f.is_active)

    def get_income_in_case_of_invoke(self, game):
        if self.queue_of_floors_for_effect:
            return self.queue_of_floors_for_effect[0].get_income_in_case_of_invoke(game)
        return 0

    def effect(self, game):
        if self.queue_of_floors_for_effect:
            self.queue_of_floors_for_effect[0].effect(game)
            del self.queue_of_floors_for_effect[0]

# MainBaseFloor
class MainBaseFloor:
    def __init__(self):
        self.id = Floor.FIRST_ENTRY_FLOOR
        self.price = 0
        self.is_active = False

    def initialize(self):
        self.is_active = True

    def get_income_in_case_of_invoke(self, game):
        return 0

    def effect(self, game):
        pass

class FirstEntryFloor(MainBaseFloor, IInvokableInDicesRoll):
    def __init__(self):
        super().__init__()
        self.id = Floor.FIRST_ENTRY_FLOOR
        self.price = 0
        self.buildings_for_invoke_effect = []

    def invoke(self, game, sum_of_dices):
        self.buildings_for_invoke_effect = game.get_all_buildings_that_will_be_invoked_at_dice_value(game.game_moves_system.get_current_turn_player(), sum_of_dices)
        game.get_main_building_for_current_player().floor_activate_effect(self)

    def has_player_zero_all(self, game):
        player = game.game_moves_system.get_current_turn_player()
        player_income = len([b for b in self.buildings_for_invoke_effect if b.type != BuildingType.MAIN_BASE and b.get_income_in_case_of_invoke(game) > 0])
        if game.player_money[player] == 0 and (len(self.buildings_for_invoke_effect) == 0 or 
                                               len([b for b in self.buildings_for_invoke_effect if b.type != BuildingType.MAIN_BASE and b.owner == player]) == 0 or 
                                               player_income == 0):
            return True
        return False

    def get_income_in_case_of_invoke(self, game):
        return 2 if self.has_player_zero_all(game) else 0

    def effect(self, game):
        if self.has_player_zero_all(game):
            game.player_get_money(game.game_moves_system.get_current_turn_player(), 2, False)
        self.buildings_for_invoke_effect = []

class ScienceFloor(MainBaseFloor):
    def __init__(self):
        super().__init__()
        self.id = Floor.SCIENCE_FLOOR
        self.price = 4

class InnovationsFloor(MainBaseFloor):
    def __init__(self):
        super().__init__()
        self.id = Floor.INNOVATIONS_FLOOR
        self.price = 15

class TradeFloor(MainBaseFloor):
    def __init__(self):
        super().__init__()
        self.id = Floor.TRADE_FLOOR
        self.price = 2

class CommunicationFloor(MainBaseFloor, IInvokableInNextMove):
    def __init__(self):
        super().__init__()
        self.id = Floor.COMMUNICATION_FLOOR
        self.price = 10

    def get_income_in_case_of_invoke(self, game):
        if game.game_moves_system.get_current_turn_player() in game.get_most_rich_players():
            return 1
        return -1

    def invoke(self, game):
        game.get_main_building_for_current_player().floor_activate_effect(self)

    def effect(self, game):
        player = game.game_moves_system.get_current_turn_player()
        if player in game.get_most_rich_players():
            game.player_get_money(player, 1, False)
        elif player in game.get_most_poor_players():
            game.game_moves_system.give_player_step()

class ExcitementFloor(MainBaseFloor):
    def __init__(self):
        super().__init__()
        self.id = Floor.EXCITEMENT_FLOOR
        self.price = 22

class StrategicFloor(MainBaseFloor, IInvokableInNextMove):
    def __init__(self):
        super().__init__()
        self.id = Floor.STRATEGIC_FLOOR
        self.price = 30
        self.is_all_spheres_built = False

    def invoke(self, game):
        game.get_main_building_for_current_player().floor_activate_effect(self)

    def get_income_in_case_of_invoke(self, game):
        if self.check_if_all_spheres_built(game):
            return -1
        return 0

    def effect(self, game):
        if self.check_if_all_spheres_built(game):
            self.is_all_spheres_built = True
            game.game_moves_system.give_player_step()
        else:
            self.is_all_spheres_built = False

    def check_if_all_spheres_built(self, game):
        buildings = game.get_all_buildings_for_current_player()
        spheres = [b for b in buildings if b.emblem == BuildingEmblem.SPHERE]
        has_exploitation = any(isinstance(b, ExploitationSphere) for b in spheres)
        has_profit = any(isinstance(b, ProfitMakingSphere) for b in spheres)
        has_devastation = any(isinstance(b, DevastationSphere) for b in spheres)
        has_transformation = any(isinstance(b, TransformationSphere) for b in spheres)
        return has_exploitation and has_profit and has_devastation and has_transformation

# Buildings
class QueenBurger(Building):
    def __init__(self):
        super().__init__()
        self.id = 1
        self.name_tag = "cards/queenBurger"
        self.description_tag = "cards/queenBurgerDescription"
        self.type = BuildingType.GREEN
        self.min_dice_value = 1
        self.max_dice_value = 1
        self.requirement_tile_surface = SurfaceType.FIELD
        self.emblem = BuildingEmblem.FOOD
        self.price = 1

    def get_income_in_case_of_invoke(self, game):
        return 1

    def effect(self, game):
        game.player_get_money(self.owner, 1)

class TidalPowerPlant(Building):
    def __init__(self):
        super().__init__()
        self.id = 2
        self.name_tag = "cards/tidalPowerPlant"
        self.description_tag = "cards/tidalPowerPlantDescription"
        self.type = BuildingType.BLUE
        self.min_dice_value = 3
        self.max_dice_value = 3
        self.requirement_tile_surface = SurfaceType.WATER
        self.emblem = BuildingEmblem.ENERGY
        self.price = 2

    def get_income_in_case_of_invoke(self, game):
        return 2

    def effect(self, game):
        game.player_get_money(self.owner, 2)

class Orchard(Building):
    def __init__(self):
        super().__init__()
        self.id = 3
        self.name_tag = "cards/orchard"
        self.description_tag = "cards/orchardDescription"
        self.type = BuildingType.GREEN
        self.min_dice_value = 4
        self.max_dice_value = 4
        self.requirement_tile_surface = SurfaceType.FOREST
        self.emblem = BuildingEmblem.FOOD
        self.price = 2

    def get_income_in_case_of_invoke(self, game):
        return 2

    def effect(self, game):
        game.player_get_money(self.owner, 2)

class Trawler(Building):
    def __init__(self):
        super().__init__()
        self.id = 4
        self.name_tag = "cards/trawler"
        self.description_tag = "cards/trawlerDescription"
        self.type = BuildingType.BLUE
        self.min_dice_value = 5
        self.max_dice_value = 5
        self.requirement_tile_surface = SurfaceType.WATER
        self.emblem = BuildingEmblem.FOOD
        self.price = 3

    def get_income_in_case_of_invoke(self, game):
        return 3

    def effect(self, game):
        game.player_get_money(self.owner, 3)

class WindPowerPlant(Building):
    def __init__(self):
        super().__init__()
        self.id = 5
        self.name_tag = "cards/windPowerPlant"
        self.description_tag = "cards/windPowerPlantDescription"
        self.type = BuildingType.GREEN
        self.min_dice_value = 6
        self.max_dice_value = 6
        self.requirement_tile_surface = SurfaceType.FIELD
        self.emblem = BuildingEmblem.ENERGY
        self.price = 3

    def get_income_in_case_of_invoke(self, game):
        return 3

    def effect(self, game):
        game.player_get_money(self.owner, 3)

class EBankOffice(Building):
    def __init__(self):
        super().__init__()
        self.id = 6
        self.name_tag = "cards/eBankOffice"
        self.description_tag = "cards/eBankOfficeDescription"
        self.type = BuildingType.RED
        self.min_dice_value = 7
        self.max_dice_value = 7
        self.requirement_tile_surface = SurfaceType.FIELD
        self.emblem = BuildingEmblem.RUBY
        self.price = 4

    def get_income_in_case_of_invoke(self, game):
        return 1

    def effect(self, game):
        current_player = game.game_moves_system.get_current_turn_player()
        game.player_give_money(current_player, self.owner, 1)

class OilRig(Building):
    def __init__(self):
        super().__init__()
        self.id = 7
        self.name_tag = "cards/oilRig"
        self.description_tag = "cards/oilRigDescription"
        self.type = BuildingType.BLUE
        self.min_dice_value = 8
        self.max_dice_value = 8
        self.requirement_tile_surface = SurfaceType.WATER
        self.emblem = BuildingEmblem.ENERGY
        self.price = 4

    def get_income_in_case_of_invoke(self, game):
        return 4

    def effect(self, game):
        game.player_get_money(self.owner, 4)

class RiceField(Building):
    def __init__(self):
        super().__init__()
        self.id = 8
        self.name_tag = "cards/riceField"
        self.description_tag = "cards/riceFieldDescription"
        self.type = BuildingType.GREEN
        self.min_dice_value = 9
        self.max_dice_value = 9
        self.requirement_tile_surface = SurfaceType.FIELD
        self.emblem = BuildingEmblem.FOOD
        self.price = 5

    def get_income_in_case_of_invoke(self, game):
        return 3

    def effect(self, game):
        game.player_get_money(self.owner, 3)

class StoragePowerPlant(Building):
    def __init__(self):
        super().__init__()
        self.id = 9
        self.name_tag = "cards/storagePowerPlant"
        self.description_tag = "cards/storagePowerPlantDescription"
        self.type = BuildingType.BLUE
        self.min_dice_value = 10
        self.max_dice_value = 10
        self.requirement_tile_surface = SurfaceType.MOUNTAIN
        self.emblem = BuildingEmblem.ENERGY
        self.price = 5

    def get_income_in_case_of_invoke(self, game):
        return 5

    def effect(self, game):
        game.player_get_money(self.owner, 5)

class Sawmill(Building):
    def __init__(self):
        super().__init__()
        self.id = 10
        self.name_tag = "cards/sawmill"
        self.description_tag = "cards/sawmillDescription"
        self.type = BuildingType.GREEN
        self.min_dice_value = 11
        self.max_dice_value = 11
        self.requirement_tile_surface = SurfaceType.FOREST
        self.emblem = BuildingEmblem.RUBY
        self.price = 6

    def get_income_in_case_of_invoke(self, game):
        return len([t for t in game.get_all_map_tiles_for_player(self.owner) if t.surface == SurfaceType.FOREST])

    def effect(self, game):
        game.player_get_money(self.owner, self.get_income_in_case_of_invoke(game))

class WeaponsFactory(Building):
    def __init__(self):
        super().__init__()
        self.id = 11
        self.name_tag = "cards/weaponsFactory"
        self.description_tag = "cards/weaponsFactoryDescription"
        self.type = BuildingType.RED
        self.min_dice_value = 12
        self.max_dice_value = 12
        self.requirement_tile_surface = SurfaceType.MOUNTAIN
        self.emblem = BuildingEmblem.RUBY
        self.price = 6

    def get_income_in_case_of_invoke(self, game):
        return 3

    def effect(self, game):
        current_player = game.game_moves_system.get_current_turn_player()
        game.player_give_money(current_player, self.owner, 3)

class Jammer(EnableableBuilding):
    def __init__(self):
        super().__init__()
        self.id = 12
        self.name_tag = "cards/jammer"
        self.description_tag = "cards/jammerDescription"
        self.type = BuildingType.GREY
        self.min_dice_value = 1
        self.max_dice_value = 6
        self.requirement_tile_surface = SurfaceType.FIELD
        self.emblem = BuildingEmblem.NONE
        self.price = 2

    def get_income_in_case_of_invoke(self, game):
        return 0

    def effect(self, game):
        super().effect(game)
        # game.is_jammer_active = True  # Skip since no use

class MilitaryCamp(Building):
    def __init__(self):
        super().__init__()
        self.id = 13
        self.name_tag = "cards/militaryCamp"
        self.description_tag = "cards/militaryCampDescription"
        self.type = BuildingType.RED
        self.min_dice_value = 2
        self.max_dice_value = 3
        self.requirement_tile_surface = SurfaceType.FIELD
        self.emblem = BuildingEmblem.NONE
        self.price = 3

    def get_income_in_case_of_invoke(self, game):
        return 1

    def effect(self, game):
        current_player = game.game_moves_system.get_current_turn_player()
        game.player_give_money(current_player, self.owner, 1)

class CentralBank(Building):
    def __init__(self):
        super().__init__()
        self.id = 14
        self.name_tag = "cards/centralBank"
        self.description_tag = "cards/centralBankDescription"
        self.type = BuildingType.GREEN
        self.min_dice_value = 4
        self.max_dice_value = 5
        self.requirement_tile_surface = SurfaceType.FIELD
        self.emblem = BuildingEmblem.RUBY
        self.price = 4

    def get_income_in_case_of_invoke(self, game):
        return 2

    def effect(self, game):
        game.player_get_money(self.owner, 2)

class Mines(EnableableBuilding, IInvokableInNextBuildingsEffect):
    def __init__(self):
        super().__init__()
        self.id = 15
        self.name_tag = "cards/mines"
        self.description_tag = "cards/minesDescription"
        self.type = BuildingType.GREY
        self.min_dice_value = 6
        self.max_dice_value = 6
        self.requirement_tile_surface = SurfaceType.MOUNTAIN
        self.emblem = BuildingEmblem.RUBY
        self.price = 5

    def get_income_in_case_of_invoke(self, game):
        return 0

    def init(self, game):
        game.on_buildings_effect.append(self.mines_effect)

    def mines_effect(self, building, game):
        if self.is_building_enabled and building.type == BuildingType.RED:
            game.player_get_money(self.owner, 5)

class ControlCenter(EnableableBuilding, IInvokableInNextBuildingsEffect):
    def __init__(self):
        super().__init__()
        self.id = 16
        self.name_tag = "cards/controlCenter"
        self.description_tag = "cards/controlCenterDescription"
        self.type = BuildingType.GREY
        self.min_dice_value = 7
        self.max_dice_value = 8
        self.requirement_tile_surface = SurfaceType.FIELD
        self.emblem = BuildingEmblem.NONE
        self.price = 7

    def get_income_in_case_of_invoke(self, game):
        return 0

    def init(self, game):
        game.on_buildings_effect.append(self.control_center_effect)

    def control_center_effect(self, building, game):
        if self.is_building_enabled and building.type == BuildingType.GREEN:
            game.game_moves_system.give_player_step()

class Casino(Building):
    def __init__(self):
        super().__init__()
        self.id = 17
        self.name_tag = "cards/casino"
        self.description_tag = "cards/casinoDescription"
        self.type = BuildingType.RED
        self.min_dice_value = 9
        self.max_dice_value = 9
        self.requirement_tile_surface = SurfaceType.FIELD
        self.emblem = BuildingEmblem.NONE
        self.price = 8
        self.multiplier = 1

    def get_income_in_case_of_invoke(self, game):
        return 3 * self.multiplier

    def effect(self, game):
        current_player = game.game_moves_system.get_current_turn_player()
        game.player_give_money(current_player, self.owner, 3 * self.multiplier)
        if game.is_thrown_two_dice:
            self.multiplier += 1

class ExploitationSphere(Building):
    def __init__(self):
        super().__init__()
        self.id = 18
        self.name_tag = "cards/exploitationSphere"
        self.description_tag = "cards/exploitationSphereDescription"
        self.type = BuildingType.BLUE
        self.min_dice_value = 5
        self.max_dice_value = 5
        self.requirement_tile_surface = SurfaceType.FIELD
        self.emblem = BuildingEmblem.SPHERE
        self.price = 4

    def get_income_in_case_of_invoke(self, game):
        income = 0
        if game.is_thrown_two_dice:
            energy_buildings = [b for b in game.get_all_buildings_for_player(self.owner) if b.emblem == BuildingEmblem.ENERGY]
            for energy_building in energy_buildings:
                income += energy_building.get_income_in_case_of_invoke(game)
        else:
            income = 1
        return income

    def effect(self, game):
        if game.is_thrown_two_dice:
            energy_buildings = [b for b in game.get_all_buildings_for_player(self.owner) if b.emblem == BuildingEmblem.ENERGY]
            for energy_building in energy_buildings:
                game.player_get_money(self.owner, energy_building.get_income_in_case_of_invoke(game))
        else:
            game.player_get_money(self.owner, 1)

class ProfitMakingSphere(Building):
    def __init__(self):
        super().__init__()
        self.id = 19
        self.name_tag = "cards/profitMakingSphere"
        self.description_tag = "cards/profitMakingSphereDescription"
        self.type = BuildingType.BLUE
        self.min_dice_value = 2
        self.max_dice_value = 2
        self.requirement_tile_surface = SurfaceType.FIELD
        self.emblem = BuildingEmblem.SPHERE
        self.price = 6

    def get_income_in_case_of_invoke(self, game):
        income = 0
        if game.is_thrown_two_dice:
            food_buildings = [b for b in game.get_all_buildings_for_player(self.owner) if b.emblem == BuildingEmblem.FOOD]
            for food_building in food_buildings:
                income += food_building.get_income_in_case_of_invoke(game)
        else:
            income = 1
        return income

    def effect(self, game):
        if game.is_thrown_two_dice:
            food_buildings = [b for b in game.get_all_buildings_for_player(self.owner) if b.emblem == BuildingEmblem.FOOD]
            for food_building in food_buildings:
                game.player_get_money(self.owner, food_building.get_income_in_case_of_invoke(game))
        else:
            game.player_get_money(self.owner, 1)

class DevastationSphere(Building):
    def __init__(self):
        super().__init__()
        self.id = 20
        self.name_tag = "cards/devastationSphere"
        self.description_tag = "cards/devastationSphereDescription"
        self.type = BuildingType.RED
        self.min_dice_value = 10
        self.max_dice_value = 10
        self.requirement_tile_surface = SurfaceType.WATER
        self.emblem = BuildingEmblem.SPHERE
        self.price = 5

    def get_income_in_case_of_invoke(self, game):
        return len(game.get_all_available_for_build_map_tiles_for_player(game.game_moves_system.get_current_turn_player()))

    def effect(self, game):
        current_player = game.game_moves_system.get_current_turn_player()
        amount = len(game.get_all_available_for_build_map_tiles_for_player(current_player))
        game.player_give_money(current_player, self.owner, amount)

class TransformationSphere(EnableableBuilding, IInvokableInNextMove):
    def __init__(self):
        super().__init__()
        self.id = 21
        self.name_tag = "cards/transformationSphere"
        self.description_tag = "cards/transformationSphereDescription"
        self.type = BuildingType.GREY
        self.min_dice_value = 12
        self.max_dice_value = 14
        self.requirement_tile_surface = SurfaceType.MOUNTAIN
        self.emblem = BuildingEmblem.SPHERE
        self.price = 6
        self.unused_step_count = 0
        self.is_owner_turn_passed = False
        self._game = None

    def get_income_in_case_of_invoke(self, game):
        return 0

    def effect(self, game):
        super().effect(game)
        self._game = game
        game.on_next_turn.append(self.get_current_player_step_count)

    def get_current_player_step_count(self, game):
        if not self.is_building_enabled:
            return
        if not self.is_owner_turn_passed:
            self.is_owner_turn_passed = True
            return
        self.unused_step_count += game.game_moves_system.previous_player_step_count
        unused = game.game_moves_system.max_player_step_count - game.game_moves_system.previous_player_step_count
        game.player_get_money(self.owner, unused * 2)

    def invoke(self, game):
        if game.game_moves_system.get_current_turn_player() == self.owner:
            game.game_moves_system.give_player_step(self.unused_step_count)
            self.unused_step_count = 0
            self.is_owner_turn_passed = False
            if self.get_current_player_step_count in game.on_next_turn:
                game.on_next_turn.remove(self.get_current_player_step_count)

class Bathyscaphe(Building):
    def __init__(self):
        super().__init__()
        self.id = 22
        self.name_tag = "cards/bathyscaphe"
        self.description_tag = "cards/bathyscapheDescription"
        self.type = BuildingType.BLUE
        self.min_dice_value = 4
        self.max_dice_value = 4
        self.requirement_tile_surface = SurfaceType.WATER
        self.emblem = BuildingEmblem.NONE
        self.price = 3

    def get_income_in_case_of_invoke(self, game):
        return len([t for t in game.get_all_map_tiles_for_player(self.owner) if t.surface == SurfaceType.WATER])

    def effect(self, game):
        game.player_get_money(self.owner, self.get_income_in_case_of_invoke(game))

# BuildingsObjectStorage
class BuildingsObjectStorage:
    def __init__(self):
        self.buildings_count = 22

    def get_buildings_count(self):
        return self.buildings_count

    def get_building(self, id):
        if id == 0: return MainBase()
        if id == 1: return QueenBurger()
        if id == 2: return TidalPowerPlant()
        if id == 3: return Orchard()
        if id == 4: return Trawler()
        if id == 5: return WindPowerPlant()
        if id == 6: return EBankOffice()
        if id == 7: return OilRig()
        if id == 8: return RiceField()
        if id == 9: return StoragePowerPlant()
        if id == 10: return Sawmill()
        if id == 11: return WeaponsFactory()
        if id == 12: return Jammer()
        if id == 13: return MilitaryCamp()
        if id == 14: return CentralBank()
        if id == 15: return Mines()
        if id == 16: return ControlCenter()
        if id == 17: return Casino()
        if id == 18: return ExploitationSphere()
        if id == 19: return ProfitMakingSphere()
        if id == 20: return DevastationSphere()
        if id == 21: return TransformationSphere()
        if id == 22: return Bathyscaphe()
        return MainBase()

# PlayerHand
class PlayerHand:
    def __init__(self, game):
        self.hand = [None] * 6
        self.game = game
        self.buildings_object_storage = game.buildings_object_storage
        self.ability_to_replace_card_count = 1
        self.last_wasted_building = None
        self.last_wasted_building_id = 0

    def add_buildings_to_full_hand(self):
        for i in range(len(self.hand)):
            if self.hand[i] is None:
                self.add_building(i)

    def add_building(self, card_id):
        building = None
        while True:
            building = self.buildings_object_storage.get_building(random.randint(1, self.buildings_object_storage.get_buildings_count()))
            if building.id not in [b.id for b in self.hand if b is not None]:
                break
        self.hand[card_id] = building
        return building

    def use_building(self, card_id):
        building = self.hand[card_id]
        if building:
            self.last_wasted_building = building
            self.last_wasted_building_id = card_id
            self.hand[card_id] = None
            return building
        return None

    def return_last_wasted_building(self):
        if self.last_wasted_building:
            self.hand[self.last_wasted_building_id] = self.last_wasted_building
            self.last_wasted_building = None
            self.last_wasted_building_id = 0
            self.game.game_moves_system.give_player_step()

    def replace_card(self, card_id):
        if self.ability_to_replace_card_count > 0:
            current_id = self.hand[card_id].id if self.hand[card_id] else 0
            self.hand[card_id] = None
            self.add_building(card_id)
            while self.hand[card_id].id == current_id:
                self.add_building(card_id)
            self.ability_to_replace_card_count -= 1

# BuilderOnTile
class BuilderOnTile:
    def __init__(self, game):
        self.game = game

    def set_main_base_for_build_on_tile(self, building, tile, player, position):
        tile.owner = player
        tile.surface = SurfaceType.FIELD
        self.build(tile, building, player)
        self.game.player_buildings.append({'player': player, 'building': building})
        self.game.player_main_base_position[player] = position

    def set_building_for_build_on_tile(self, building, tile, player):
        if tile.building is not None:
            return False
        if tile.surface != building.requirement_tile_surface and building.requirement_tile_surface != SurfaceType.ANY:
            return False
        tile.building = building
        building.set_tile(tile)
        self.game.player_build_building(player, building)
        return True

    def build(self, tile, building, player):
        building.set_owner(player)

# GameMap
class GameMap:
    def __init__(self, size=(10, 10)):
        self.size = size
        self.map = [[Tile((x, y), random.choice([s for s in SurfaceType if s != SurfaceType.ANY])) for y in range(size[1])] for x in range(size[0])]

# GameMovesSystem
class GameMovesSystem:
    def __init__(self, game):
        self.game = game
        self.current_player_step_count = 0
        self.previous_player_step_count = 0
        self.players_turn_order = deque()
        self.first_player = None
        self.max_player_step_count = 2

    def initialize(self):
        self.add_players_in_queue()
        self.first_player = self.players_turn_order[0]
        self.make_turn()

    def add_players_in_queue(self):
        for p in self.game.players:
            self.players_turn_order.append(p)

    def make_turn(self):
        if self.players_turn_order:
            self.players_turn_order.rotate(-1)
        else:
            self.add_players_in_queue()
            self.first_player = self.players_turn_order[0]

        self.reset_variables()
        self.give_cards()
        self.invoke_game_objects_in_next_move()
        for callback in self.game.on_next_turn:
            callback(self.game)

    def reset_variables(self):
        self.previous_player_step_count = self.current_player_step_count
        self.current_player_step_count = self.max_player_step_count

    def give_cards(self):
        hand = self.game.player_hand_of_cards[self.get_current_turn_player()]
        hand.add_buildings_to_full_hand()

    def invoke_game_objects_in_next_move(self):
        for pb in self.game.player_buildings:
            building = pb['building']
            if isinstance(building, IInvokableInNextMove):
                building.invoke(self.game)
            if isinstance(building, IInvokableInNextBuildingsEffect):
                building.init(self.game)
        main_base = self.game.get_main_building_for_current_player()
        for floor in main_base.floors:
            if floor.is_active:
                if isinstance(floor, IInvokableInNextMove):
                    floor.invoke(self.game)
                if isinstance(floor, IInvokableInNextBuildingsEffect):
                    floor.init(self.game)

    def get_current_turn_player(self):
        return self.players_turn_order[0] if self.players_turn_order else Player.NULL

    def can_make_move(self):
        return self.game.has_current_player_threw_dice and self.current_player_step_count > 0

    def make_move(self):
        if self.can_make_move():
            self.current_player_step_count -= 1

    def give_player_step(self, count=1):
        self.current_player_step_count += count

# Game
class Game:
    def __init__(self, num_players=2, map_size=(10,10)):
        self.player_main_base_position = {}
        self.player_money = {list(Player)[i]: 10 for i in range(1, num_players+1)}
        self.player_buildings = []
        self.player_grey_buildings = []
        self.player_tiles = []
        self.game_map = GameMap(map_size)
        self.game_moves_system = GameMovesSystem(self)
        self.buildings_object_storage = BuildingsObjectStorage()
        self.player_hand_of_cards = {list(Player)[i]: PlayerHand(self) for i in range(1, num_players+1)}
        self.players = list(Player)[1:num_players+1]
        self.sum_of_thrown_dice = 0
        self.thrown_dice_values = []
        self.is_thrown_two_dice = False
        self.has_current_player_threw_dice = False
        self.is_game_over = False
        self.on_next_turn = []
        self.on_buildings_effect = []
        self.init_game()

    def init_game(self):
        self.init_map()
        self.game_moves_system.initialize()

    def is_player_in_the_game(self, player):
        return player in self.players

    def init_map(self):
        positions = [(0,0, Player.HOST), (0, self.game_map.size[1]-3, Player.ENEMY1), (self.game_map.size[0]-3, 0, Player.ENEMY2), (self.game_map.size[0]-3, self.game_map.size[1]-3, Player.ENEMY3)]
        for px, py, player in positions:
            if self.is_player_in_the_game(player):
                for dx in range(3):
                    for dy in range(3):
                        tile_pos = (px + dx, py + dy)
                        tile = self.game_map.map[tile_pos[0]][tile_pos[1]]
                        tile.owner = player
                        self.player_tiles.append({'player': player, 'tile': tile})
                center_pos = (px + 1, py + 1)
                center_tile = self.game_map.map[center_pos[0]][center_pos[1]]
                main_base = MainBase()
                main_base.game = self
                self.builder_on_tile = BuilderOnTile(self)
                self.builder_on_tile.set_main_base_for_build_on_tile(main_base, center_tile, player, center_pos)

    def player_throw_dice(self, two_dice=False):
        if two_dice:
            d1 = random.randint(1,6)
            d2 = random.randint(1,6)
            sum_d = d1 + d2
            self.thrown_dice_values = [d1, d2]
            self.is_thrown_two_dice = True
        else:
            sum_d = random.randint(1,6)
            self.thrown_dice_values = [sum_d]
            self.is_thrown_two_dice = False
        self.sum_of_thrown_dice = sum_d
        self.has_current_player_threw_dice = True
        self.invoke_dices_roll_invocables(sum_d)
        self.invoke_all_buildings(self.game_moves_system.get_current_turn_player(), sum_d)

    def invoke_dices_roll_invocables(self, sum_d):
        main_base = self.get_main_building_for_current_player()
        for floor in main_base.floors:
            if floor.is_active and isinstance(floor, IInvokableInDicesRoll):
                floor.invoke(self, sum_d)
        for pb in self.player_buildings:
            building = pb['building']
            if isinstance(building, IInvokableInDicesRoll):
                building.invoke(self, sum_d)

    def invoke_all_buildings(self, player, dice_value):
        # Red
        for pb in self.player_buildings:
            b = pb['building']
            if b.owner is not None and b.type == BuildingType.RED and b.min_dice_value <= dice_value <= b.max_dice_value and pb['player'] != player:
                for callback in self.on_buildings_effect:
                    callback(b, self)
                b.effect(self)
        # Green
        for pb in self.player_buildings:
            b = pb['building']
            if b.owner is not None and b.type == BuildingType.GREEN and b.min_dice_value <= dice_value <= b.max_dice_value and pb['player'] == player:
                for callback in self.on_buildings_effect:
                    callback(b, self)
                b.effect(self)
        # Blue
        for pb in self.player_buildings:
            b = pb['building']
            if b.owner is not None and b.type == BuildingType.BLUE and b.min_dice_value <= dice_value <= b.max_dice_value:
                b.effect(self)
        # Grey
        for pb in self.player_buildings:
            b = pb['building']
            if b.owner is not None and b.type == BuildingType.GREY and b.min_dice_value <= dice_value <= b.max_dice_value and pb['player'] == player:
                b.effect(self)
        # Main base
        main_base = self.get_main_building_for_player(player)
        main_base.effect(self)

    def get_all_buildings(self):
        return [pb['building'] for pb in self.player_buildings]

    def get_all_buildings_for_player(self, player):
        return [pb['building'] for pb in self.player_buildings if pb['player'] == player]

    def get_all_buildings_for_current_player(self):
        return self.get_all_buildings_for_player(self.game_moves_system.get_current_turn_player())

    def get_all_buildings_except_player(self, player):
        return [pb['building'] for pb in self.player_buildings if pb['player'] != player]

    def get_main_building_for_player(self, player):
        for pb in self.player_buildings:
            if pb['player'] == player and isinstance(pb['building'], MainBase):
                return pb['building']
        return None

    def get_main_building_for_current_player(self):
        return self.get_main_building_for_player(self.game_moves_system.get_current_turn_player())

    def get_all_map_tiles_for_player(self, player):
        return [pt['tile'] for pt in self.player_tiles if pt['player'] == player]

    def get_all_available_for_build_map_tiles_for_player(self, player):
        return [pt['tile'] for pt in self.player_tiles if pt['player'] == player and pt['tile'].building is None]

    def get_all_buildings_that_will_be_invoked_at_dice_value(self, player, dice_value):
        buildings = []
        buildings.extend(self.get_all_buildings_for_player_that_will_be_invoked_at_dice_value(player, dice_value))
        buildings.extend(self.get_all_buildings_except_player_that_will_be_invoked_at_dice_value(player, dice_value))
        return buildings

    def get_all_buildings_for_player_that_will_be_invoked_at_dice_value(self, player, dice_value):
        return [b for b in self.get_all_buildings_for_player(player) if b.type != BuildingType.RED and b.min_dice_value <= dice_value <= b.max_dice_value]

    def get_all_buildings_except_player_that_will_be_invoked_at_dice_value(self, player, dice_value):
        return [b for b in self.get_all_buildings_except_player(player) if b.type != BuildingType.GREEN and b.min_dice_value <= dice_value <= b.max_dice_value]

    def player_get_money(self, player, amount, is_from_building_income=True):
        self.player_money[player] += amount
        if self.player_money[player] < 0:
            self.player_money[player] = 0

    def player_give_money(self, from_player, to_player, amount):
        self.player_money[from_player] -= amount
        self.player_money[to_player] += amount
        if self.player_money[from_player] < 0:
            self.player_money[from_player] = 0

    def can_player_purchase_building(self, player, building):
        return self.player_money[player] >= building.price

    def player_build_building(self, player, building):
        building.set_owner(player)
        self.player_buildings.append({'player': player, 'building': building})
        self.player_money[player] -= building.price

    def player_build_main_base(self, player, position):
        self.player_main_base_position[player] = position
        main_base = self.get_main_building_for_player(player)
        self.player_buildings.append({'player': player, 'building': main_base})

    def player_owns_new_tile(self, player, tile):
        self.player_tiles.append({'player': player, 'tile': tile})

    def buy_tile(self, player, position):
        if self.player_money[player] < self.get_buy_tile_cost(player):
            return False
        tile = self.game_map.map[position[0]][position[1]]
        if tile.owner != Player.NULL or tile.building is not None:
            return False
        adjacent = False
        for pt in self.player_tiles:
            if pt['player'] == player:
                p = pt['tile'].position
                if abs(p[0] - position[0]) + abs(p[1] - position[1]) == 1:
                    adjacent = True
                    break
        if not adjacent:
            return False
        tile.owner = player
        self.player_owns_new_tile(player, tile)
        self.player_money[player] -= self.get_buy_tile_cost(player)
        return True

    def get_buy_tile_cost(self, player):
        main_base = self.get_main_building_for_player(player)
        return main_base.get_count_of_activated_floors()

    def buy_floor(self, player, floor_id):
        main_base = self.get_main_building_for_player(player)
        floor = main_base.floors[floor_id]
        if floor.is_active:
            return False
        if self.player_money[player] < floor.price:
            return False
        self.player_money[player] -= floor.price
        main_base.activate_floor(floor_id)
        return True

    def get_most_rich_players(self):
        counts = {p: self.get_main_building_for_player(p).get_count_of_activated_floors() if self.is_player_in_the_game(p) else -10 for p in self.players}
        max_count = max(counts.values())
        return [p for p, c in counts.items() if c == max_count]

    def get_most_poor_players(self):
        counts = {p: self.get_main_building_for_player(p).get_count_of_activated_floors() if self.is_player_in_the_game(p) else 10 for p in self.players}
        min_count = min(counts.values())
        return [p for p, c in counts.items() if c == min_count]

    def does_player_have_available_tile_for_build(self, player):
        return len(self.get_all_available_for_build_map_tiles_for_player(player)) > 0

if __name__ == "__main__":
    game = Game(num_players=2)
    while not game.is_game_over:
        player = game.game_moves_system.get_current_turn_player()
        game.player_throw_dice()
        hand = game.player_hand_of_cards[player]
        building = hand.use_building(0)
        if building:
            tiles = game.get_all_available_for_build_map_tiles_for_player(player)
            if tiles:
                tile = tiles[0]
                game.builder_on_tile.set_building_for_build_on_tile(building, tile, player)
        game.buy_tile(player, (3,3))
        game.buy_floor(player, 1)
        game.game_moves_system.make_turn()