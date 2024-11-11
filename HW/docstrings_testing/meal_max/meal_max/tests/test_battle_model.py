import pytest

from meal_max.models.battle_model import BattleModel
from meal_max.models.kitchen_model import Meal


@pytest.fixture()
def battle_model():
    """Fixture to provide a new instance of BattleModel for each test."""
    return BattleModel()

@pytest.fixture
def mock_update_meal_stats(mocker):
    """Mock the update_meal_stats function for testing purposes."""
    return mocker.patch("meal_max.models.battle_model.update_meal_stats")

"""Fixtures providing sample meals for the tests."""
@pytest.fixture
def meal_1():
    return Meal(1, 'Meal 1', 'Cuisine 1', 20.00, 'LOW')

@pytest.fixture
def meal_2():
    return Meal(2, 'Meal 2', 'Cuisine 2', 25.00, 'MED')

@pytest.fixture
def sample_meals(meal_1, meal_2):
    return [meal_1, meal_2]


##################################################
#
# Battle Management Test Cases
#
##################################################

def test_battle_meal1_wins(battle_model, meal_1, meal_2, mock_update_meal_stats, mocker):
    """Test a scenario where meal_1 successfully wins the battle."""
    battle_model.combatants = [meal_1, meal_2]
    
    # Mock scores to make sample_meal1 win
    mocker.patch.object(battle_model, 'get_battle_score', side_effect=[90, 85])
    mocker.patch("meal_max.models.battle_model.get_random", return_value=0.02)
    
    winner = battle_model.battle()
    assert winner == meal_1.meal, f"Expected winner to be {meal_1.meal}, but got {winner}"
    mock_update_meal_stats.assert_any_call(meal_1.id, 'win')
    mock_update_meal_stats.assert_any_call(meal_2.id, 'loss')
    assert len(battle_model.combatants) == 1
    assert battle_model.combatants[0] == meal_1

def test_battle_meal2_wins(battle_model, meal_1, meal_2, mock_update_meal_stats, mocker):
    """Test a scenario where sample_meal2 succesfully wins the battle."""
    battle_model.combatants = [meal_1, meal_2]
    
    # Mock scores to make sample_meal2 win
    mocker.patch.object(battle_model, 'get_battle_score', side_effect=[85, 90])
    mocker.patch("meal_max.models.battle_model.get_random", return_value=0.05)
    
    winner = battle_model.battle()
    assert winner == meal_2.meal, f"Expected winner to be {meal_2.meal}, but got {winner}"
    mock_update_meal_stats.assert_any_call(meal_2.id, 'win')
    mock_update_meal_stats.assert_any_call(meal_1.id, 'loss')
    assert len(battle_model.combatants) == 1
    assert battle_model.combatants[0] == meal_2

def test_battle_with_insufficient_combatants(battle_model, meal_1):
    """Test error when only one combatant tries to battle."""
    # Only one combatant in the list
    battle_model.combatants = [meal_1]
    
    with pytest.raises(ValueError, match="Two combatants must be prepped for a battle."):
        battle_model.battle()


##################################################
#
# Meal Retrieval Test Cases
#
##################################################

def test_get_battle_score(battle_model, meal_1):
    """Test successfully retrieving the battle score from the given meal combatant."""
    retrieved_score = battle_model.get_battle_score(meal_1)
    expected_score = (meal_1.price * len(meal_1.cuisine)) - 3
    assert retrieved_score == expected_score, f"Expected score of {expected_score}, got {retrieved_score}"


##################################################
#
# Combatant Management Functions
#
##################################################

def test_clear_singular_combatant(battle_model, meal_1):
    """Test clearing the combatants list of len 1."""
    battle_model.combatants = [meal_1]

    battle_model.clear_combatants()
    assert len(battle_model.combatants) == 0, "Combatants list should be empty after clearing"

def test_clear_multiple_combatants(battle_model, meal_1, meal_2):
    """Test clearing the entire combatants list of len > 1."""
    battle_model.combatants = [meal_1, meal_2]

    battle_model.clear_combatants()
    assert len(battle_model.combatants) == 0, "Combatants list should be empty after clearing"

def test_clear_empty_combatant(battle_model):
    """Test clearing the empty combatants list of len = 0."""
    battle_model.combatants = []

    battle_model.clear_combatants()
    assert len(battle_model.combatants) == 0, "Combatants list should be empty after clearing"

def test_get_all_combatants_multiple(battle_model, meal_1, meal_2):
    """Test successfully retrieving all combatants from the list."""
    battle_model.combatants = [meal_1, meal_2]

    all_combatants = battle_model.get_combatants()
    assert len(all_combatants) == 2
    assert all_combatants[0].id == 1
    assert all_combatants[1].id == 2

def test_get_all_combatants_singular(battle_model, meal_1):
    """Test successfully retrieving all combatants from the list of len 1."""
    battle_model.combatants = [meal_1]

    all_combatants = battle_model.get_combatants()
    assert len(all_combatants) == 1
    assert all_combatants[0].id == 1

def test_prep_two_combatants(battle_model, meal_1, meal_2):
    """Test successfully prepping all combatants from the list of len 2."""
    battle_model.prep_combatant(meal_1)
    battle_model.prep_combatant(meal_2)
    
    assert len(battle_model.combatants) == 2
    assert battle_model.combatants == [meal_1, meal_2]

def test_prep_one_combatant(battle_model, meal_1):
    """Test successfully prepping one combatant."""
    battle_model.prep_combatant(meal_1)
    
    assert len(battle_model.combatants) == 1
    assert battle_model.combatants == [meal_1]

def test_prep_three_combatants(battle_model, meal_1, meal_2):
    """Test error when trying to prep and add a third combatant."""
    battle_model.prep_combatant(meal_1)
    battle_model.prep_combatant(meal_2)
    
    assert len(battle_model.combatants) == 2, "There should be exactly two combatants prepped."
    assert battle_model.combatants == [meal_1, meal_2], "Combatants list does not match expected entries."
    
    with pytest.raises(ValueError, match="Combatant list is full, cannot add more combatants."):
        battle_model.prep_combatant(Meal(3, 'Meal 3', 'Cuisine 3', 15.00, 'HIGH'))

